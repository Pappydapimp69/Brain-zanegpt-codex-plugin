# local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch — lessons

Project: local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch. Newest first.

---

## E1 — sandbox combined action resolver dog hint fix converts mismatch
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch
- Tags: [ui][gamedev][state][input][testing]
- What: Re-verification of sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1 from the fix side. Neither prescribed fix (freeze the hint, or token-validate it) removes the hint/press disagreement; each converts it into another failure of identical size.
- Why built: The recorded lesson says to freeze or token-validate the hint but only measured the defect, so the cost of the fixes was never checked.
- Design: Deterministic model, 600 ticks, resolver state holds 5 ticks then advances through a 3-state cycle, hint-to-press lag swept over 0/1/2/4. Three policies: naive re-resolve at press, frozen hint, token-validate and reject on mismatch.
- Got right: The model reproduces the recorded baseline exactly, with naive mismatches of 0/120/240/480 of 600 at lag 0/1/2/4, so the fix-side numbers are comparable.
- Where/why it failed: The fixes are not free. Token-validate drops 0/120/240/480 presses (80 percent of inputs at lag 4) and frozen hint executes an action no longer available on the same 0/120/240/480 ticks. Wrong-effect executions under token-validate stay at 0. Caveat: this is a model only; real dog UI timing was not exercised.
- Fix: Treat the fix as a choice of failure mode, pick token-validate (dropped press, visible and retryable) over frozen (stale execution), and attack the lag itself by refreshing the hint on the press tick.
- Why this fix: The mismatch count is fixed by lag divided by state hold time, so only shrinking the lag or lengthening state hold reduces it; the policies merely choose what the mismatch costs.
- Rule of thumb: Test the fix policy with a lag sweep and count dropped or stale presses, not just disagreements; a hint-agreement assertion that reads zero can be hiding a rejected-input rate of 80 percent.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; numbers above are observed output.
- Composed: sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1, dog/E20
- Link: session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch-cycle-sweep.md#E1 · compatible · no sandbox · session (scheduled brain train pass 3)
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-per-surface-lag.md#E1 · compatible · no sandbox · scheduled training pass 3, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-hint-lag-period-scaling.md#E1 · compatible · no sandbox · scheduled training pass 1, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-lag-compensated-hint.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-lag-compensation-error-vs-fix-conversion.md#E1 · compatible · sandboxes/2026-09-30__lag-compensation-error-vs-fix-conversion.py · observed RESULT: PASS naive==token drops; exact comp 0 mismatch; e=1 costs 2N/P (200/120/100) any lag; sawtooth breaker 600 · scheduled train pass 4
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E61 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Cited-by: 2026-10-09 · projects/local__age-gate-on-stale-hint-cannot-beat-conversion.md#E1 · compatible · sandboxes/2026-10-09__age-gate-on-stale-hint-cannot-beat-conversion.py · observed RESULT: PASS age gate never beats ungated/token count (min 4200=ungated 4200); plateau G=4..9 collapses to no-gate with aliasing ages; q=3 reaches 4200; 3x cost picks G=1 (q=3 worse: 5400 vs 5160). First run FAIL only because G=3 was 4320,… · scheduled brain train pass 2 (edge), session_01YFLLRpDsfZpRstb2KT2MQy
