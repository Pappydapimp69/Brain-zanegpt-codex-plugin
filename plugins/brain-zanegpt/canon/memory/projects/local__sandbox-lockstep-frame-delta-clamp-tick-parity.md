# local/sandbox-lockstep-frame-delta-clamp-tick-parity — lessons

Project: local/sandbox-lockstep-frame-delta-clamp-tick-parity. Newest first.

---

## E1 — sandbox lockstep delta clamp breaks tick parity
- Date: 2026-09-29
- Project: local/sandbox-lockstep-frame-delta-clamp-tick-parity
- Tags: [gamedev][determinism][architecture][testing]
- What: Composed lockstep#E6 (cap the max frame delta so a stall does not miss collisions) with the integer-time fixed-step loop lesson (equal-total frame schedules give equal tick counts) and checked what the clamp does to tick parity between two peers.
- Why built: The brain and lockstep systems had never been exercised together, and the frame-delta clamp was recorded only as a collision fix, with no check of what it does to a deterministic replay or lockstep tick count.
- Design: Deterministic, no RNG. Integer time with a 16-unit tick and 16000 units of wall time. One peer runs a smooth 16-unit frame schedule; the other stalls every 20th frame by 100, 250 or 1000 units. Three policies: no cap, clamp of the frame delta to 50, and a cap of 3 ticks per frame with the remainder kept in the accumulator and drained at the end.
- Got right: With no cap and with the step cap that keeps the remainder, both peers finished on 1000 ticks at every stall size. The delta clamp gave divergence of 122, 358 and 713 ticks for stalls of 100, 250 and 1000.
- Where/why it failed: The delta clamp discards the clamped time, so the stalled peer simulates less game time than the wall clock and its tick count depends on its own stall pattern. The lockstep#E6 clamp is safe for a single-player sim but silently breaks replay and lockstep parity.
- Fix: For any loop that must stay tick-count-deterministic, cap catch-up steps per frame and keep the leftover time in the accumulator instead of clamping the delta. This sandbox drained the leftover only at the end, so the mid-run lag of the capped peer was not measured.
- Why this fix: Keeping the remainder preserves total simulated time, so the tick count depends only on total elapsed time and not on how frames were scheduled.
- Rule of thumb: A frame-delta clamp trades tick parity for stall safety; when replay or lockstep matters, cap steps per frame and carry the remainder instead, and assert equal tick counts across a stalled and a smooth schedule.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the divergence figures are observed output. Mid-run lag under the step cap and behavior in a networked game were not tested.
- Composed: lockstep/E6, local/sandbox-combined-game-loop/E2, the-game-prologue/E24
- Link: session (scheduled brain train pass 4)
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E248 · compatible · sandboxes/2026-10-14__seeded-rng-state-words-save-exact-and-o1-but-draw-order-and-dropped-ticks-desync.py · observed RESULT: PASS state-words save exact (1 step vs 50000 replay); clamp ticks 5 vs 10, stalled client holds a prefix only; swapped draw order reassigns values to systems. · scheduled brain train auto loop 2 pass 1; session_01EU6f7a12wCvzUSXEbn87pv
