# local/sandbox-combined-august-10-waiting-city-roll-count-audit-measures-a-cold-path — lessons

Project: local/sandbox-combined-august-10-waiting-city-roll-count-audit-measures-a-cold-path. Newest first.

---

## E1 — sandbox combined august 10 waiting city roll count audit measures a cold path
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-waiting-city-roll-count-audit-measures-a-cold-path
- Tags: [determinism][testing][state][method]
- What: A deterministic sandbox (explicit seeded LCG stream, every draw counted, no wall-clock) running a waiting-city#E9-compliant constant-roll-count decision function with and without a memoization cache, audited two ways: the unit-test-shaped audit that calls with a fresh agent each time, and the real replayed loop where agents repeat across ticks.
- Why built: waiting-city#E9 prescribes putting agent AI inside the replayed reducer and paying the tax, explicitly including a constant RNG-roll count per decision. august-10#E28 records that memoization changes call count and that for a function touching a shared sequence, call count IS behaviour. This tests whether the natural audit for waiting-city#E9's discipline actually detects an august-10#E28 cache installed beneath the decision function.
- Design: A decision function drawing a fixed 3 rolls (2 for the threat score, 1 for the tiebreak) from the authoritative sim RNG, with an optional cache on the threat-score half. Two measurements: a roll-count audit invoking the decision with a distinct fresh agent id each time (how a unit test of the function would naturally be written), and a 10-tick, 3-agent replayed loop where agent ids necessarily repeat.
- Got right: Counting draws on the shared RNG object rather than inferring roll counts from the decision function's source, so the measurement reflects actual sequence consumption — the quantity waiting-city#E9's discipline is really about.
- Where/why it failed: The constant-roll-count audit returns [3, 3, 3, 3, 3] with the cache in place, identical to the uncached run and perfectly constant — it passes cleanly, because a fresh agent id never hits the cache. In the real replayed loop the same code consumes 36 rolls instead of 90 and the authoritative decision sequence diverges, first at decision index 5, with 10 of 30 decisions differing. The audit is measuring the cold path while the discipline governs the warm one.
- Fix: Audit roll counts across REPEATED decisions for the same agent within a single RNG stream, not across fresh agents — the audit must exercise whatever caching, memoization or short-circuit path production actually takes on its second and subsequent calls. A per-decision roll-count assertion written as a unit test with distinct inputs is structurally incapable of seeing a cache.
- Why this fix: waiting-city#E9's discipline is a property of the sequence a real run consumes, but the obvious way to test "constant rolls per decision" is to call the decision function repeatedly with varied inputs, which is exactly the access pattern that defeats a cache. The discipline and its natural audit therefore diverge on the one code path that matters, and the audit's passing result is not weak evidence but actively misleading — it certifies the property precisely where it does not hold.
- Rule of thumb: A constant-roll-count audit (waiting-city#E9) written with fresh inputs per call measures a cold path and cannot see an august-10#E28-style cache beneath the decision — sandbox-confirmed the audit returns a perfect constant [3,3,3,3,3] while the real replayed loop consumes 36 rolls instead of 90 and diverges on 10 of 30 decisions; audit repeated decisions for the same agent within one stream.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/sb14/s.py) and confirmed the fresh-input audit returns [3,3,3,3,3] constant both with and without the cache, while the 10-tick 3-agent replayed loop consumes 36 vs 90 rolls with the decision sequence first diverging at index 5 and differing on 10 of 30 decisions. august-10#E28 and the-game-the-waiting-city#E9 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E28, pappydapimp69__the-game-the-waiting-city/E9
- Link: session_014mRpopK9xnhvk35tT8ozkX

