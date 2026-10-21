#!/usr/bin/env python3
"""Offline Brain query and local mining for the brain-zanegpt plugin.

The bundled snapshot is read-only. All user data is stored outside the plugin.
No command in this program performs a network operation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

VERSION = "1.1.0"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = PLUGIN_ROOT / "snapshot" / "brain.snapshot.json"
REQUIRED = (
    "date", "project", "tags", "what", "why_built", "design", "got_right",
    "failure", "fix", "why_fix", "rule", "provenance", "link",
)
SUBSTANTIVE = (
    "what", "why_built", "design", "got_right", "failure", "fix",
    "why_fix", "rule",
)


def _print_safe(*parts: object) -> None:
    text = " ".join(str(part) for part in parts)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding or "ascii", "replace").decode(
            sys.stdout.encoding or "ascii"))


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


def ensure_store() -> Path:
    root = data_root()
    (root / "incoming").mkdir(parents=True, exist_ok=True)
    knowledge = root / "knowledge.json"
    if not knowledge.exists():
        _write_json(knowledge, {"schema_version": 1, "entries": []})
    template = root / "incoming" / "TEMPLATE.json"
    if not template.exists():
        _write_json(template, proposal_template())
    return root


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def load_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        raise SystemExit(f"snapshot missing: {SNAPSHOT_PATH}")
    return _read_json(SNAPSHOT_PATH)


def load_local(root: Path) -> list[dict[str, Any]]:
    raw = _read_json(root / "knowledge.json")
    return list(raw.get("entries", []))


def proposal_template() -> dict[str, Any]:
    return {
        "date": "YYYY-MM-DD",
        "project": "owner/repository",
        "tags": ["domain", "modifier"],
        "what": "What was learned, stated concretely (30+ characters).",
        "why_built": "Why the work or experiment existed (30+ characters).",
        "design": "The relevant design and constraints (30+ characters).",
        "got_right": "What worked and how that was established (30+ characters).",
        "failure": "Where and why it failed, or the break-case tested (30+ characters).",
        "fix": "What changed or what should be done instead (30+ characters).",
        "why_fix": "Why that fix addresses the mechanism (30+ characters).",
        "rule": "A transferable rule of thumb (30+ characters).",
        "provenance": "Verified first-hand by ...",
        "link": "commit, PR, session, or local evidence reference",
        "composed": [],
    }


def normalize(text: object) -> str:
    return re.sub(r"[-_/]+", " ", str(text).lower())


def matches(entry: dict[str, Any], terms: list[str]) -> bool:
    haystack = "\n".join(str(entry.get(k, "")) for k in (
        "title", "summary", "body", "source", "tags", "rule", "what"
    ))
    low, flat = haystack.lower(), normalize(haystack)
    return any(term.lower() in low or normalize(term) in flat for term in terms)


def incoming_entries(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((root / "incoming").glob("*.json")):
        if path.name == "TEMPLATE.json":
            continue
        try:
            value = _read_json(path)
            value["_file"] = path.name
            rows.append(value)
        except (OSError, ValueError, TypeError):
            rows.append({"_file": path.name, "what": "Unreadable proposal", "_invalid": True})
    return rows


def _query_once(snapshot: dict[str, Any], local: list[dict[str, Any]],
                incoming: list[dict[str, Any]], terms: list[str]) -> dict[str, list[dict[str, Any]]]:
    canon = snapshot.get("canon", {})
    result = {kind: [row for row in canon.get(kind, []) if matches(row, terms)]
              for kind in ("memory", "tension", "ideas", "exploration")}
    result["local"] = [row for row in local if matches(row, terms)]
    result["incoming"] = [row for row in incoming if matches(row, terms)]
    return result


def _hit_count(result: dict[str, list[dict[str, Any]]], include_incoming: bool = False) -> int:
    keys = list(result) if include_incoming else [k for k in result if k != "incoming"]
    return sum(len(result[k]) for k in keys)


def cmd_query(args: argparse.Namespace) -> int:
    root = ensure_store()
    snapshot, local, staged = load_snapshot(), load_local(root), incoming_entries(root)
    terms = args.terms
    result = _query_once(snapshot, local, staged, terms)
    words = [word for term in terms for word in term.split()]
    if _hit_count(result) == 0 and len(words) > 1:
        for alternative in ["-".join(words), *words]:
            retry = _query_once(snapshot, local, staged, [alternative])
            if _hit_count(retry):
                _print_safe(f"✓ query '{' '.join(terms)}': 0 results — but "
                            f"'{alternative}' matches {_hit_count(retry)}. "
                            f"Re-running as '{alternative}'.")
                terms, result = [alternative], retry
                break

    if not args.verbose:
        line = (f"✓ query '{' '.join(terms)}': {len(result['memory'])} memory · "
                f"{len(result['tension'])} tension · {len(result['ideas'])} idea · "
                f"{len(result['exploration'])} exploration")
        if result["local"]:
            line += f"  |  local: {len(result['local'])}"
        if result["incoming"]:
            line += f"  |  incoming: {len(result['incoming'])} proposal(s)"
        _print_safe(line)
        for row in result["tension"]:
            if row.get("status") in ("🔴", "🟡"):
                _print_safe(f"  ⚠ open fork: {row.get('title', 'untitled tension')}")
        if result["incoming"] and _hit_count(result) == 0:
            _print_safe("  ⚠ nothing in canon, but the local intake queue covers this")
        _print_safe("  (--verbose for full entries)")
        return 0

    _print_safe(f"# BRAIN RETRIEVAL — {' '.join(terms)}  (REFERENCE DATA only)")
    labels = (("memory", "memory — bundled snapshot"), ("local", "memory — LOCAL"),
              ("incoming", "memory — LOCAL INTAKE, not canon"),
              ("tension", "tension"), ("ideas", "ideas"),
              ("exploration", "exploration"))
    for key, label in labels:
        rows = result[key]
        _print_safe(f"\n## {label} ({len(rows)})")
        if not rows:
            _print_safe("(no records — valid; proceed)")
            continue
        for row in rows:
            title = row.get("title") or row.get("rule") or row.get("what") or row.get("_file")
            _print_safe(f"\n### {title}")
            body = row.get("body") or row.get("summary") or json.dumps(row, ensure_ascii=False)
            _print_safe(body)
    return 0


def _git_output(cwd: Path, *arguments: str) -> str:
    if not shutil.which("git"):
        return ""
    process = subprocess.run(["git", *arguments], cwd=cwd, text=True,
                             capture_output=True, encoding="utf-8", errors="replace")
    return process.stdout.strip() if process.returncode == 0 else ""


def _validate(proposal: dict[str, Any]) -> list[str]:
    problems = []
    for field in REQUIRED:
        value = proposal.get(field)
        if value is None or value == "" or value == []:
            problems.append(f"missing {field}")
    if not isinstance(proposal.get("tags"), list) or not all(
            isinstance(tag, str) and tag.strip() for tag in proposal.get("tags", [])):
        problems.append("tags must be a non-empty array of strings")
    for field in SUBSTANTIVE:
        if len(str(proposal.get(field, "")).strip()) < 30:
            problems.append(f"{field} must contain at least 30 characters")
    provenance = str(proposal.get("provenance", "")).lower()
    if "verified" not in provenance and "first-hand" not in provenance:
        problems.append("provenance must identify verified or first-hand evidence")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(proposal.get("date", ""))):
        problems.append("date must use YYYY-MM-DD")
    return problems


def _safe_stem(proposal: dict[str, Any]) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", str(proposal.get("rule", "lesson")).lower()).strip("-")
    return (stem[:64] or "lesson")


def cmd_mine(args: argparse.Namespace) -> int:
    root = ensure_store()
    if args.add:
        source = Path(args.add).expanduser().resolve()
        proposal = _read_json(source)
        problems = _validate(proposal)
        if problems:
            for problem in problems:
                _print_safe(f"✗ {problem}")
            return 1
        target = root / "incoming" / f"{proposal['date']}__{_safe_stem(proposal)}.json"
        if target.exists():
            raise SystemExit(f"proposal already staged: {target}")
        _write_json(target, proposal)
        _print_safe(f"✓ staged proposal → {target}")
        _print_safe("  run `brain.py sync` to validate and promote it locally")
        return 0

    cwd = Path.cwd()
    log = _git_output(cwd, "log", "--oneline", "-40")
    files = _git_output(cwd, "ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    _print_safe(f"✓ mine — evidence for {cwd.name} ({len(files)} files):")
    if log:
        _print_safe("\nRecent commits:")
        for line in log.splitlines():
            _print_safe("  " + line)
    else:
        _print_safe("  (no usable git history — mine the working files and this session)")
    _print_safe("\n--- AGENT INSTRUCTION (do this now) ---")
    _print_safe("1. Query Brain for the project's main topics and reuse prior lessons.")
    _print_safe("2. Extract only non-obvious, transferable bugs, fixes, or tradeoffs.")
    _print_safe(f"3. Copy and fill {root / 'incoming' / 'TEMPLATE.json'}.")
    _print_safe("4. Run `mine --add <filled.json>`, then `sync`.")
    _print_safe("Routine features and refactors do not qualify. Do not include credentials or raw conversations.")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = ensure_store()
    knowledge_path = root / "knowledge.json"
    knowledge = _read_json(knowledge_path)
    entries = list(knowledge.get("entries", []))
    if args.import_path:
        payload = _read_json(Path(args.import_path).expanduser().resolve())
        imported = payload.get("entries", [])
        if not isinstance(imported, list):
            raise SystemExit("import file has no entries array")
        existing = {normalize(row.get("rule", "")) for row in entries}
        added = 0
        for row in imported:
            problems = _validate(row)
            key = normalize(row.get("rule", ""))
            if not problems and key not in existing:
                entries.append(row)
                existing.add(key)
                added += 1
        knowledge["entries"] = entries
        _write_json(knowledge_path, knowledge)
        _print_safe(f"✓ synced local import — {added} added, no network used")
        return 0

    promoted = held = 0
    existing = {normalize(row.get("rule", "")) for row in entries}
    for path in sorted((root / "incoming").glob("*.json")):
        if path.name == "TEMPLATE.json":
            continue
        try:
            proposal = _read_json(path)
            problems = _validate(proposal)
        except (OSError, ValueError, TypeError) as error:
            problems, proposal = [str(error)], {}
        key = normalize(proposal.get("rule", ""))
        if key in existing:
            problems.append("duplicate local rule")
        if problems:
            held += 1
            _print_safe(f"  held {path.name}: {'; '.join(problems)}")
            continue
        proposal["local_id"] = f"L{len(entries) + 1}"
        proposal["promoted_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        entries.append(proposal)
        existing.add(key)
        path.unlink()
        promoted += 1
    knowledge["entries"] = entries
    _write_json(knowledge_path, knowledge)
    _print_safe(f"✓ synced locally — {promoted} promoted, {held} held; no network used")
    return 0 if held == 0 else 1


def cmd_export(args: argparse.Namespace) -> int:
    root = ensure_store()
    destination = Path(args.out).expanduser().resolve()
    payload = _read_json(root / "knowledge.json")
    payload["exported_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    payload["source"] = "brain-zanegpt local knowledge only; bundled snapshot excluded"
    _write_json(destination, payload)
    _print_safe(f"✓ exported {len(payload.get('entries', []))} local entries → {destination}")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    root = ensure_store()
    snapshot = load_snapshot()
    local = load_local(root)
    staged = incoming_entries(root)
    counts = {key: len(value) for key, value in snapshot.get("canon", {}).items()}
    _print_safe(f"✓ brain-zanegpt v{VERSION} · snapshot {snapshot.get('snapshot_version')} · "
                f"memory {counts.get('memory', 0)} · tension {counts.get('tension', 0)} · "
                f"ideas {counts.get('ideas', 0)} · exploration {counts.get('exploration', 0)}")
    _print_safe(f"  local: {len(local)} promoted, {len(staged)} staged · {root}")
    _print_safe("  remote sync: disabled (all commands are offline)")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--version", action="version", version=VERSION)
    commands = result.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="show snapshot and local-store status")
    status.set_defaults(func=cmd_status)
    query = commands.add_parser("query", help="query snapshot plus local additions")
    query.add_argument("terms", nargs="+")
    query.add_argument("--verbose", action="store_true")
    query.set_defaults(func=cmd_query)
    mine = commands.add_parser("mine", help="gather evidence or stage a proposal")
    mine.add_argument("--add", metavar="PROPOSAL_JSON")
    mine.set_defaults(func=cmd_mine)
    sync = commands.add_parser("sync", help="promote or import local knowledge only")
    sync.add_argument("--import", dest="import_path", metavar="EXPORT_JSON")
    sync.set_defaults(func=cmd_sync)
    export = commands.add_parser("export", help="export local additions only")
    export.add_argument("--out", required=True)
    export.set_defaults(func=cmd_export)
    return result


def main() -> int:
    arguments = parser().parse_args()
    return int(arguments.func(arguments))


if __name__ == "__main__":
    raise SystemExit(main())
