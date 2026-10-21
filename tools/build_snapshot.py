#!/usr/bin/env python3
"""Build the immutable public Brain snapshot from checked-out upstream repos."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "brain-zanegpt"
UPSTREAM = {
    "brain": (ROOT / ".upstream-brain", "https://github.com/Pappydapimp69/Brain"),
    "zanegpt": (ROOT / ".upstream-zanegpt", "https://github.com/Pappydapimp69/Zanegpt"),
    "memory": (ROOT / ".upstream-memory", "https://github.com/Pappydapimp69/memory"),
    "ideas": (ROOT / ".upstream-ideas", "https://github.com/Pappydapimp69/ideas"),
    "tension": (ROOT / ".upstream-tension", "https://github.com/Pappydapimp69/Tension"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def blocks(text: str, marker: str) -> list[str]:
    result: list[str] = []
    current: list[str] | None = None
    for line in text.splitlines():
        if line.startswith(marker):
            if current:
                result.append("\n".join(current).strip())
            current = [line]
        elif current is not None:
            if line.startswith("## ") and not line.startswith(marker):
                result.append("\n".join(current).strip())
                current = None
            else:
                current.append(line)
    if current:
        result.append("\n".join(current).strip())
    return result


def memory_index(text: str) -> list[str]:
    result: list[str] = []
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("- `["):
            if current:
                result.append(current)
            current = line
        elif current and line.startswith("  "):
            current += " " + line.strip()
        else:
            if current:
                result.append(current)
            current = None
    if current:
        result.append(current)
    return result


def memory_details(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / "projects").glob("*.md")):
        for block in blocks(read(path), "## E"):
            match = re.match(r"## (E\d+)\b", block)
            if match:
                result[f"{path.name}#{match.group(1)}"] = block
    return result


def status(block: str) -> str:
    marks = ("🔴", "🟡", "🟢", "⚪")
    lines = block.splitlines()
    lean = [line for line in lines if re.match(r"\s*Lean\s*:", line)]
    for line in lean[:1] + lines[:1]:
        hits = [(line.find(mark), mark) for mark in marks if mark in line]
        if hits:
            return min(hits)[1]
    return next((mark for mark in marks if mark in block), "")


def first_line(block: str) -> str:
    return block.splitlines()[0].lstrip("# ").strip()


def commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True,
        encoding="utf-8").strip()


def main() -> None:
    for name, (path, _) in UPSTREAM.items():
        if not (path / ".git").exists():
            raise SystemExit(f"missing upstream checkout for {name}: {path}")

    memory_root = UPSTREAM["memory"][0]
    details = memory_details(memory_root)
    memory = []
    for line in memory_index(read(memory_root / "PITFALLS.md")):
        match = re.search(r"projects/([^\s#`]+\.md)#(E\d+)", line)
        source = f"projects/{match.group(1)}#{match.group(2)}" if match else "PITFALLS.md"
        key = f"{match.group(1)}#{match.group(2)}" if match else ""
        memory.append({
            "title": source,
            "summary": line,
            "body": details.get(key, line),
            "source": source,
        })

    ideas_root = UPSTREAM["ideas"][0]
    idea_rows = [{"title": first_line(block), "body": block,
                  "source": "ideas/idea-repository.md"}
                 for block in blocks(read(ideas_root / "idea-repository.md"), "## [")]
    exploration_rows = [{"title": first_line(block), "body": block,
                         "source": "ideas/exploration.md"}
                        for block in blocks(read(ideas_root / "exploration.md"), "### ")]
    tension_root = UPSTREAM["tension"][0]
    tension_rows = [{"title": first_line(block), "body": block,
                     "status": status(block), "source": "Tension/tension-ledger.md"}
                    for block in blocks(read(tension_root / "tension-ledger.md"), "### ")]

    commits = {name: {"url": url, "commit": commit(path)}
               for name, (path, url) in UPSTREAM.items()}
    snapshot = {
        "schema_version": 1,
        "snapshot_version": "2026.10.21.1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "read_only": True,
        "privacy": {
            "included": "public curated canon only",
            "excluded": [
                "credentials", "private local Brain stores", "raw conversations",
                "Git history", "incoming queues", "sandboxes",
            ],
        },
        "sources": commits,
        "canon": {
            "memory": memory,
            "tension": tension_rows,
            "ideas": idea_rows,
            "exploration": exploration_rows,
        },
    }
    output_dir = PLUGIN / "snapshot"
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = output_dir / "brain.snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False,
                                        separators=(",", ":")) + "\n", encoding="utf-8")
    digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    manifest = {
        "snapshot_version": snapshot["snapshot_version"],
        "sha256": digest,
        "counts": {key: len(value) for key, value in snapshot["canon"].items()},
        "sources": commits,
        "notes": "Public curated canon only; no credentials, private stores, raw conversations, incoming proposals, or sandboxes.",
    }
    (output_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
