#!/usr/bin/env python3
"""End-to-end tests: install layout, the steward gate on local lessons, reviews,
v1 migration, export/restore, and an upgrade that keeps local knowledge."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path(os.environ.get("BRAIN_ZANEGPT_PLUGIN_ROOT",
                             ROOT / "plugins" / "brain-zanegpt")).resolve()

SANDBOX = """\
def run(reset_per_enqueue):
    budget, attempts = 5, 0
    while attempts < 1000:
        attempts += 1
        if reset_per_enqueue:
            budget = 5
        budget -= 1
        if budget <= 0:
            break
    return attempts
a, b = run(True), run(False)
print("RESULT: PASS" if (a, b) == (1000, 5) else "RESULT: FAIL", f"reset={a} shared={b}")
"""

PROPOSAL = """\
## FULL ENTRY

- ID: E?
- Date: 2026-10-21
- Project: testowner/demo-app
- Tags: [queue][retry]
- What: A job retry budget that resets every time the job re-enqueues never runs out, so a poison job loops forever.
- Why built: The worker retried failed jobs to ride out transient network errors without paging anyone.
- Design: Each enqueue created a fresh retry counter keyed by the queue message, not by the logical job id.
- Got right: Transient failures did recover within one or two retries, measured in the sandbox model.
- Where/why it failed: A permanently failing job re-enqueued itself, got a new message, and its counter reset each time.
- Fix: Key the retry budget by the logical job id and persist it across re-enqueues so attempts accumulate.
- Why this fix: The loop only terminates if the counter survives the re-enqueue, which keying by job id guarantees.
- Rule of thumb: Key a retry budget to the logical job, never to the queue message, or a self-re-enqueueing failure never exhausts it.
- Provenance (verified/assumed): Verified first-hand in the sandbox: reset-per-enqueue ran to the cap, shared budget stopped at 5.
- Composed: opticon/E1
- Sandbox: 2026-10-21__retry-budget.py
- Prediction: reset-per-enqueue hits the 1000 cap; the shared budget stops at exactly 5 attempts.
- Observed: RESULT: PASS reset=1000 shared=5
- Scenarios: 1) transient failure recovers; 2) poison job with reset budget (built to break the claim); 3) poison job with shared budget
- Link: test session one

## PROPOSED INDEX LINE

`[queue][retry]` Key a retry budget to the logical job, not the queue message, or a self-re-enqueueing failure never exhausts it
"""

REVIEW = """\
## REVIEW

- Target: {target}
- Kind: audit
- Verdict: {verdict}
- Checked: Read the entry and its sandbox; the model computes the result rather than assuming it.
- Link: test review session
"""

V1_ENTRY = {
    "date": "2026-10-04", "project": "test/restart", "tags": ["testing", "persistence"],
    "what": "A local lesson remains queryable after the CLI process exits and restarts.",
    "why_built": "The plugin must preserve each user's mined knowledge across plugin upgrades.",
    "design": "The test uses an external data directory and launches a fresh Python process.",
    "got_right": "The second process reads the promoted entry without consulting plugin files.",
    "failure": "Writing additions below the installed plugin would lose them during an upgrade.",
    "fix": "Store promoted knowledge in a stable per-user data directory outside the plugin.",
    "why_fix": "The plugin cache can be replaced while the user data path remains unchanged.",
    "rule": "Persist mutable user knowledge outside immutable install artifacts and query both layers.",
    "provenance": "Verified first-hand by the end-to-end restart test.",
    "link": "tests/test_plugin.py", "composed": [],
}


def run(plugin: Path, data: Path, *args: str, cwd: Path | None = None
        ) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BRAIN_ZANEGPT_DATA"] = str(data)
    return subprocess.run([sys.executable, str(plugin / "scripts" / "brain.py"), *args],
                          cwd=cwd or ROOT, env=env, text=True, capture_output=True,
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
    for rel in ("Brain/bin/brain", "memory/scripts/steward.py", "memory/PITFALLS.md",
                "memory/incoming/TEMPLATE.md", "MANIFEST.json"):
        check((PLUGIN / "canon" / rel).is_file(), f"bundled {rel}")

    with tempfile.TemporaryDirectory(prefix="brain-zanegpt-test-") as temporary:
        tmp = Path(temporary)
        data = tmp / "user-data"
        incoming = data / "memory" / "incoming"

        status = run(PLUGIN, data, "status")
        check(status.returncode == 0 and "remote sync: disabled" in status.stdout, status.stdout + status.stderr)

        query = run(PLUGIN, data, "query", "reachability")
        check(query.returncode == 0 and "query 'reachability'" in query.stdout
              and "memory" in query.stdout, query.stdout + query.stderr)

        # a broad term is capped to the most relevant hits, not the whole canon
        broad = run(PLUGIN, data, "query", "ui", "--verbose")
        check(broad.returncode == 0 and len(broad.stdout) < 40000
              and "most relevant hits only" in broad.stdout, f"{len(broad.stdout)} bytes")
        every = run(PLUGIN, data, "query", "reachability", "--verbose", "--all")
        check(every.returncode == 0 and "most relevant hits only" not in every.stdout
              and "--all" not in every.stdout.split("\n", 1)[0], every.stdout[:300])

        mine = run(PLUGIN, data, "mine", cwd=tmp)
        check(mine.returncode == 0 and "AGENT INSTRUCTION" in mine.stdout
              and "PROPOSAL SCHEMA" in mine.stdout and str(incoming.as_posix()) in mine.stdout,
              mine.stdout + mine.stderr)

        # a sandbox-backed lesson composing a shared entry passes the real steward
        (incoming / "2026-10-21__retry-budget.py").write_text(SANDBOX, encoding="utf-8")
        (incoming / "2026-10-21__retry-budget.md").write_text(PROPOSAL, encoding="utf-8")
        synced = run(PLUGIN, data, "sync")
        check(synced.returncode == 0 and "1 promoted" in synced.stdout
              and "no network used" in synced.stdout, synced.stdout + synced.stderr)
        local_file = data / "memory" / "projects" / "testowner__demo-app__local.md"
        check(local_file.is_file() and "## E1" in local_file.read_text(encoding="utf-8"), "local project file")
        check((data / "memory" / "sandboxes" / "2026-10-21__retry-budget.py").is_file(), "sandbox kept")
        overlay = (data / "memory" / "overlay" / "pappydapimp69__opticon.md").read_text(encoding="utf-8")
        check("Cited-by:" in overlay and "testowner__demo-app__local.md#E1" in overlay, overlay)

        # the same rule again is a duplicate: held, visible, not promoted
        duplicate = PROPOSAL.replace("testowner/demo-app", "testowner/other").replace(
            "- Sandbox: 2026-10-21__retry-budget.py\n", "")
        (incoming / "2026-10-21__retry-again.md").write_text(duplicate, encoding="utf-8")
        held = run(PLUGIN, data, "sync")
        check(held.returncode == 1 and "1 held" in held.stdout and "dedup" in held.stdout, held.stdout)
        check("STEWARD HOLD" in (incoming / "2026-10-21__retry-again.md").read_text(encoding="utf-8"), "hold block")
        (incoming / "2026-10-21__retry-again.md").unlink()

        # reviews: one on the local lesson, one on a shared entry
        (incoming / "2026-10-21__review-local.md").write_text(REVIEW.format(
            target="projects/testowner__demo-app__local.md#E1", verdict="pass"), encoding="utf-8")
        (incoming / "2026-10-21__review-shared.md").write_text(REVIEW.format(
            target="projects/pappydapimp69__opticon.md#E1", verdict="modeled"), encoding="utf-8")
        reviewed = run(PLUGIN, data, "sync")
        check(reviewed.returncode == 0 and "2 promoted" in reviewed.stdout, reviewed.stdout + reviewed.stderr)
        check("- Audited:" in local_file.read_text(encoding="utf-8"), "local review applied")
        overlay = (data / "memory" / "overlay" / "pappydapimp69__opticon.md").read_text(encoding="utf-8")
        check("- Audited:" in overlay and "modeled" in overlay, overlay)

        # a fresh process sees the lesson, its tier, and the shared review
        restarted = run(PLUGIN, data, "query", "retry", "--verbose")
        check(restarted.returncode == 0 and "memory — LOCAL (1)" in restarted.stdout
              and "[audited]" in restarted.stdout, restarted.stdout + restarted.stderr)
        trained = run(PLUGIN, data, "train", "audit")
        check(trained.returncode == 0 and str(incoming.as_posix()) in trained.stdout, trained.stdout)

        # export, then restore into an empty store: byte-identical
        export_path = tmp / "export.zip"
        exported = run(PLUGIN, data, "export", "--out", str(export_path))
        check(exported.returncode == 0 and export_path.is_file(), exported.stdout + exported.stderr)
        restored = tmp / "restored"
        imported = run(PLUGIN, restored, "import", str(export_path))
        check(imported.returncode == 0 and "restored" in imported.stdout, imported.stdout + imported.stderr)
        check((restored / "memory" / "projects" / local_file.name).read_text(encoding="utf-8")
              == local_file.read_text(encoding="utf-8"), "restore is exact")

        # v1 store: moved into the steward's queue and promoted, backup kept
        legacy = tmp / "legacy"
        legacy.mkdir()
        (legacy / "knowledge.json").write_text(json.dumps(
            {"schema_version": 1, "entries": [V1_ENTRY]}), encoding="utf-8")
        migrated = run(PLUGIN, legacy, "query", "immutable")
        check(migrated.returncode == 0 and "1 promoted" in migrated.stdout
              and "local: 1 memory" in migrated.stdout, migrated.stdout + migrated.stderr)
        check((legacy / "legacy-v1" / "knowledge.json").is_file(), "v1 backup kept")

        # merge an export into a non-empty store: re-filed through the steward
        merged = run(PLUGIN, legacy, "import", str(export_path))
        check("1 promoted" in merged.stdout, merged.stdout + merged.stderr)
        check(not re.search(r"^- Audited:", (legacy / "memory" / "projects" / local_file.name)
                            .read_text(encoding="utf-8"), re.M), "merge re-earns reviews")

        # upgrade: shared canon gains an entry; local lessons and overlays survive
        upgraded = tmp / "upgraded-plugin"
        shutil.copytree(PLUGIN, upgraded)
        shared = upgraded / "canon" / "memory" / "projects" / "pappydapimp69__opticon.md"
        text = shared.read_text(encoding="utf-8")
        head, _, tail = text.partition("\n---\n")
        shared.write_text(f"{head}\n---\n\n## E999 — upstream addition\n- Date: 2026-10-22\n\n"
                          f"{tail.lstrip()}", encoding="utf-8")
        meta = json.loads((upgraded / "canon" / "MANIFEST.json").read_text(encoding="utf-8"))
        meta["sha256"] = "upgraded"
        (upgraded / "canon" / "MANIFEST.json").write_text(json.dumps(meta), encoding="utf-8")
        after = run(upgraded, data, "query", "retry", "--verbose")
        check("memory — LOCAL (1)" in after.stdout and "[audited]" in after.stdout, after.stdout)
        view = (data / "view" / "memory" / "projects" / "pappydapimp69__opticon.md").read_text(encoding="utf-8")
        check("## E999" in view and "testowner__demo-app__local.md#E1" in view, "overlay after upgrade")

    print("PASS: layout, steward gate, dedup hold, reviews, tiers, train, export/restore, "
          "v1 migration, merge, upgrade persistence, capped verbose")


if __name__ == "__main__":
    main()
