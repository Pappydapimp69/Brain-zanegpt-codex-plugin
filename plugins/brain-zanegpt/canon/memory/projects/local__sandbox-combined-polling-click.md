# local/sandbox-combined-polling-click — lessons

Project: local/sandbox-combined-polling-click. Newest first.

---

## E1 — polling state does not refresh click coordinates
- Date: 2026-07-13
- Project: local/sandbox-combined-polling-click
- Tags: [harness][gamedev][browser][testing][process]
- What: Replacing fixed real-time waits with state polling does not fix an E2E test that cached an autonomous entity's click coordinates before the wait. The harness must poll for the right moment and reread the live target position at the moment it interacts.
- Why built: `brain train` selected the high-value seam `dog + the-game-the-waiting-city`. The interaction claim was that dog#E22's "poll actual state transition, not assumed wall time" and waiting-city#E2's "reread live entity positions" are separate harness requirements. Satisfying only the timing half still leaves stale-coordinate failures.
- Design: Built `sandbox-live-poll-stale-coordinates.js`, a deterministic model with: - One autonomous NPC moving one tile per tick from `(10,4)` to `(16,4)`. - A fixed-wait harness that caches `(10,4)` and clicks after 6 ticks. - A polling harness that waits until tick 6 but still uses cached `(10,4)`. - A polling+reread harness that waits until tick 6 and reads the NPC's current `(16,4)` before clicking.
- Got right: The sandbox separates time synchronization from target localization. Both failing paths interact at the same correct tick; only one rereads the coordinate.
- Where/why it failed: Both cached-coordinate harnesses clicked `(10,4)` at tick 6 while the NPC was at `(16,4)`, so both missed. Polling the tick did not update the stale click target.
- Fix: For live-game E2E commands against moving entities, poll the game state until the command is appropriate, then query the target's current position immediately before issuing the input. Do not carry screen/world coordinates across autonomous movement.
- Why this fix: The polling+reread path clicked `(16,4)` at tick 6, matching the NPC's live position and producing a hit. The only difference from the polling-only path was where the click coordinate came from.
- Rule of thumb: Polling solves "when"; rereading solves "where." A live browser game harness usually needs both once autonomous movement exists.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-live-poll-stale-coordinates.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: fixed wait + cached coords = tick 6, NPC `16,4`, click `10,4`, hit `false`; poll state + cached coords = tick 6, NPC `16,4`, click `10,4`, hit `false`; poll state + reread coords = tick 6, NPC `16,4`, click `16,4`, hit `true`.
- Composed: dog/E22, the-game-the-waiting-city/E2
- Link: Sandbox: `sandbox-live-poll-stale-coordinates.js`

