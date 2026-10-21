#!/usr/bin/env python3
"""Offline Brain for the brain-zanegpt plugin.

The plugin bundles the upstream canon files, Brain's own CLI and the memory
repo's own steward. Local lessons go through that same steward, reviews and
training, so they carry the same checks as shared canon. Nothing here performs
a network operation, and all user data lives outside the plugin.

Commands run by Brain's CLI (offline):
  query <terms> [--verbose]   challenge <terms>   paths [topic]
  mine                        train [mode]        check <proposal.md>
  analyze [report]            tension             scorecard
Commands run by this script:
  status                      sync                mine --add <proposal>
  export --out <file.zip>     import <file.zip|export.json>
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

VERSION = "2.0.0"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CANON = PLUGIN_ROOT / "canon"
MANIFEST_PATH = CANON / "MANIFEST.json"
BRAIN_CLI = CANON / "Brain" / "bin" / "brain"
STEWARD_RUNNER = Path(__file__).resolve().parent / "steward_local.py"
LOCAL_SUFFIX = "__local"
STORE_VERSION = 2
# Commands handed to Brain's CLI unchanged.
DELEGATED = ("query", "challenge", "paths", "mine", "train", "check",
             "analyze", "tension", "scorecard")
# Files the local store seeds itself with (same seeds as Brain's ensure_local).
SEEDS = {
    "memory/PITFALLS.md": "# LOCAL PITFALLS — this project's private index\n",
    "memory/incoming/stubs.md": "# LOCAL STUBS\n\n<!-- append stubs below -->\n",
    "ideas/idea-repository.md": "# LOCAL IDEAS\n",
    "ideas/exploration.md": "# LOCAL EXPLORATION\n",
    "tension/tension-ledger.md": "# LOCAL TENSION LEDGER\n",
}
INCOMING_SKIP = {"README.md", "TEMPLATE.md", "stubs.md"}
ENTRY_HEAD_RE = re.compile(r"^## (E\d+)\b", re.M)
STEWARD_LINE_RE = re.compile(r"^-\s*(Audited|Reverified|Cited-by)\s*:", re.I)
INDEX_LINE_RE = re.compile(r"^- `\[")
ANCHOR_RE = re.compile(r"→\s*projects/([^\s#]+\.md)#(E\d+)")


def _print_safe(*parts: object) -> None:
    text = " ".join(str(part) for part in parts)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding or "ascii", "replace").decode(
            sys.stdout.encoding or "ascii"))


def cli_command() -> str:
    return f'python "{Path(__file__).resolve()}"'


# ------------------------------------------------------------------ the store

def data_root() -> Path:
    override = os.environ.get("BRAIN_ZANEGPT_DATA") or os.environ.get("PLUGIN_DATA")
    if override:
        return Path(override).expanduser().resolve()
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return (base / "brain-zanegpt").resolve()


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"canon bundle missing: {MANIFEST_PATH}")
    return _read_json(MANIFEST_PATH)


def ensure_store() -> Path:
    """The user's store, laid out exactly like Brain's local `.brain/` store."""
    root = data_root()
    for sub in ("memory/incoming", "memory/projects", "memory/sandboxes",
                "memory/overlay", "ideas", "tension"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    for rel, body in SEEDS.items():
        if not (root / rel).exists():
            _write(root / rel, body)
    version_file = root / "store.json"
    if not version_file.exists():
        _write(version_file, json.dumps({"store_version": STORE_VERSION}) + "\n")
    return root


# ---------------------------------------------------------- entry text helpers

def _entry_spans(text: str) -> dict[str, tuple[int, int]]:
    """E-id -> (start, end) of its block; same bounds the steward uses."""
    spans = {}
    for match in re.finditer(r"^## (E\d+)\b.*$", text, re.M):
        nxt = re.search(r"^## E\d+\b|^---\s*$", text[match.end():], re.M)
        end = match.end() + nxt.start() if nxt else len(text)
        spans[match.group(1)] = (match.start(), end)
    return spans


def _append_to_entry(text: str, eid: str, lines: list[str]) -> str:
    span = _entry_spans(text).get(eid)
    if not span:
        return text
    start, end = span
    block = text[start:end]
    new = [line for line in lines if line not in block.splitlines()]
    if not new:
        return text
    body = block.rstrip("\n") + "\n" + "\n".join(new) + "\n"
    tail = text[end:]
    if tail and not tail.startswith("\n"):
        body += "\n"
    return text[:start] + body + tail


def _overlay(root: Path) -> dict[str, dict[str, list[str]]]:
    """Steward lines (reviews, Cited-by) local work added to SHARED entries."""
    result: dict[str, dict[str, list[str]]] = {}
    for path in sorted((root / "memory" / "overlay").glob("*.md")):
        current = None
        for line in _read(path).splitlines():
            head = ENTRY_HEAD_RE.match(line)
            if head:
                current = head.group(1)
            elif current and STEWARD_LINE_RE.match(line):
                result.setdefault(path.name, {}).setdefault(current, []).append(line)
    return result


def _save_overlay(root: Path, name: str, entries: dict[str, list[str]]) -> None:
    def key(eid: str) -> int:
        return int(eid[1:])
    parts = [f"# Local review lines on shared {name}\n"]
    for eid in sorted(entries, key=key):
        parts.append(f"\n## {eid}\n" + "\n".join(entries[eid]) + "\n")
    _write(root / "memory" / "overlay" / name, "".join(parts))


def _local_index_lines(root: Path) -> list[str]:
    return [line for line in _read(root / "memory" / "PITFALLS.md").splitlines()
            if INDEX_LINE_RE.match(line)]


# --------------------------------------------------------------- the view
# Brain's CLI and the steward expect one memory repo. The view is that repo,
# rebuilt from the bundle plus the user's store whenever either changes. It is
# derived data: deleting it loses nothing.

def _fingerprint(root: Path) -> str:
    digest = hashlib.sha256(f"{VERSION}\0{manifest().get('sha256')}".encode())
    for sub in ("memory", "ideas", "tension"):
        base = root / sub
        for path in sorted(base.rglob("*")):
            if path.is_file() and not path.name.endswith(".tmp"):
                stat = path.stat()
                digest.update(f"{path.relative_to(root)}\0{stat.st_size}\0"
                              f"{stat.st_mtime_ns}\0".encode())
    return digest.hexdigest()


def build_view(root: Path, force: bool = False) -> Path:
    view = root / "view"
    stamp = root / "view.stamp"
    fingerprint = _fingerprint(root)
    if not force and view.is_dir() and _read(stamp).strip() == fingerprint:
        return view
    staging = root / "view.building"
    if staging.exists():
        shutil.rmtree(staging)
    for name in ("memory", "ideas", "Tension"):
        shutil.copytree(CANON / name, staging / name)
    memory = staging / "memory"
    projects = memory / "projects"
    for name, entries in _overlay(root).items():
        target = projects / name
        if target.exists():
            text = _read(target)
            for eid, lines in entries.items():
                text = _append_to_entry(text, eid, lines)
            _write(target, text)
    for path in (root / "memory" / "projects").glob("*.md"):
        shutil.copy2(path, projects / path.name)
    for path in (root / "memory" / "sandboxes").glob("*.py"):
        shutil.copy2(path, memory / "sandboxes" / path.name)
    local_index = _local_index_lines(root)
    if local_index:
        pitfalls = memory / "PITFALLS.md"
        _write(pitfalls, _read(pitfalls).rstrip("\n") + "\n" + "\n".join(local_index) + "\n")
    for path in (root / "memory" / "incoming").iterdir():
        if path.is_file() and path.name not in ("README.md", "TEMPLATE.md"):
            shutil.copy2(path, memory / "incoming" / path.name)
    if view.exists():
        shutil.rmtree(view)
    os.replace(staging, view)
    _write(stamp, fingerprint + "\n")
    return view


# ---------------------------------------------------------- Brain's own CLI

def _rewrite(text: str, root: Path) -> str:
    """Point Brain's instructions at this plugin's store and launcher."""
    command = cli_command()
    for sub in ("memory/incoming", "memory", "ideas", "tension"):
        text = text.replace(f".brain/{sub}/", f"{(root / sub).as_posix()}/")
    return re.sub(r"\bbrain (query|challenge|paths|mine|train|check|analyze|tension|"
                  r"scorecard|sync|status)\b", lambda m: f"{command} {m.group(1)}", text)


def _codex_answer(prompt: str) -> str:
    """The ZaneGPT check in a separate Codex agent, when `claude` is absent."""
    with tempfile.TemporaryDirectory(prefix="brain-zanegpt-check-") as tmp:
        out = Path(tmp) / "answer.txt"
        try:
            subprocess.run(["codex", "exec", "--skip-git-repo-check", "--ephemeral",
                            "--sandbox", "read-only", "-o", str(out), prompt],
                           cwd=tmp, capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return _read(out)


def load_brain(root: Path, view: Path, argv: list[str]):
    os.environ["BRAIN_CACHE"] = str(view)
    sys.argv = ["brain", *argv]
    loader = importlib.machinery.SourceFileLoader("brain_cli", str(BRAIN_CLI))
    spec = importlib.util.spec_from_loader("brain_cli", loader)
    brain = importlib.util.module_from_spec(spec)
    loader.exec_module(brain)
    memory = str(view / "memory")
    local_memory = str(root / "memory")
    shared_index = brain._memory_index

    def memory_index(base: str) -> list[str]:
        rows = shared_index(base)
        if os.path.abspath(base) == os.path.abspath(memory):
            # local lines live in the view for the steward; report them once,
            # in the LOCAL bucket, the way Brain does
            return [row for row in rows if f"{LOCAL_SUFFIX}.md#" not in row]
        if os.path.abspath(base) == os.path.abspath(local_memory) and rows:
            # Brain tags shared hits with their review tier; do the same here
            tiers = {(e["file"], e["id"]): e["tier"] for e in brain._load_entries([memory])
                     if e["file"].endswith(f"{LOCAL_SUFFIX}.md")}
            tagged = []
            for row in rows:
                anchor = ANCHOR_RE.search(row)
                tier = tiers.get((anchor.group(1), anchor.group(2))) if anchor else None
                tagged.append(f"{row}  [{tier}]" if tier and tier != "provisional" else row)
            return tagged
        return rows

    brain.require_link = lambda need_enabled=True: {
        "mode": "read-only", "enabled": True, "stance": "conversation"}
    brain.ensure_cache = lambda pull=True: []
    brain._self_update = lambda: None
    brain._inject_pointer = lambda: None
    brain.local_root = lambda: str(root)
    brain._memory_index = memory_index
    # the view already holds the local lessons, promoted by the same steward,
    # so training and analysis treat them as canon rather than as a second base
    brain._analyze_bases = lambda: [memory]
    return brain


# Hits per section a verbose query prints. Brain's matcher is a substring test
# (`ui` matches "build"), and a broad term used to put the whole canon into the
# agent's context; verbose now prints the most relevant hits only.
VERBOSE_TOP = {"memory": 12, "tension": 5, "ideas": 8, "exploration": 4,
               "incoming": 6}


def _term_patterns(terms: list[str]) -> list[tuple[re.Pattern, re.Pattern]]:
    """(word-start, whole-word) pattern per term; hyphens, underscores, slashes
    and spaces inside a term are interchangeable, as in Brain's own matcher."""
    result = []
    for term in terms:
        words = [w for w in re.split(r"[\s_/-]+", term.lower()) if w]
        if words:
            body = r"[\s_/-]*".join(re.escape(w) for w in words)
            result.append((re.compile(r"(?<![a-z0-9])" + body, re.I),
                           re.compile(r"(?<![a-z0-9])" + body + r"(?:e?s)?(?![a-z0-9])", re.I)))
    return result


def _relevance(text: str, patterns: list[tuple[re.Pattern, re.Pattern]]) -> int:
    """0 unless some term starts a word in the text. Ranks by how many terms
    hit, then hits in the heading or tags, then exact words, then frequency."""
    head = text.split("\n", 1)[0]
    terms_hit = score = 0
    for start, whole in patterns:
        body_hits = len(start.findall(text))
        if not body_hits:
            continue
        terms_hit += 1
        score += 4 * min(len(start.findall(head)), 3) + 2 * min(len(whole.findall(text)), 5) \
            + min(body_hits, 5)
    return 100 * terms_hit + score if terms_hit else 0


def _install_ranked_matcher(brain, root: Path, top: dict[str, int] | None):
    """Swap Brain's `matches` for one that admits only the top-ranked hits per
    section. Returns {terms: {section: (shown, total)}} filled as queries run."""
    plain = brain.matches
    report: dict[tuple[str, ...], dict[str, tuple[int, int]]] = {}
    allowed: dict[tuple[str, ...], set[str]] = {}

    def pools() -> dict[str, list[str]]:
        canon = dict(brain._shared_canon())
        local = str(root / "memory")
        return {
            "memory": canon["memory"], "tension": canon["tension"],
            "ideas": canon["ideas"], "exploration": canon["exploration"],
            "local memory": brain._memory_index(local),
            "local tension": brain._blocks(_read(root / "tension" / "tension-ledger.md"), "### "),
            "local ideas": brain._blocks(_read(root / "ideas" / "idea-repository.md"), "## ["),
            "incoming": [body for _, body, _ in brain._incoming_proposals(brain.node("memory"))],
        }

    def admitted(terms: list[str]) -> set[str]:
        key = tuple(terms)
        if key not in allowed:
            patterns = _term_patterns(terms)
            keep: set[str] = set()
            counts = {}
            for section, rows in pools().items():
                hits = [row for row in rows if plain(row, terms)]
                ranked = sorted(((_relevance(row, patterns), i, row) for i, row in enumerate(hits)),
                                key=lambda item: (-item[0], item[1]))
                relevant = [row for score, _, row in ranked if score > 0]
                # nothing starts a word: fall back to Brain's substring hits
                chosen = relevant or [row for _, _, row in ranked]
                limit = None if top is None else top.get(section.replace("local ", ""), 8)
                chosen = chosen if limit is None else chosen[:limit]
                keep.update(chosen)
                counts[section] = (len(chosen), len(hits))
            allowed[key] = keep
            report[key] = counts
        return allowed[key]

    brain.matches = lambda block, terms: block in admitted(terms)
    return report


def _query_flags(argv: list[str]) -> tuple[list[str], dict[str, int] | None]:
    """Strip --all / --top N from a query's argv; return (argv, caps)."""
    top: dict[str, int] | None = dict(VERBOSE_TOP)
    rest, i = [], 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--all":
            top = None
        elif arg == "--top" and i + 1 < len(argv) and argv[i + 1].isdigit():
            top = {section: int(argv[i + 1]) for section in VERBOSE_TOP}
            i += 1
        else:
            rest.append(arg)
        i += 1
    return rest, top


def run_brain(argv: list[str]) -> int:
    root = ensure_store()
    view = build_view(root)
    saved_argv = sys.argv[:]
    command = argv[0]
    ranked = None
    if command == "query":
        argv, top = _query_flags(argv)
        ranked = "--verbose" in argv
    if command == "check" and not shutil.which("claude") and shutil.which("codex") \
            and "--answer" not in argv:
        files = [arg for arg in argv[1:] if not arg.startswith("--")]
        if files:
            brain = load_brain(root, view, ["check", *files])
            path = Path(files[0])
            if not path.is_file():
                path = root / "memory" / "incoming" / path.name
            if path.is_file():
                _print_safe("· running the ZaneGPT check in a separate agent (codex exec) …")
                answer = _codex_answer(brain._zanegpt_prompt(_read(path)))
                if answer:
                    handle = tempfile.NamedTemporaryFile(
                        "w", suffix=".txt", delete=False, encoding="utf-8")
                    handle.write(answer)
                    handle.close()
                    argv = [*argv, "--answer", handle.name]
    buffer = io.StringIO()
    report: dict = {}
    try:
        brain = load_brain(root, view, argv)
        if ranked:
            report = _install_ranked_matcher(brain, root, top)
        with contextlib.redirect_stdout(buffer):
            code = brain.COMMANDS[command]()
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else 1
    finally:
        sys.argv = saved_argv
    output = buffer.getvalue()
    if command in ("mine", "train", "check"):
        # these print instructions for the agent; retrieved canon is data and
        # is never rewritten
        output = _rewrite(output, root)
    if output:
        _print_safe(output.rstrip("\n"))
    if report:
        counts = list(report.values())[-1]
        cut = [f"{section} {shown}/{total}" for section, (shown, total) in counts.items()
               if shown < total]
        if cut:
            _print_safe(f"\n(most relevant hits only — {', '.join(cut)}. "
                        "Narrow the query, or pass --top N / --all for more)")
    if command in ("train", "challenge", "check") and code == 0:
        _print_safe(f"\n(canon paths such as projects/… and sandboxes/… are under "
                    f"{(view / 'memory').as_posix()}/ — read-only; write only to "
                    f"{(root / 'memory' / 'incoming').as_posix()}/)")
    return int(code or 0)


# ------------------------------------------------------------------- sync

def _project_texts(directory: Path) -> dict[str, str]:
    return {path.name: _read(path) for path in sorted(directory.glob("*.md"))}


def sync(root: Path) -> int:
    view = build_view(root, force=True)
    memory = view / "memory"
    before = _project_texts(memory / "projects")
    before_index = set(_read(memory / "PITFALLS.md").splitlines())
    before_sandboxes = {path.name for path in (memory / "sandboxes").glob("*.py")}
    env = dict(os.environ)
    env["GIT_CEILING_DIRECTORIES"] = str(view)
    env.pop("BRAIN_DEDUP_EXTRA", None)
    process = subprocess.run(
        [sys.executable, str(STEWARD_RUNNER), str(memory / "scripts" / "steward.py")],
        cwd=str(memory), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    report = process.stdout.strip()
    after = _project_texts(memory / "projects")

    # local project files: append-only, then copy back
    for name, text in after.items():
        if not name[:-3].endswith(LOCAL_SUFFIX):
            continue
        old = before.get(name, "")
        removed = set(ENTRY_HEAD_RE.findall(old)) - set(ENTRY_HEAD_RE.findall(text))
        if removed:
            _print_safe(f"✗ refusing a sync that removes local entries {sorted(removed)} "
                        f"from {name} — local canon is append-only")
            return 1
        if text != old:
            _write(root / "memory" / "projects" / name, text)

    # shared project files: only steward lines may change, kept as an overlay
    overlay = _overlay(root)
    for name, text in after.items():
        if name[:-3].endswith(LOCAL_SUFFIX) or text == before.get(name):
            continue
        old_spans = _entry_spans(before.get(name, ""))
        old_text = before.get(name, "")
        changed = False
        for eid, (start, end) in _entry_spans(text).items():
            if eid not in old_spans:
                _print_safe(f"⚠ unexpected new shared entry {name}#{eid} ignored")
                continue
            old_lines = set(old_text[old_spans[eid][0]:old_spans[eid][1]].splitlines())
            added = [line for line in text[start:end].splitlines()
                     if line not in old_lines and STEWARD_LINE_RE.match(line)]
            if added:
                kept = overlay.setdefault(name, {}).setdefault(eid, [])
                kept.extend(line for line in added if line not in kept)
                changed = True
        if changed:
            _save_overlay(root, name, overlay[name])

    # new index lines -> the local index
    new_index = [line for line in _read(memory / "PITFALLS.md").splitlines()
                 if line not in before_index and INDEX_LINE_RE.match(line)]
    if new_index:
        pitfalls = root / "memory" / "PITFALLS.md"
        _write(pitfalls, _read(pitfalls).rstrip("\n") + "\n" + "\n".join(new_index) + "\n")

    # sandboxes the steward moved out of incoming/
    for path in (memory / "sandboxes").glob("*.py"):
        if path.name not in before_sandboxes:
            shutil.copy2(path, root / "memory" / "sandboxes" / path.name)

    # incoming: promoted drops are gone, held ones carry their hold block
    incoming = root / "memory" / "incoming"
    for path in sorted(incoming.iterdir()):
        if not path.is_file() or path.name in INCOMING_SKIP:
            continue
        mirrored = memory / "incoming" / path.name
        if not mirrored.exists():
            path.unlink()
        elif _read(mirrored) != _read(path):
            shutil.copy2(mirrored, path)

    (root / "view.stamp").unlink(missing_ok=True)
    if process.returncode not in (0, 1) and not report:
        _print_safe(f"✗ steward failed: {process.stderr.strip()[-600:]}")
        return 1
    match = re.search(r"promoted (\d+) . held (\d+) . previously-held (\d+)", report)
    promoted, held, previously = (int(g) for g in match.groups()) if match else (0, 0, 0)
    if "--verbose" in sys.argv or held or process.returncode:
        _print_safe("  " + report.replace("\n", "\n  "))
        if process.stderr.strip():
            _print_safe("  " + process.stderr.strip().replace("\n", "\n  "))
    stubs = [line for line in _read(incoming / "stubs.md").splitlines()
             if line.startswith("- ")]
    note = (f"{promoted} promoted to local canon, {held} held"
            + (f", {previously} still held from before" if previously else "")
            + (f", {len(stubs)} stub(s) kept" if stubs else ""))
    _print_safe(f"✓ synced (offline) — {note}; no network used")
    if held or previously:
        _print_safe("\n--- AGENT INSTRUCTION (do this now, do not ask) ---")
        _print_safe(f"Held proposals stay in {incoming.as_posix()}/ with a STEWARD HOLD "
                    "block listing the reasons. For each one:")
        _print_safe("  1. Fix exactly the listed reasons, using the schema from "
                    f"`{cli_command()} mine`. Write the missing content from what "
                    "actually happened; do NOT invent evidence, and do NOT reword "
                    "Provenance to satisfy the check.")
        _print_safe("  2. Delete the STEWARD HOLD block, then run sync again.")
        _print_safe("Repeat up to 3 times per proposal. If it still cannot pass, or the "
                    "lesson does not meet the bar, delete the file and say so.")
    if process.returncode:
        _print_safe("⚠ post-promotion validation reported a problem (see above)")
    return 0 if not (held or process.returncode) else 1


# ---------------------------------------------------- proposals and import

def _one_line(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:64] or "lesson"


def _tag(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", str(text).lower()).strip("-")


def _proposal_from_json(item: dict[str, Any]) -> tuple[str, str]:
    """A v1 JSON lesson as a memory-repo proposal (TEMPLATE.md schema)."""
    tags = "".join(f"[{_tag(tag)}]" for tag in item.get("tags") or [] if _tag(tag))
    composed = item.get("composed") or []
    if isinstance(composed, list):
        composed = ", ".join(str(ref) for ref in composed)
    fields = [
        ("ID", "E?"), ("Date", item.get("date")), ("Project", item.get("project")),
        ("Tags", tags), ("What", item.get("what")), ("Why built", item.get("why_built")),
        ("Design", item.get("design")), ("Got right", item.get("got_right")),
        ("Where/why it failed", item.get("failure")), ("Fix", item.get("fix")),
        ("Why this fix", item.get("why_fix")), ("Rule of thumb", item.get("rule")),
        ("Provenance (verified/assumed)", item.get("provenance")),
    ]
    if composed:
        fields.append(("Composed", composed))
    fields.append(("Link", item.get("link")))
    body = "\n".join(f"- {label}: {_one_line(value)}" for label, value in fields)
    date = str(item.get("date") or dt.date.today().isoformat())[:10]
    name = f"{date}__{_slug(str(item.get('rule') or item.get('what') or 'lesson'))}.md"
    text = (f"## FULL ENTRY\n\n{body}\n\n## PROPOSED INDEX LINE\n\n"
            f"`{tags or '[general]'}` {_one_line(item.get('rule'))}\n")
    return name, text


def _proposal_from_entry(block: str, index_line: str) -> tuple[str, str, str]:
    """A promoted entry block back into a proposal: (name, text, sandbox)."""
    lines = block.splitlines()
    title = re.sub(r"^## E\d+\s*[—-]?\s*", "", lines[0]).strip()
    date = ""
    sandbox = ""
    body = []
    for line in lines[1:]:
        if not line.strip() or line.strip() == "---":
            continue
        match = re.match(r"^-\s*Date\s*:\s*(\S+)", line)
        if match:
            date = match.group(1)[:10]
        match = re.match(r"^-\s*Sandbox\s*:\s*(?:sandboxes/)?(\S+\.py)", line)
        if match:
            sandbox = match.group(1)
            line = f"- Sandbox: {sandbox}"
        if STEWARD_LINE_RE.match(line):
            # review and citation lines are written by the steward, never by an
            # author; this store re-derives Cited-by and re-earns reviews
            continue
        body.append(line)
    date = date if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) else dt.date.today().isoformat()
    lesson = ANCHOR_RE.sub("", index_line).strip()
    lesson = re.sub(r"^-\s*", "", lesson)
    text = ("## FULL ENTRY\n\n- ID: E?\n" + "\n".join(body)
            + f"\n\n## PROPOSED INDEX LINE\n\n{lesson}\n")
    return f"{date}__{_slug(title)}.md", text, sandbox


def _stage(root: Path, name: str, text: str) -> Path | None:
    incoming = root / "memory" / "incoming"
    target = incoming / name
    stem = target.stem
    counter = 2
    while target.exists():
        if _read(target) == text:
            return None
        target = incoming / f"{stem}-{counter}.md"
        counter += 1
    _write(target, text)
    return target


def migrate_v1(root: Path) -> int:
    """Move a v1 JSON store into the v2 store as proposals for the steward."""
    legacy = root / "knowledge.json"
    old_incoming = root / "incoming"
    if not legacy.exists() and not old_incoming.is_dir():
        return 0
    items = []
    if legacy.exists():
        try:
            items += list(_read_json(legacy).get("entries", []))
        except (OSError, ValueError, AttributeError):
            pass
    if old_incoming.is_dir():
        for path in sorted(old_incoming.glob("*.json")):
            if path.name == "TEMPLATE.json":
                continue
            try:
                items.append(_read_json(path))
            except (OSError, ValueError):
                pass
    staged = 0
    for item in items:
        if isinstance(item, dict):
            name, text = _proposal_from_json(item)
            staged += 1 if _stage(root, name, text) else 0
    backup = root / "legacy-v1"
    backup.mkdir(exist_ok=True)
    if legacy.exists():
        os.replace(legacy, backup / "knowledge.json")
    if old_incoming.is_dir():
        shutil.move(str(old_incoming), str(backup / "incoming"))
    return staged


def _store_is_empty(root: Path) -> bool:
    memory = root / "memory"
    return not (any((memory / "projects").glob("*.md"))
                or any((memory / "overlay").glob("*.md"))
                or any(path.name not in INCOMING_SKIP for path in (memory / "incoming").iterdir())
                or _local_index_lines(root)
                or any(_read(root / rel) != body for rel, body in SEEDS.items()
                       if not rel.startswith("memory/")))


def import_zip(root: Path, source: Path) -> tuple[int, bool]:
    """(proposals staged, restored). Into an empty store an export is restored
    exactly, reviews included: it is the same canon moving between machines.
    Into a store that already has lessons, each lesson is re-filed through the
    steward, so a merge cannot slip past dedup or renumber over local entries."""
    staged = 0
    with tempfile.TemporaryDirectory(prefix="brain-zanegpt-import-") as tmp:
        base = Path(tmp)
        with zipfile.ZipFile(source) as archive:
            for member in archive.namelist():
                resolved = (base / member).resolve()
                if not str(resolved).startswith(str(base.resolve()) + os.sep):
                    raise SystemExit(f"unsafe path in export: {member}")
            archive.extractall(base)
        if not (base / "export.json").exists():
            raise SystemExit("not a brain-zanegpt export (no export.json)")
        if _store_is_empty(root):
            for sub in ("memory", "ideas", "tension"):
                if (base / sub).is_dir():
                    shutil.copytree(base / sub, root / sub, dirs_exist_ok=True)
            return 0, True
        index = {}
        for line in _read(base / "memory" / "PITFALLS.md").splitlines():
            anchor = ANCHOR_RE.search(line)
            if anchor:
                index[(anchor.group(1), anchor.group(2))] = line
        for path in sorted((base / "memory" / "projects").glob("*.md")):
            text = _read(path)
            spans = sorted(_entry_spans(text).items(), key=lambda kv: int(kv[0][1:]))
            for eid, (start, end) in spans:
                block = text[start:end]
                line = index.get((path.name, eid), "")
                if not line:
                    _print_safe(f"  skipped {path.name}#{eid}: no index line in the export")
                    continue
                name, proposal, sandbox = _proposal_from_entry(block, line)
                if sandbox:
                    src = base / "memory" / "sandboxes" / sandbox
                    if src.exists() and not (root / "memory" / "incoming" / sandbox).exists():
                        shutil.copy2(src, root / "memory" / "incoming" / sandbox)
                staged += 1 if _stage(root, name, proposal) else 0
        for path in sorted((base / "memory" / "incoming").glob("*")):
            if path.is_file() and path.name not in INCOMING_SKIP:
                target = root / "memory" / "incoming" / path.name
                if not target.exists():
                    shutil.copy2(path, target)
                    staged += path.suffix == ".md"
        overlay = _overlay(root)
        for name, entries in _overlay(base).items():
            for eid, lines in entries.items():
                kept = overlay.setdefault(name, {}).setdefault(eid, [])
                kept.extend(line for line in lines if line not in kept)
            _save_overlay(root, name, overlay[name])
        for rel, marker in (("ideas/idea-repository.md", "## ["),
                            ("ideas/exploration.md", "### "),
                            ("tension/tension-ledger.md", "### ")):
            mine = _read(root / rel)
            extra = []
            for block in _blocks(_read(base / rel), marker):
                if block.splitlines()[0] not in mine:
                    extra.append(block)
            if extra:
                _write(root / rel, mine.rstrip("\n") + "\n\n" + "\n\n".join(extra) + "\n")
    return staged, False


def _blocks(text: str, marker: str) -> list[str]:
    result, current = [], None
    for line in text.splitlines():
        if line.startswith(marker):
            if current:
                result.append("\n".join(current).strip())
            current = [line]
        elif current is not None:
            current.append(line)
    if current:
        result.append("\n".join(current).strip())
    return result


# ------------------------------------------------------------------ commands

def cmd_status(_: argparse.Namespace) -> int:
    root = ensure_store()
    info = manifest()
    counts = info.get("counts", {})
    local = sum(len(ENTRY_HEAD_RE.findall(_read(path)))
                for path in (root / "memory" / "projects").glob("*.md"))
    proposals = [path for path in (root / "memory" / "incoming").glob("*.md")
                 if path.name not in INCOMING_SKIP]
    held = sum(1 for path in proposals if "<!-- STEWARD HOLD" in _read(path))
    reviews = sum(len(lines) for entries in _overlay(root).values()
                  for lines in entries.values())
    _print_safe(f"✓ brain-zanegpt v{VERSION} · canon {info.get('snapshot_version')} · "
                f"memory {counts.get('memory', 0)} · tension {counts.get('tension', 0)} · "
                f"ideas {counts.get('ideas', 0)} · exploration {counts.get('exploration', 0)} · "
                f"sandboxes {counts.get('sandboxes', 0)}")
    _print_safe(f"  local: {local} promoted, {len(proposals)} proposal(s)"
                + (f" ({held} held)" if held else "")
                + f", {reviews} review/citation line(s) on shared canon · {root}")
    _print_safe("  remote sync: disabled (all commands are offline)")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = ensure_store()
    if args.import_path:
        return cmd_import(argparse.Namespace(path=args.import_path))
    return sync(root)


def cmd_mine_add(source: Path) -> int:
    root = ensure_store()
    if source.suffix.lower() == ".json":
        name, text = _proposal_from_json(_read_json(source))
    else:
        name, text = source.name, _read(source)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}__[a-z0-9][a-z0-9-]*\.md", name):
            name = f"{dt.date.today().isoformat()}__{_slug(source.stem)}.md"
    target = _stage(root, name, text)
    if not target:
        _print_safe("✓ already staged — nothing to add")
        return 0
    _print_safe(f"✓ staged proposal → {target}")
    _print_safe(f"  run `{cli_command()} sync` to run the steward and promote it locally")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    root = ensure_store()
    destination = Path(args.out).expanduser().resolve()
    if destination.suffix.lower() != ".zip":
        destination = destination.with_suffix(".zip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for sub in ("memory", "ideas", "tension"):
            for path in sorted((root / sub).rglob("*")):
                if path.is_file() and not path.name.endswith(".tmp"):
                    archive.write(path, path.relative_to(root).as_posix())
                    count += 1
        archive.writestr("export.json", json.dumps({
            "store_version": STORE_VERSION, "plugin_version": VERSION,
            "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": "brain-zanegpt local store only; bundled canon excluded"}) + "\n")
    _print_safe(f"✓ exported local store ({count} files) → {destination}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    root = ensure_store()
    source = Path(args.path).expanduser().resolve()
    if zipfile.is_zipfile(source):
        staged, restored = import_zip(root, source)
        if restored:
            _print_safe(f"✓ restored the export into an empty store → {root}")
            return sync(root)
    else:
        payload = _read_json(source)
        staged = 0
        for item in payload.get("entries", []):
            name, text = _proposal_from_json(item)
            staged += 1 if _stage(root, name, text) else 0
    _print_safe(f"✓ import staged {staged} proposal(s); running the steward")
    return sync(root)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--version", action="version", version=VERSION)
    commands = result.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="show canon and local-store status")
    status.set_defaults(func=cmd_status)
    sync_parser = commands.add_parser("sync", help="run the steward on local proposals")
    sync_parser.add_argument("--import", dest="import_path", metavar="EXPORT")
    sync_parser.add_argument("--verbose", action="store_true")
    sync_parser.set_defaults(func=cmd_sync)
    export = commands.add_parser("export", help="export the local store as a zip")
    export.add_argument("--out", required=True)
    export.set_defaults(func=cmd_export)
    importer = commands.add_parser("import", help="re-file an export through the steward")
    importer.add_argument("path")
    importer.set_defaults(func=cmd_import)
    return result


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] not in ("status", "sync", "export", "import") \
            and not argv[0].startswith("-"):
        root = ensure_store()
        staged = migrate_v1(root)
        if staged:
            _print_safe(f"✓ moved {staged} v1 lesson(s) into the steward's queue")
            sync(root)
        if argv[0] == "mine" and "--add" in argv:
            position = argv.index("--add")
            if position + 1 >= len(argv):
                _print_safe("✗ usage: mine --add <proposal.md|proposal.json>")
                return 2
            return cmd_mine_add(Path(argv[position + 1]).expanduser().resolve())
        if argv[0] not in DELEGATED:
            _print_safe(f"✗ unknown command '{argv[0]}' "
                        f"(try: status, sync, export, import, {', '.join(DELEGATED)})")
            return 2
        return run_brain(argv)
    root = ensure_store()
    staged = migrate_v1(root)
    if staged:
        _print_safe(f"✓ moved {staged} v1 lesson(s) into the steward's queue")
        if not argv or argv[0] != "sync":
            sync(root)
    arguments = parser().parse_args(argv)
    return int(arguments.func(arguments))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
