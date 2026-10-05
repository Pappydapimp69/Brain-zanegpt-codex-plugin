#!/usr/bin/env python3
"""End-to-end tests for install layout, query, mine, sync, and restart persistence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path(os.environ.get("BRAIN_ZANEGPT_PLUGIN_ROOT",
                             ROOT / "plugins" / "brain-zanegpt")).resolve()
CLI = PLUGIN / "scripts" / "brain.py"


def run(data: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BRAIN_ZANEGPT_DATA"] = str(data)
    return subprocess.run([sys.executable, str(CLI), *args], cwd=cwd or ROOT,
                          env=env, text=True, capture_output=True,
                          encoding="utf-8", errors="replace")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    manifest = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    check(manifest["name"] == "brain-zanegpt", "plugin identity")
    check(manifest["$schema"].endswith("/1.0.0/plugin.schema.json"), "portable schema")
    check(marketplace["plugins"][0]["source"]["path"] == "./plugins/brain-zanegpt", "marketplace path")
    check((PLUGIN / "skills" / "brain-zanegpt" / "SKILL.md").is_file(), "skill discovery")

    with tempfile.TemporaryDirectory(prefix="brain-zanegpt-test-") as temporary:
        data = Path(temporary) / "user-data"
        status = run(data, "status")
        check(status.returncode == 0 and "remote sync: disabled" in status.stdout, status.stderr)

        query = run(data, "query", "reachability")
        check(query.returncode == 0 and "memory" in query.stdout and "query 'reachability'" in query.stdout, query.stdout)

        mine = run(data, "mine")
        check(mine.returncode == 0 and "AGENT INSTRUCTION" in mine.stdout, mine.stdout)

        proposal = {
            "date": "2026-10-04",
            "project": "test/restart",
            "tags": ["testing", "persistence"],
            "what": "A local lesson remains queryable after the CLI process exits and restarts.",
            "why_built": "The plugin must preserve each user's mined knowledge across plugin upgrades.",
            "design": "The test uses an external data directory and launches a fresh Python process.",
            "got_right": "The second process reads the promoted entry without consulting plugin files.",
            "failure": "Writing additions below the installed plugin would lose them during an upgrade.",
            "fix": "Store promoted knowledge in a stable per-user data directory outside the plugin.",
            "why_fix": "The plugin cache can be replaced while the user data path remains unchanged.",
            "rule": "Persist mutable user knowledge outside immutable install artifacts and query both layers.",
            "provenance": "Verified first-hand by the end-to-end restart test.",
            "link": "tests/test_plugin.py",
            "composed": [],
        }
        proposal_path = Path(temporary) / "proposal.json"
        proposal_path.write_text(json.dumps(proposal), encoding="utf-8")
        staged = run(data, "mine", "--add", str(proposal_path))
        check(staged.returncode == 0 and "staged proposal" in staged.stdout, staged.stdout + staged.stderr)
        synced = run(data, "sync")
        check(synced.returncode == 0 and "1 promoted" in synced.stdout and "no network used" in synced.stdout, synced.stdout)

        restarted = run(data, "query", "immutable install artifacts", "--verbose")
        check(restarted.returncode == 0 and "test/restart" in restarted.stdout, restarted.stdout)

        export_path = Path(temporary) / "export.json"
        exported = run(data, "export", "--out", str(export_path))
        check(exported.returncode == 0 and export_path.is_file(), exported.stdout)
        exported_json = json.loads(export_path.read_text(encoding="utf-8"))
        check(len(exported_json["entries"]) == 1, "local export count")

    print("PASS: manifest, marketplace, query, mining, local sync, export, and restart persistence")


if __name__ == "__main__":
    main()
