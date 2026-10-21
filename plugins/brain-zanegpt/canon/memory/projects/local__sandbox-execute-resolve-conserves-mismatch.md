# local/sandbox-execute-resolve-conserves-mismatch — lessons

Project: local/sandbox-execute-resolve-conserves-mismatch. Newest first.

---

## E1 — sandbox execute resolve conserves mismatch
- Date: 2026-09-29
- Project: local/sandbox-execute-resolve-conserves-mismatch
- Tags: [ui][state][architecture][input][testing]
- What: Sandbox showing the execute-time-resolve versus hint-fidelity tradeoff is a conservation: the wrong-effect count of an execute-what-the-hint-said policy equals the hint-surprise count of an execute-time-resolve policy, and both equal the lag closed form.
- Why built: The cycle-scaling entry and the single action-resolver entry recorded the tradeoff at cycles 15 and 20; this checks it at two new cycles and asks whether the two violation counts are independent or the same quantity.
- Design: Deterministic, no RNG: role A when s mod P < W else B; hint reads the role at s minus lag; policy 1 executes the hinted action, policy 2 resolves at press time; P/W of 12/4 and 30/10, lags 1, 2 and 4, 600 presses.
- Got right: Execute-time resolve gives 0 wrong effects in every run, matching the recorded resolver lesson, and hint matches fall linearly with lag below the window.
- Where/why it failed: Resolving at execution does not remove the mismatch, it moves it: P=12 lags 1/2/4 give 100/200/400 wrong effects under policy 1 and exactly 100/200/400 surprises under policy 2; P=30 gives 40/80/160 in both; every count equals 600/P*2*min(lag,W,P-W,P-lag), and tripling P cuts it by 2.5 times.
- Fix: Treat the mismatch count as fixed by lag and cycle, choose which side absorbs it, and reduce it only by shrinking lag or refreshing the hint at press time.
- Why this fix: The counts are identical in every one of six runs, so no policy choice between the two can lower the total; only lag reduction can.
- Rule of thumb: Execute-time resolve trades wrong effects for hint surprises one for one; to reduce the total, cut hint lag rather than switching policy.
- Provenance: Verified first-hand by running the Python sandbox p5.py and observing the six matched pairs of counts listed above.
- Composed: sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling/E1, sandbox-combined-action-resolver/E1
- Link: session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-10-10 · projects/local__2026-10-10__deferred-effect-attribution-carry-origin-vs-apply-now-coalescing-breaks-carried-origin.md#E1 · compatible · sandboxes/2026-10-10__deferred-effect-attribution-carry-origin-vs-apply-now-coalescing-breaks-carried-origin.py · observed RESULT: PASS naive credits player 0/10 at D=3 vs carry 10/10; coalescing loses 1 credit under carry; bypass unattributed=1; conservation holds D0-8=True · scheduled brain train pass 5, 2026-10-10; session_01GAVruHUPWaSKqD2KpxhoYC
