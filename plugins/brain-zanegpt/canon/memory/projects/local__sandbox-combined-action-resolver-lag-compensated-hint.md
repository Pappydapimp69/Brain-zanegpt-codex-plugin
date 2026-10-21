# local/sandbox-combined-action-resolver-lag-compensated-hint — lessons

Project: local/sandbox-combined-action-resolver-lag-compensated-hint. Newest first.

---

## E1 — sandbox lag compensated hint error bound
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-lag-compensated-hint
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox of a lag-compensated hint that shows the state predicted at tick t plus an estimated lag, tested against the recorded claim that freeze, token and re-resolve policies only relabel the stale presses.
- Why built: Two recorded lessons (fix-converts-mismatch and period-scaling) say no press policy removes the hint and press disagreement; a prediction-side fix acts on the hint instead of the press and was untested.
- Design: Deterministic, no RNG. State is (t // P) % 4 over 600 ticks at P5 and P7. The press lands at t plus true lag, lags 0/1/2/4. The hint shows the state at t plus estimate; estimates tried are 0, lag minus 1, exact, and lag plus 1. Mismatch counts hint versus press-time state.
- Got right: With an exact estimate the mismatch is 0 at every lag and both periods, while the uncompensated hint reproduces the recorded 0/120/240/480 at P5 and 0/85/170/342 at P7.
- Where/why it failed: An estimate off by one tick in either direction costs 120 at P5 and 85 to 86 at P7, whatever the lag size, so compensation trades a lag-proportional error for an error-proportional one; a lag of 0 with an estimate of 1 also breaks a perfect hint.
- Fix: Compensate the hint by measured lag per surface and re-measure it continuously; keep a press-time validity check for the ticks where the estimate is off.
- Why this fix: Mismatch depends on the estimate error times the boundary rate 600/P, so shrinking the error from the lag itself to the jitter around it removes most of the count, and it has to be measured because it is the only input.
- Rule of thumb: The stale-hint budget is lag/period only for an uncompensated hint; a predicted hint's budget is estimate error over period, so log estimate error and never over-compensate a zero-lag surface.
- Provenance: Verified first-hand by running the Python sandbox (sb/p3.py) and observing the counts listed above; lag was fixed per run, so jitter was modelled only as a constant error.
- Composed: sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch/E1, sandbox-combined-action-resolver-hint-lag-period-scaling/E1
- Link: session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-lag-compensation-error-vs-fix-conversion.md#E1 · compatible · sandboxes/2026-09-30__lag-compensation-error-vs-fix-conversion.py · observed RESULT: PASS naive==token drops; exact comp 0 mismatch; e=1 costs 2N/P (200/120/100) any lag; sawtooth breaker 600 · scheduled train pass 4
