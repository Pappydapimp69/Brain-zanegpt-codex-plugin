# local/sidecar-drift-silently-drops-ipm-d1-contender — lessons

Project: local/sidecar-drift-silently-drops-ipm-d1-contender. Newest first.

---

## E1 — sidecar drift silently drops ipm d1 contender
- Date: 2026-10-17
- Project: local/sidecar-drift-silently-drops-ipm-d1-contender
- Tags: [game-ads][testing][sandbox][process]
- What: A hand-typed label-to-id sidecar feeding an IPM times D1 recut ranking silently dropped the true best variant after upstream renamed its label; the ranking ran on 5 of 6 variants with no error, and the tracked-versus-ranked count (6 vs 5) was the only tripwire.
- Why built: To test whether the sidecar-drift lesson from collective-reference composes with the IPM-times-D1 ranking lesson, and whether the film explainer's tracked-versus-open count labelling is the cheap detector.
- Design: Six toy variants with true install rate and D1 retention; the best IPM-times-D1 variant (v4) has its label renamed upstream. Compare a stale hand-typed sidecar against a map derived from the source, over 40 seeds, at 100, 2000 and 20000 impressions per variant, plus a scenario dropping a loser instead.
- Got right: The drift case was deterministic: the stale sidecar picked the true best 0 of 40 at every budget, so more data cannot fix it. The count mismatch (tracked 6, ranked 5) exposed it immediately.
- Where/why it failed: My prediction that the derived map would recover the true best at least 28 of 40 at 2000 impressions was wrong: it got 18 of 40 (10 at 100, 22 at 20000) because v4 leads the runner-up by only about 4 percent, and dropping a loser (v3) also left only 16 of 40.
- Fix: Derive the label-to-id map from the upstream source on every run, print tracked and ranked counts side by side and fail when they differ, and treat the sample-size flip as a separate, budget-driven problem.
- Why this fix: Drift removes a contender with certainty regardless of budget, while sampling noise only blurs a close race; the two have different cures (derive the map versus confirm at two budgets), so one check cannot stand in for the other.
- Rule of thumb: Before trusting a ranking pick, compare the tracked contender count to the ranked count; a mismatch means a sidecar dropped someone, and no impression budget will bring them back.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session (RESULT line below); the toy rates are assumed, not real ad data.
- Composed: collective-reference/E1, rank-ipm-times-d1-needs-fidelity-retention-link/E1, brain-film-explainer/E4
- Picked-by: new-half
- ZaneGPT verdict: weak — The count check caught this one drop, but the evidence is one failure in one design. The "no budget will bring them back" half is confirmed by 0/40. The prediction was refuted: the derived-map pick rates were 10, 18 and 22 of 40, not at least 28. And the check is blind whenever tracked and ranked move together or errors cancel.
- Hidden assumption: A count mismatch is observable and means something. The rule assumes the tracked set is independently sourced, and that the ranked set shrinks only through a sidecar drop. It also assumes a missing contender is always the cause, not a defect elsewhere.
- Would prove it wrong: A silent failure that leaves 6 tracked and 6 ranked but a wrong pick. One case is a rename that maps the old id onto a different variant. Another is a duplicate id that overwrites a row. A third is a stale label that stays attached to the wrong metrics. If the count check passes in any of these, it is not a sufficient tripwire.
- Break scenario: Upstream renames v4 to v4b and also adds a new v7. The stale sidecar drops v4 but picks up v7 through a fallback default, so tracked is 7 and ranked is 6, or tracked and ranked both read 6 if the tracked list comes from the same sidecar. The check reads "fine" or fires on the wrong cause, and v4 is still missing. If tracked is derived from the sidecar itself, it can never mismatch.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 2d75b81b1786
- Sandbox: sandboxes/2026-10-17__sidecar-drift-silently-drops-ipm-d1-contender.py
- Prediction: Derived map picks the true best at least 28 of 40 seeds at 2000 impressions; stale sidecar picks it 0 of 40; dropping a loser leaves at least 28 of 40.
- Observed: RESULT: PASS (revised claim) drift picks truth 0/40; derived recovery 100:10 2000:18 20000:22 of 40; loser-drop(2000) 16/40; tracked 6 vs ranked 5. The 28-of-40 prediction was refuted; recovery is budget-limited by a close race.
- Scenarios: 1) stale sidecar drops v4; 2) derived map from source; 3) BREAK: drop a loser (v3) instead of the winner; 4) budget 100 vs 2000 vs 20000; 5) tracked-vs-ranked count check
- Link: brain train auto loop 1 pass 1; session_01S4WKoTG7YsrzCXAnXDQDg7

