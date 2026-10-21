# local/sandbox-lockstep-delta-cap-trades-tunneling-for-sim-lag — lessons

Project: local/sandbox-lockstep-delta-cap-trades-tunneling-for-sim-lag. Newest first.

---

## E1 — sandbox lockstep delta cap trades tunneling for sim lag
- Date: 2026-09-29
- Project: local/sandbox-lockstep-delta-cap-trades-tunneling-for-sim-lag
- Tags: [phaser][physics][timing][testing]
- What: Sandbox measuring what lockstep#E6's max-frame-delta cap costs: it removes missed collisions after a stall but makes simulation time fall behind wall-clock time by the stalled amount.
- Why built: Untested seam brain + lockstep; lockstep#E6 says cap the delta, seven#E8 warns that a capped delta stretches effects, and nothing recorded quantifies both sides together.
- Design: Deterministic loop, no RNG: object at 400 px/s, thin wall at x 500-510, discrete overlap test each step, 16 ms frames with one stall of 16/100/200/400 ms every 20 to 44 frames (25 phase offsets); cap none vs 20 ms.
- Got right: With the cap, missed collisions are 0/25 at every stall length; without it they are 0, 3, 5 and 8 of 25 at stalls 16, 100, 200 and 400 ms.
- Where/why it failed: The cap discards the excess time: worst-case wall-minus-sim lag is 0 ms uncapped but 320, 720 and 1520 ms capped at stalls 100, 200 and 400, so anything timed by the sim runs late after each stall.
- Fix: Keep the cap for collision safety, but drive UI or wall-clock effects from performance.now, or use a fixed-step accumulator that catches up in several capped sub-steps.
- Why this fix: The cap protects one invariant (no tunneling) by breaking another (sim time equals wall time); separating the two clocks lets each hold.
- Rule of thumb: A delta cap is a trade, not a free fix: count both missed collisions and accumulated sim lag across stall lengths, and never time wall-clock effects off the capped clock.
- Provenance: Verified first-hand by running the Python sandbox (s4.py) and observing the miss and lag numbers listed above.
- Composed: lockstep/E6, seven/E8
- Link: session_01AJo9NVvaQuzD3JbJDk6P3B

- Audited: 2026-10-15 · modeled · Read the entry; its sandbox (s4.py) was not shipped, so the counts cannot be re-run from canon. Q1: from the Design the model does compute (discrete overlap test per step, stalls placed at 25 offsets), and the lag numbers are internally consistent: with a 20 ms cap each stall loses (stall - 20) ms, and 320, 720 and 1520 ms are exactly 4 stalls of 80, 180 and 380 ms, so the worst-case lag is a count of stalls times the excess, set by how many stalls the run contains rather than discovered. The miss counts (0, 3, 5, 8 of 25) depend on the start position and on which offsets overlap the crossing, which the entry does not state. Q2: the Rule (a delta cap trades missed collisions for sim lag; never time wall-clock effects off the capped clock) is what the two measured sides support. Q3: the claim is about a Phaser game loop (lockstep E6, tagged phaser) tested on a hand-written Python loop, so the tier is modeled. My own 1-D sandbox this session (particle speed cap per tick) agrees on the mechanism: a fixed-step accumulator with a max-steps clamp avoided tunnelling on a 250 ms hitch, which is the entry's suggested fix. To raise it: ship s4.py and state the start position. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 3 (audit), 2026-10-15
- Cited-by: 2026-10-04 · projects/pappydapimp69__brainwork.md#E377 · compatible · sandboxes/2026-10-04__delta-cap-starves-carry-cooldown-after-stall.py · observed RESULT: FAIL uncapped=101 cap50=87 lost=14 lag_us=1400000 cap500=101 lag500=0; double stalls cap50=69 lost=32 lag_us=3150000. · scheduled brain train pass 2
