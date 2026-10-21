#!/usr/bin/env python3
"""Structural validator for the `memory` knowledge base.

Enforces the invariants that keep canon trustworthy:
  * canon (projects/*.md + PITFALLS.md) stays consistent — IDs unique, index
    anchors resolve, project filenames conform;
  * canon is append-only — no existing entry is removed versus the base commit;
  * incoming/ proposals are schema-complete before a steward promotes them
    (a `## REVIEW` drop is checked against REVIEW-TEMPLATE.md's fields instead);
  * incoming/ sandbox files (*.py, never executed here) carry no injection
    text; orphaned or misnamed ones only warn;
  * no secrets land anywhere in the repo.

Run locally (`python3 scripts/validate.py`) or in CI. Exits nonzero with a
report if anything fails. Pure standard library, no dependencies.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    """Reported, never fails the run (train-verification phase 1 is warn-first)."""
    warnings.append(msg)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def git(*args: str):
    try:
        out = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        )
        return out.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# A held proposal carries a `<!-- STEWARD HOLD ... -->` block the steward
# appended when it quarantined the file for a human. It is already triaged and
# stays in incoming/ by design until someone fixes or drops it — so the schema
# gate must NOT keep failing on it. One held, un-promotable proposal that still
# tripped this check would exit the steward run nonzero, skip its commit step,
# and permanently block committing everyone else's promotions (the observed
# deadlock). Reuse steward.py's OWN marker regex (single source, no drift) —
# the same skip check_incoming_content() already applies. Cached; falls back to
# "not held" if steward.py can't load (fail-open is safe here: worst case is the
# pre-fix behaviour, and a genuinely missing steward.py surfaces via the job).
_steward_mod = None
_steward_loaded = False


def held(text: str) -> bool:
    global _steward_mod, _steward_loaded
    if not _steward_loaded:
        _steward_loaded = True
        import importlib.util
        try:
            spec = importlib.util.spec_from_file_location(
                "steward_checks", os.path.join(ROOT, "scripts", "steward.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _steward_mod = mod
        except Exception:
            _steward_mod = None
    return bool(_steward_mod and _steward_mod.HOLD_MARKER_RE.search(text))


HEADING_RE = re.compile(r"^## (E\d+)\b", re.M)
PROJECT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*__[a-z0-9][a-z0-9._-]*\.md$")
TAG_TOKEN_RE = re.compile(r"\[[^\]]*\]")
GOOD_TAG_RE = re.compile(r"^\[[a-z0-9][a-z0-9._-]*\]$")
ANCHOR_RE = re.compile(r"→\s*(projects/[^\s#]+\.md)#(E\d+)")


def ids_in(text: str):
    return HEADING_RE.findall(text)


def project_files():
    d = os.path.join(ROOT, "projects")
    if not os.path.isdir(d):
        return []
    return sorted(
        os.path.join("projects", f) for f in os.listdir(d) if f.endswith(".md")
    )


def check_projects() -> None:
    for rel in project_files():
        name = os.path.basename(rel)
        if not PROJECT_NAME_RE.match(name):
            fail(f"{rel}: filename must match <owner>__<repo>.md (lowercase).")
        seen = set()
        for i in ids_in(read(os.path.join(ROOT, rel))):
            if i in seen:
                fail(f"{rel}: duplicate entry id {i}.")
            seen.add(i)


# An index ENTRY starts with a bullet whose first token is the bracketed tag
# block (`- `[tag][tag]` prose … → anchor`); its prose/anchor may then wrap to
# indented continuation lines. Legend lines ("- domains: `[x]`") put text
# before the bracket, so they don't match — only real entries do.
ENTRY_START_RE = re.compile(r"^\s*-\s*`?\s*(\[[^\]]*\](?:\s*\[[^\]]*\])*)")


def check_pitfalls() -> None:
    p = os.path.join(ROOT, "PITFALLS.md")
    if not os.path.exists(p):
        fail("PITFALLS.md is missing (the index must exist).")
        return
    text = read(p)
    # Tag-format on canon. The index is the documented retrieval surface
    # (`grep '[browser]' PITFALLS.md`), so a malformed/uppercase/unclosed tag
    # silently breaks discoverability for that lesson. GOOD_TAG_RE only ran on
    # incoming/; once a proposal was promoted (and its incoming file deleted),
    # nothing ever re-checked its tags. Validate the leading tag block of every
    # index entry.
    for line in text.splitlines():
        m = ENTRY_START_RE.match(line)
        if not m:
            continue
        for t in TAG_TOKEN_RE.findall(m.group(1)):
            if not GOOD_TAG_RE.match(t):
                fail(f"PITFALLS.md: malformed tag {t} in index line "
                     f"(lowercase [a-z0-9._-], bracketed): {line.strip()[:60]}")
    for m in ANCHOR_RE.finditer(text):
        target, anchor = m.group(1), m.group(2)
        tpath = os.path.join(ROOT, target)
        if not os.path.exists(tpath):
            fail(f"PITFALLS.md: anchor target {target} does not exist.")
            continue
        if anchor not in ids_in(read(tpath)):
            fail(f"PITFALLS.md: {target}#{anchor} does not resolve to a heading.")


def base_ref():
    base = os.environ.get("GITHUB_BASE_REF")
    if base and git("rev-parse", "--verify", "origin/" + base) is not None:
        return "origin/" + base
    # A push can carry several commits; compare against the commit before the
    # whole push, not only HEAD~1, or a removal in an earlier commit of the
    # same push is never seen (the 2026-10-15 cleanup passed unchecked this way).
    before = os.environ.get("PUSH_BEFORE", "")
    if before.strip("0") and git("rev-parse", "--verify", before + "^{commit}") is not None:
        return before
    if git("rev-parse", "--verify", "HEAD~1") is not None:
        return "HEAD~1"
    return None


OWNER_EXCEPTION_RE = re.compile(r"^Owner-Exception:\s*\S", re.M)


def owner_exception(base: str) -> bool:
    """True when a commit in base..HEAD carries an `Owner-Exception:` trailer:
    a removal the owner approved, recorded in history (and in the tension
    ledger) instead of slipping through. It turns the failure into a warning."""
    log = git("log", "--format=%B", f"{base}..HEAD")
    return bool(log and OWNER_EXCEPTION_RE.search(log))


def check_append_only() -> None:
    base = base_ref()
    if not base:
        return  # nothing to compare against (first commit / shallow clone)
    report = warn if owner_exception(base) else fail
    current = set(project_files())
    listed = git("ls-tree", "--name-only", base, "projects/") or ""
    for rel in sorted(x for x in listed.splitlines() if x.endswith(".md")):
        if rel not in current:
            old = git("show", f"{base}:{rel}") or ""
            n = len(ids_in(old))
            report(f"{rel}: append-only violation — the whole file ({n} entr"
                   f"{'y' if n == 1 else 'ies'}) was removed. Correct via a new "
                   "dated entry, or record the owner's approval in an "
                   "'Owner-Exception:' commit trailer.")
    for rel in sorted(current):
        old = git("show", f"{base}:{rel}")
        if old is None:
            continue  # newly added file
        removed = set(ids_in(old)) - set(ids_in(read(os.path.join(ROOT, rel))))
        if removed:
            plural = "y" if len(removed) == 1 else "ies"
            report(
                f"{rel}: append-only violation — entr{plural} "
                f"{', '.join(sorted(removed))} removed. Correct via a new dated entry."
            )


def changed_files():
    """Union of paths changed vs the base commit, plus staged/untracked, so the
    scope check works both in CI (committed PR diff) and locally (staged drop)."""
    files = set()
    base = base_ref()
    if base:
        out = git("diff", "--name-only", f"{base}...HEAD")
        if out:
            files.update(out.split())
    for extra in (git("diff", "--name-only", "HEAD"),
                  git("ls-files", "--others", "--exclude-standard")):
        if extra:
            files.update(extra.split())
    return {f for f in files if f}


def check_contribution_scope() -> None:
    """Contributor mode: changes may only touch incoming/. Canon is steward-only.
    Active only when ENFORCE_INCOMING_ONLY=1 (set by CI on pull_request)."""
    if os.environ.get("ENFORCE_INCOMING_ONLY") != "1":
        return
    for f in sorted(p for p in changed_files() if not p.startswith("incoming/")):
        fail(
            f"{f}: contributors may only add files under incoming/. "
            "Canon is changed only by a steward promoting your drop."
        )


PROPOSAL_FIELDS = [
    "tags",
    "what",
    "why built",
    "design",
    "got right",
    "where/why",
    "fix",
    "why this fix",
    "rule of thumb",
]
REVIEW_FIELDS = ["target", "kind", "verdict", "checked", "link"]
PROPOSAL_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}__[a-z0-9][a-z0-9-]*\.md$")


def check_incoming() -> None:
    d = os.path.join(ROOT, "incoming")
    if not os.path.isdir(d):
        return
    for f in sorted(os.listdir(d)):
        # stubs.md is the zero-validation capture file (capture/curate split);
        # stubs graduate through the template at curation time.
        if not f.endswith(".md") or f in ("README.md", "TEMPLATE.md", "stubs.md"):
            continue
        rel = f"incoming/{f}"
        text = read(os.path.join(d, f))
        if held(text):
            # Steward-quarantined for a human — skip, exactly as
            # check_incoming_content() does. Re-flagging it would keep the
            # steward run red and block committing other proposals' promotions.
            continue
        if not PROPOSAL_NAME_RE.match(f):
            fail(f"{rel}: name must be YYYY-MM-DD__<slug>.md (lowercase slug).")
        if re.search(r"^##\s*REVIEW\s*$", text, re.M):
            # a review of an existing entry (REVIEW-TEMPLATE.md), not a lesson:
            # the steward appends it to its target, so lesson fields don't apply
            for fld in REVIEW_FIELDS:
                if not re.search(rf"^\s*-\s*\**{fld}\**\s*:", text, re.M | re.I):
                    fail(f"{rel}: review missing required field '{fld}'.")
            continue
        if re.search(r"^\s*-\s*\**(Audited|Reverified)\**\s*:", text, re.M | re.I):
            fail(f"{rel}: a lesson may not carry its own Audited/Reverified line "
                 "— file a separate REVIEW (REVIEW-TEMPLATE.md).")
        low = text.lower()
        for field in PROPOSAL_FIELDS:
            if field not in low:
                fail(f"{rel}: missing required field '{field}'.")
        for line in text.splitlines():
            if re.match(r"^\s*[-*]?\s*\**tags\**\s*:", line, re.I):
                toks = TAG_TOKEN_RE.findall(line.split(":", 1)[1])
                if not toks:
                    fail(f"{rel}: Tags line has no [bracketed] tags.")
                for t in toks:
                    if not GOOD_TAG_RE.match(t):
                        fail(f"{rel}: bad tag {t} (use lowercase [a-z0-9._-], bracketed).")
                break
        if not ANCHOR_RE.search(text) and "→ projects/" not in text:
            fail(
                f"{rel}: missing a proposed index line "
                "(`[tags]` lesson → projects/<file>.md#<id>)."
            )
        m = re.search(r"^\s*[-*]?\s*\**polarity\**\s*:\s*(.*)$", text, re.M | re.I)
        if m and m.group(1).strip().lower() not in ("compatible", "incompatible"):
            fail(f"{rel}: Polarity must be 'compatible' or 'incompatible'.")
        # `Composed:` is OPTIONAL (single-system lessons omit it). It is only
        # validated when present: it must be an explicit N/A/none, or contain at
        # least one parseable ref — a `<slug>/E<n>` memory entry, or an
        # `ideas:<DOMAIN>/<path>` kernel (some canon domains are lowercase, e.g.
        # `testing/harness/...`). Whether a kernel ref resolves is
        # checked by `brain analyze graph`, which has the ideas repo; this repo
        # does not. Never fires on a proposal that omits the field.
        for line in text.splitlines():
            m = re.match(r"^\s*[-*]?\s*\**composed\**\s*:\s*(.*)$", line, re.I)
            if not m:
                continue
            val = m.group(1).strip()
            if not val or re.fullmatch(r"(n/?a|none|—|-)\.?", val, re.I):
                break
            if not (re.search(r"[a-z0-9][a-z0-9-]*/E\d+", val, re.I)
                    or re.search(r"ideas:\s*\[?\s*[A-Za-z][A-Za-z0-9-]*\s*/", val)):
                fail(f"{rel}: Composed field present but has no parseable "
                     "`<slug>/E<n>` or `ideas:<DOMAIN>/<kernel>` ref "
                     "(use `N/A` for a single-system lesson).")
            break


def check_incoming_content() -> None:
    """PR-time safety subset. The steward's real content gates (injection scan,
    provenance) live in steward.py and only run in the post-merge steward job —
    so a green PR check formerly meant NONE of them had run, and a reviewer
    trusting green CI had zero automated poisoning defense until content was
    already on main. Reuse steward.py's OWN regexes/predicates (single source,
    no drift) to run the injection + provenance gates here, at pull_request
    time. Promotion, dedup and substance stay steward-side; this is only the
    subset that must not wait until after merge. Active under
    ENFORCE_INCOMING_ONLY=1 (set by CI on pull_request), matching the scope
    check. A hit fails CI = "a human must look before this merges" — a false
    positive is a safe-fail, never a silent pass."""
    if os.environ.get("ENFORCE_INCOMING_ONLY") != "1":
        return
    d = os.path.join(ROOT, "incoming")
    if not os.path.isdir(d):
        return
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "steward_checks", os.path.join(ROOT, "scripts", "steward.py")
    )
    try:
        steward = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(steward)
    except Exception as e:  # never let a loader hiccup silently drop the gate
        fail(f"could not load steward safety checks from steward.py: {e}")
        return
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md") or f in ("README.md", "TEMPLATE.md", "stubs.md"):
            continue
        rel = f"incoming/{f}"
        text = read(os.path.join(d, f))
        if steward.HOLD_MARKER_RE.search(text):
            continue  # already held for a human; don't double-flag
        for rx in steward.INJECTION_RES:
            if rx.search(text):
                fail(f"{rel}: injection-pattern content — blocked pending "
                     "human review (a lesson other agents read must not carry "
                     "directives aimed at them).")
                break
        if "provenance" in text.lower():
            fields, _index = steward.parse(text)
            if not steward.provenance_ok(steward.field(fields, "provenance")):
                fail(f"{rel}: provenance not clearly verified/firsthand "
                     "(empty, negated, or assumed-only) — needs a human.")
        # Format gates mirrored from steward.check(): these two deviations
        # don't hold safely, they promote LOSSILY (empty body / truncated
        # index line), so they must fail at PR time, not post-merge.
        if hasattr(steward, "wrapped_index_line") and steward.wrapped_index_line(text):
            fail(f"{rel}: PROPOSED INDEX LINE spans multiple lines — it is "
                 "machine-read verbatim into PITFALLS.md and must be ONE "
                 "physical line, not wrapped prose.")
        if "FULL ENTRY" in text and not re.search(r"^\s*-\s*ID\s*:", text, re.M):
            fail(f"{rel}: missing '- ID:' bullet — the steward's body capture "
                 "is keyed on it; without it the entry promotes EMPTY.")


def check_incoming_sandboxes() -> None:
    """Sandbox files shipped beside proposals (see steward.py SANDBOX_NAME_RE).
    Nothing here RUNS them. A misnamed or unreferenced one warns; injection text
    fails at pull_request time, same bar as the proposal body, because agents
    read (and rerun) stored sandboxes."""
    d = os.path.join(ROOT, "incoming")
    if not os.path.isdir(d):
        return
    pys = sorted(f for f in os.listdir(d) if f.endswith(".py"))
    if not pys:
        return
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location(
            "steward_checks", os.path.join(ROOT, "scripts", "steward.py"))
        steward = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(steward)
    except Exception as e:  # never let a loader hiccup silently drop the gate
        fail(f"could not load steward checks from steward.py: {e}")
        return
    named = set()
    for f in os.listdir(d):
        if f.endswith(".md"):
            # cut any appended STEWARD HOLD block: its `- reason:` lines
            # parse as fields and would shadow the real `- Sandbox:`
            body = steward.HOLD_MARKER_RE.split(read(os.path.join(d, f)))[0]
            fields, _ = steward.parse(body)
            named.add(steward.sandbox_name(fields))
    for f in pys:
        rel = f"incoming/{f}"
        if not steward.SANDBOX_NAME_RE.match(f):
            warn(f"{rel}: sandbox name should be YYYY-MM-DD__<slug>.py")
        if f not in named:
            warn(f"{rel}: no proposal names this sandbox in '- Sandbox:'")
        if os.environ.get("ENFORCE_INCOMING_ONLY") == "1":
            try:
                code = read(os.path.join(d, f))
            except (UnicodeDecodeError, OSError):
                fail(f"{rel}: sandbox is not readable UTF-8 text")
                continue
            if any(rx.search(code) for rx in steward.INJECTION_RES):
                fail(f"{rel}: injection-pattern content in sandbox — blocked "
                     "pending human review.")


SECRET_RES = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
        "private key",
    ),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|password|token)\b\s*[:=]\s*"
            r"['\"][^'\"]{12,}['\"]"
        ),
        "hardcoded credential",
    ),
]


def scan_secrets() -> None:
    self_rel = os.path.join("scripts", "validate.py")
    for dirpath, _dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            if rel == self_rel:
                continue  # this file contains the patterns themselves
            try:
                text = read(os.path.join(dirpath, fn))
            except (UnicodeDecodeError, OSError):
                continue
            for rx, label in SECRET_RES:
                if rx.search(text):
                    fail(f"{rel}: possible {label} committed — no secrets in the repo.")
                    break


def main() -> int:
    check_contribution_scope()
    check_projects()
    check_pitfalls()
    check_append_only()
    check_incoming()
    check_incoming_content()
    check_incoming_sandboxes()
    scan_secrets()
    for w in warnings:
        print(f"  ⚠ {w}")
    if errors:
        print("VALIDATION FAILED:\n")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n{len(errors)} problem(s).")
        return 1
    print("✓ validation passed — canon is consistent, append-only, and clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
