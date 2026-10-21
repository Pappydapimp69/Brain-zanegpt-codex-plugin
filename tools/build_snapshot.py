#!/usr/bin/env python3
"""Build the immutable Brain canon bundle from checked-out upstream repos.

The bundle is the upstream files themselves, not a digest: Brain's own CLI and
the memory repo's own steward run against them offline, so local lessons pass
exactly the gate shared canon passes.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "brain-zanegpt"
CANON = PLUGIN / "canon"
SNAPSHOT_VERSION = "2026.10.21.2"
UPSTREAM = {
    "brain": (ROOT / ".upstream-brain", "https://github.com/Pappydapimp69/Brain"),
    "zanegpt": (ROOT / ".upstream-zanegpt", "https://github.com/Pappydapimp69/Zanegpt"),
    "memory": (ROOT / ".upstream-memory", "https://github.com/Pappydapimp69/memory"),
    "ideas": (ROOT / ".upstream-ideas", "https://github.com/Pappydapimp69/ideas"),
    "tension": (ROOT / ".upstream-tension", "https://github.com/Pappydapimp69/Tension"),
}
# (upstream, bundle dir, files or globs). Incoming queues, letters, Git history
# and anything else not listed here stay out of the bundle.
INCLUDE = [
    ("brain", "Brain", ["bin/brain", "subjects.json", "paths.json", "train-ignore.json"]),
    ("memory", "memory", ["PITFALLS.md", "INSTRUCTIONS.md", "REVIEW-TEMPLATE.md",
                          "incoming/TEMPLATE.md", "incoming/README.md",
                          "projects/*.md", "sandboxes/*.py",
                          "scripts/steward.py", "scripts/cited_by.py",
                          "scripts/validate.py"]),
    ("ideas", "ideas", ["idea-repository.md", "exploration.md", "README.md"]),
    ("tension", "Tension", ["tension-ledger.md", "README.md"]),
]


def commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True,
        encoding="utf-8").strip()


def count(path: Path, pattern: str) -> int:
    return len(re.findall(pattern, path.read_text(encoding="utf-8"), re.M))


def main() -> None:
    for name, (path, _) in UPSTREAM.items():
        if not (path / ".git").exists():
            raise SystemExit(f"missing upstream checkout for {name}: {path}")

    if CANON.exists():
        shutil.rmtree(CANON)
    digest = hashlib.sha256()
    for upstream, target, patterns in INCLUDE:
        source = UPSTREAM[upstream][0]
        for pattern in patterns:
            matches = sorted(source.glob(pattern))
            if not matches:
                raise SystemExit(f"{upstream}: nothing matches {pattern}")
            for item in matches:
                rel = item.relative_to(source).as_posix()
                dest = CANON / target / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = item.read_bytes()
                dest.write_bytes(data)
                digest.update(f"{target}/{rel}\0".encode())
                digest.update(data)

    memory = CANON / "memory"
    counts = {
        "memory": count(memory / "PITFALLS.md", r"^- `\["),
        "tension": count(CANON / "Tension" / "tension-ledger.md", r"^### "),
        "ideas": count(CANON / "ideas" / "idea-repository.md", r"^## \["),
        "exploration": count(CANON / "ideas" / "exploration.md", r"^### "),
        "sandboxes": len(list((memory / "sandboxes").glob("*.py"))),
    }
    commits = {name: {"url": url, "commit": commit(path)}
               for name, (path, url) in UPSTREAM.items()}
    manifest = {
        "snapshot_version": SNAPSHOT_VERSION,
        "sha256": digest.hexdigest(),
        "counts": counts,
        "sources": commits,
        "notes": "Curated canon, its sandboxes, Brain's CLI and the memory steward. "
                 "No credentials, private stores, raw conversations, incoming "
                 "proposals, or Git history.",
    }
    (CANON / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
