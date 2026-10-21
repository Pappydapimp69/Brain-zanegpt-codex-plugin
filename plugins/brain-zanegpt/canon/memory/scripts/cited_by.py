#!/usr/bin/env python3
"""Write back citations to the entries they cite.

When a lesson names an older entry in its `Composed:` field, the older entry
has surfaced: it was built on, and the citing lesson's sandbox and result are
evidence about it. The citing side already records the edge; the cited entry
recorded nothing. This appends one dated line to each cited entry, in the
style of the steward's `- Audited:` / `- Reverified:` lines:

  - Cited-by: <date> · projects/<file>#E<n> · compatible|incompatible
    · sandboxes/<file> | no sandbox · observed <...> · <link>

Idempotent: an entry already carrying a line for that citing entry is left
alone, so the steward can run this after every promotion and a catch-up run
over existing canon is safe to repeat. The label is `Cited-by`, not
`Composed-in`: the CLI matches field labels by prefix, so anything starting
with `Composed` would read as the entry's own `Composed:` field and invent a
reverse edge.

Run: python3 scripts/cited_by.py [--dry-run]
Pure standard library.
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = os.path.join(ROOT, "projects")
SANDBOX_DIR = "sandboxes"
DRY = "--dry-run" in sys.argv
LABEL = "Cited-by"
OBSERVED_MAX = 240

REF_RE = re.compile(r"([a-z0-9][a-z0-9_.-]*?)(?:\.md)?[/#](E\d+)", re.I)
ENTRY_RE = re.compile(r"^## (E\d+)\b.*$", re.M)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, text):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def field(block: str, label: str) -> str:
    """Value of `- Label: ...`, joined across indented continuation lines.
    Exact label match (case-insensitive, parenthetical suffix ignored)."""
    out, capturing = [], False
    for ln in block.splitlines():
        s = ln.strip()
        m = re.match(r"^-\s*([^:(]+?)\s*(?:\(.*?\))?\s*:\s*(.*)$", s)
        if m:
            capturing = m.group(1).strip().lower() == label.lower()
            if capturing and m.group(2):
                out.append(m.group(2))
            continue
        if capturing and ln.startswith("  ") and s:
            out.append(s)
        elif capturing:
            capturing = False
    return " ".join(out).strip()


def one_line(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def slug_index(files):
    """Every reasonable spelling of a project file stem -> filename (mirrors
    the CLI's resolver: full stem, after `owner__`, and without `sandbox-`)."""
    idx = {}
    for fn in sorted(files):
        stem = fn[:-3]
        keys = {stem}
        if "__" in stem:
            keys.add(stem.split("__", 1)[1])
        for k in list(keys):
            if k.startswith("sandbox-"):
                keys.add(k[len("sandbox-"):])
        for k in keys:
            idx.setdefault(k.lower(), fn)
    return idx


def resolve(slug: str, idx: dict):
    slug = slug.strip().lower()
    if slug in idx:
        return idx[slug]
    cands = {f for k, f in idx.items()
             if k.endswith("-" + slug) or slug.endswith("-" + k)}
    return next(iter(cands)) if len(cands) == 1 else None


def entries(ptext: str):
    """[(eid, start, end)] for every entry block in a project file."""
    heads = list(ENTRY_RE.finditer(ptext))
    out = []
    for i, m in enumerate(heads):
        rest = ptext[m.end():]
        stop = re.search(r"^## E\d+\b|^---\s*$", rest, re.M)
        if i + 1 < len(heads):
            end = heads[i + 1].start()
        else:
            end = m.end() + stop.start() if stop else len(ptext)
        out.append((m.group(1), m.start(), end))
    return out


def sandbox_ref(citing_block: str) -> str:
    v = field(citing_block, "sandbox").strip().strip("`")
    if not v:
        return "no sandbox"
    base = os.path.basename(v.split()[0])
    if os.path.isfile(os.path.join(ROOT, SANDBOX_DIR, base)):
        return f"{SANDBOX_DIR}/{base}"
    return one_line(v)


def main() -> int:
    files = [f for f in os.listdir(PROJECTS) if f.endswith(".md")]
    idx = slug_index(files)
    texts = {f: read(os.path.join(PROJECTS, f)) for f in files}
    blocks = {}        # (file, eid) -> block text
    for f, t in texts.items():
        for eid, s, e in entries(t):
            blocks[(f, eid)] = t[s:e]

    # citing entry -> the entries it composes (memory refs only; `ideas:`
    # kernels live in the ideas repo, which is append-only)
    lines = {}         # (target file, eid) -> [line]
    unresolved = 0
    for (f, eid), block in sorted(blocks.items()):
        comp = field(block, "composed")
        if not comp or re.fullmatch(r"(n/?a|none|—|-)\.?", comp.strip(), re.I):
            continue
        comp = re.sub(r"ideas:\S+", " ", comp)
        pol = field(block, "polarity").strip().lower() or "compatible"
        obs = one_line(field(block, "observed"))
        if len(obs) > OBSERVED_MAX:
            obs = obs[:OBSERVED_MAX - 1].rstrip() + "…"
        parts = [field(block, "date").strip() or "undated",
                 f"projects/{f}#{eid}", pol, sandbox_ref(block)]
        if obs:
            parts.append("observed " + obs)
        link = one_line(field(block, "link"))
        if link:
            parts.append(link)
        line = f"- {LABEL}: " + " · ".join(parts)
        for slug, teid in REF_RE.findall(comp):
            tf = resolve(slug, idx)
            if not tf:
                unresolved += 1
                continue
            if (tf, teid) not in blocks or (tf, teid) == (f, eid):
                continue
            lines.setdefault((tf, teid), []).append((f, eid, line))

    added, skipped, touched = 0, 0, set()
    for tf in sorted({k[0] for k in lines}):
        ptext = texts[tf]
        # append from the bottom up so earlier spans stay valid
        for teid, s, e in sorted(entries(ptext), key=lambda x: -x[1]):
            new = []
            body = ptext[s:e]
            for cf, ceid, line in lines.get((tf, teid), []):
                marker = f"projects/{cf}#{ceid}"
                if re.search(rf"^-\s*{LABEL}:.*{re.escape(marker)}\b", body, re.M):
                    skipped += 1
                    continue
                new.append(line)
            if not new:
                continue
            body = body.rstrip("\n") + "\n" + "\n".join(new) + "\n"
            tail = ptext[e:]
            if tail and not tail.startswith("\n"):
                body += "\n"
            ptext = ptext[:s] + body + tail
            added += len(new)
            touched.add(tf)
        texts[tf] = ptext
    if not DRY:
        for tf in touched:
            write(os.path.join(PROJECTS, tf), texts[tf])
    print(f"{'DRY RUN: ' if DRY else ''}{LABEL}: {added} line(s) added to "
          f"{len({k for k in lines if any(True for _ in lines[k])})} cited entries "
          f"in {len(touched)} files · {skipped} already present · "
          f"{unresolved} unresolved ref(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
