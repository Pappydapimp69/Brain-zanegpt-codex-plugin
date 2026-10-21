# local/sandbox-age-gate-validity-combined-aliasing — lessons

Project: local/sandbox-age-gate-validity-combined-aliasing. Newest first.

---

## E1 — sandbox age gate validity combined aliasing
- Date: 2026-09-30
- Project: local/sandbox-age-gate-validity-combined-aliasing
- Tags: [game-design][ui][input][state][gamedev][testing]
- What: Deterministic sandbox comparing three stale-hint policies for a lagged action resolver: age gate only, validity fallback only, and age filter plus validity fallback combined.
- Why built: Two recorded lessons (age-gate vs validity fallback tradeoff; age-tag staleness detection) were single-source edges; re-verify them from a new angle with one model.
- Design: 10-state cycle, 600 ticks, threshold 2, two legal actions per state, hint lag swept 1,2,3,5,10,20; no RNG, no timing. Counts invalid executions and fidelity (action equals ideal).
- Got right: Age gate alone executes invalid actions at lag 1 and 2 (599 of 600) because age passes yet the hint is wrong, and loses all fidelity above threshold (0/600) via no-op. Validity fallback alone holds at lag 1-2 (600/600) but at lag 3 aliases to 3/600 fidelity since old actions are often still legal.
- Where/why it failed: Each single guard fails in the other's regime; validity is blind to staleness that aliases legal, age is blind to wrongness below threshold.
- Fix: Combined policy: if age exceeds threshold re-derive from current state, else if the action is not legal re-derive; result 0 invalid and 600/600 fidelity at every lag tested.
- Why this fix: Age tag catches staleness independent of hint-vs-state agreement, and validity catches wrong hints inside the age window, so their failure sets do not overlap.
- Rule of thumb: Filter by age to detect staleness, guard by validity for correctness, and on either trigger re-derive from live state rather than no-op or replay the stale hint.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; observed numbers above (lag1 age inv 599 fid 1; lag3 valid fid 3; combined 600/600 all lags).
- Composed: local__age-cutoff-roll-up/E1, sandbox-combined-action-resolver-age-tag-staleness/E1
- Link: session
- Cited-by: 2026-09-30 · projects/local__sandbox-age-validity-aliasing-fallback-tradeoff.md#E1 · compatible · sandboxes/2026-09-30__age-validity-aliasing-fallback-tradeoff.py · observed RESULT: PASS combined policy 0 invalid at all 5 lags; at whole-cycle lags validity-only is (0 redo,0 invalid) while age-only pays 600 redos. · scheduled brain train pass 2
- Cited-by: 2026-09-30 · projects/pappydapimp69__brain.md#E69 · compatible · sandboxes/2026-09-30__age-vs-validity-cost-crossover-lag-sweep.py · observed RESULT: PASS violations 0 of 28152; validity beats age gate above threshold at both whole-cycle and non-whole-cycle lags; P15W5 lag 8: 40 invalid versus 120 rejected. · scheduled brain train pass 3
