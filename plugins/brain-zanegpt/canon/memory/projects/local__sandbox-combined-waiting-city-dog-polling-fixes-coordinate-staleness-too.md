# local/sandbox-combined-waiting-city-dog-polling-fixes-coordinate-staleness-too — lessons

Project: local/sandbox-combined-waiting-city-dog-polling-fixes-coordinate-staleness-too. Newest first.

---

## E1 — sandbox combined waiting city dog polling fixes coordinate staleness too
- Date: 2026-08-29
- Project: local/sandbox-combined-waiting-city-dog-polling-fixes-coordinate-staleness-too
- Tags: [testing][harness][gamedev][determinism]
- What: A deterministic sandbox (fixed NPC trajectory, no RNG, no wall-clock) running a fixed-coordinate scripted e2e driver and a polling driver against the same world before and after an NPC gains autonomous patrol movement.
- Why built: waiting-city#E2 records that a browser e2e test driving the live game with a fixed-coordinate scripted command sequence breaks the instant any entity gains real-time autonomous movement. dog#E22 records that a headless rAF slowdown ratio is not a stable constant and prescribes polling for the actual state transition rather than computing a fixed real-time wait. These are filed as separate hazards — one about coordinates, one about timing — so this tests whether they are actually one error with one remedy.
- Design: An NPC at a fixed position pre-feature and on a modulo-7 patrol post-feature. A scripted driver clicks the hardcoded coordinate at a given tick; a polling driver waits up to a bounded number of ticks for the NPC to actually occupy that coordinate. Both drivers run against both worlds.
- Got right: Bounding the polling driver's wait rather than letting it search indefinitely, so its success reflects genuinely reaching the required state within a realistic window rather than an unbounded search that would succeed trivially.
- Where/why it failed: The scripted driver is 6/6 against the static world and drops to 1/6 once the NPC patrols — waiting-city#E2's regression, occurring entirely in the test rather than the game. The polling driver recovers 6/6 on the identical autonomous world.
- Fix: Adopt dog#E22's polling discipline as the general e2e driver pattern rather than as a headless-timing-specific remedy, and treat any hardcoded coordinate or tick in a driver as the same defect regardless of whether the observed symptom is flake or a hard miss.
- Why this fix: Both hazards are one error stated twice — a test asserting WHEN something is true rather than waiting for WHAT it needs. dog#E22's remedy is filed against timing flakiness because that is where it was found, which makes it easy to scope narrowly to headless environments and miss that the same driver shape also fails deterministically when world state gains autonomy.
- Rule of thumb: dog#E22's poll-for-the-state discipline, filed as a headless timing fix, is also the structural remedy for waiting-city#E2's fixed-coordinate staleness — sandbox-confirmed a scripted driver falling from 6/6 to 1/6 once an NPC gains patrol movement while the polling driver holds 6/6; both are a test asserting WHEN instead of waiting for WHAT.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b6/l18.py) and confirmed the scripted driver scores 6/6 static and 1/6 autonomous while the polling driver scores 6/6 in both worlds. the-game-the-waiting-city#E2 and dog#E22 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-the-waiting-city/E2, pappydapimp69__dog/E22
- Link: session_014mRpopK9xnhvk35tT8ozkX

