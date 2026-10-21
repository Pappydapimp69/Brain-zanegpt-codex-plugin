# local/sandbox-symmetric-and-one-sided-agreement-share-min-term — lessons

Project: local/sandbox-symmetric-and-one-sided-agreement-share-min-term. Newest first.

---

## E1 — sandbox symmetric and one sided agreement share min term
- Date: 2026-09-30
- Project: local/sandbox-symmetric-and-one-sided-agreement-share-min-term
- Tags: [ui][input][state][gamedev][testing]
- What: Deterministic sandbox showing that the count of hints an age gate can discard as still valid follows N - 2*(N/P)*m, while the one-sided validity count follows N - (N/P)*m, with the same m = min(lag, W, P-W, P-lag).
- Why built: To re-verify from a second angle that the one-sided cost formula and the discards-valid-hints-at-cycle figures (360 at lag 3, 600 at lag 15 on P15W5) are two views of one mismatch term.
- Design: Legal(t) = t mod P < W over N=600 uses; agreement count is S(t)==S(t-lag); one-sided count is N minus uses where the hint was legal at t-lag and illegal at t. Shapes P15W5, P10W3, P12W6 at six lags each.
- Got right: Both closed forms matched the simulation exactly on all 18 cases, including 360 at lag 3 and 600 at lag 15 for P15W5, and 0 agreement at lag 6 for P12W6 where the window equals the gap.
- Where/why it failed: The factor 2 is a property of agreement (both transition edges count); applying it to one-sided legality overstates the loss, e.g. 360 instead of 480 at P15W5 lag 3.
- Fix: Choose the factor by legality type: 2 for symmetric agreement, 1 for one-sided validity, with the shared min term m and the same peak N at whole-cycle lag.
- Why this fix: Each period contributes two mismatch edges to agreement but only one to one-sided validity, so the ratio is exactly 2 for any shape.
- Rule of thumb: Agreement loss is exactly twice one-sided loss for periodic legality (same min term), so pick the factor from what a mismatch means before sizing the age gate.
- Provenance (verified/assumed): Verified first-hand by running sb/p4.py: all 18 (shape, lag) cases matched both formulas exactly, e.g. P15W5 lag 3 gives 360 versus 480.
- Composed: local__age-cutoff-roll-up/E1
- Link: scheduled training session pass 4
- Reverified: 2026-09-30 · pass · sandboxes/2026-09-30__rebuild-agreement-loss-twice-one-sided.py · observed RESULT: PASS sym=2*(N/P)*m and one-sided=(N/P)*m on all 438 (P,W,lag) with 0<=lag<=P; formula as written fails 166/166 for lag>P unless lag is reduced mod P · Own fixture: exhaustive sweep of every W from 1 to P-1 and every lag from 0 to P for P in 8, 11 and 16 with N=60P and phase offset 5, 438 cases in total; the original checked 18 cases on P15W5, P10W3 and P12W6 at six lags (read only after the run). Symmetric mismatch equalled 2*(N/P)*m and one-sided loss equalled (N/P)*m in all 438, so the factor-of-two relation holds including odd P and W above P/2. The one caveat: the min term as written includes P-lag, which goes negative for lag above P, and the formula then fails in 166 of 166 such cases; reduce lag mod P first. This does not contradict the entry, which only ever tested lags up to P. · https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E346 · compatible · sandboxes/2026-10-16__cutoff-threshold-symmetric-vs-one-sided-gate.py · observed RESULT: PASS formulas exact on 22 cells, sym thr=41 one-sided thr=42, cutting one-sided at the sym thr loses 300 · brain train auto loop 2 pass 2; session_01RbNqhLnCALyxxvjiR2t3TU
- Cited-by: 2026-10-18 · projects/local__symmetric-mismatch-is-twice-the-one-sided-invalid-count-and-lossless-cutoff-sets-its-peak.md#E1 · compatible · sandboxes/2026-10-18__symmetric-mismatch-is-twice-the-one-sided-invalid-count-and-lossless-cutoff-sets-its-peak.py · observed RESULT: PASS 330 cells, 0 symmetric mismatches, 0 formula mismatches; above-period lags 13, 14, 20, 24, 25, 36 gave 8, 16, 32, 0, 8, 0 equal to the L mod P values. · brain train auto loop 2 pass 5; session_01Q7rYJzNw1uctb9nhZsXCQx
- Cited-by: 2026-10-18 · projects/local__partial-period-window-breaks-exact-twice-ratio-but-keeps-lossless-cutoff-worst.md#E1 · compatible · sandboxes/2026-10-18__partial-period-window-breaks-exact-twice-ratio-but-keeps-lossless-cutoff-worst.py · observed RESULT: PASS 756 cells, 0 bound violations, gap 0 at whole periods and up to 7 otherwise (469 non-zero cells), cumulative peak at the lossless cutoff True. · https://claude.ai/code/session_01MRoVc2AE75bu8wwdpoV7jJ
- Cited-by: 2026-10-18 · projects/local__symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge.md#E1 · compatible · sandboxes/2026-10-18__symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge.py · observed RESULT: PASS |sym-2*one|<=L on fib, P12W5 and 20 Bernoulli seeds over lags 1..120 (violations 0/0/0); fib55 one/sym (4, 8), fib89 (3, 6); ramp rel dev 0.76 · scheduled brain train auto loop 1 pass 2; session_014AVjf81yxBZXZ5b84ovVC5
