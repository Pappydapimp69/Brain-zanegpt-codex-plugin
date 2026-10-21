# local/fidelity-check-column-guards-ipm-d1-recut-rank — lessons

Project: local/fidelity-check-column-guards-ipm-d1-recut-rank. Newest first.

---

## E1 — fidelity check column guards ipm d1 recut rank
- Date: 2026-10-17
- Project: local/fidelity-check-column-guards-ipm-d1-recut-rank
- Tags: [game-ads][testing][model][sandbox]
- What: A game-fidelity check column in front of a recut ranking is needed when recuts are ranked on IPM alone (clickbait recuts won 25 of 40 seeds) but nearly idle under IPM times D1 (2 of 40), and a naive any-new-noun version of the check also blocks a legitimate recut that was picked 10 of 40.
- Why built: To test whether the derived-from-game check from the comedy check-column lesson is the guard the IPM-times-D1 recut kernel needs against off-promise recuts.
- Design: Eight toy recuts, two of them clickbait (high install rate, low D1, new noun not derived from the game) and one legitimate recut with a new noun derived from the game. Rank at 300 impressions over 40 seeds under IPM alone and IPM times D1, with no check, a naive new-noun check, and a derived-from-game link check; plus a flat world without clickbait.
- Got right: The derived-from-game link check removed every off-game pick (25 to 0 under IPM alone) without changing the flat-world picks, and the naive check wrongly excluded the legitimate new-noun recut that the link check let win 10 of 40.
- Where/why it failed: My prediction that clickbait would win at least 20 of 40 even under IPM times D1 was refuted: it won 2 of 40, because multiplying by D1 already penalised the low-retention clickbait.
- Fix: Keep the IPM-times-D1 ranking as the first guard and add the derived-from-game link check only where ranking falls back to IPM alone or D1 is too noisy to separate the clickbait; never use a bare new-noun test.
- Why this fix: The product score and the check overlap on this failure, so stacking both is redundant in the toy world, while the check costs legitimate recuts if written as a noun test.
- Rule of thumb: Under IPM times D1 a fidelity check column is mostly redundant on clickbait recuts; under IPM alone it is required; either way test the derived-from-game link, not novelty.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the toy rates and the clickbait pattern are assumed, not measured ad data.
- Composed: game-of-scene-hxe-check-column/E1, rank-ipm-times-d1-needs-fidelity-retention-link/E1, ideas:GAME-ADS/iteration/concept-then-variants-ranked-on-ipm-times-early-retention
- Picked-by: new-half
- ZaneGPT verdict: weak — The ranking-metric half is supported, but the fix half rests on a hand-assigned oracle label and a hand-tuned D1 gap, so 25→0 and 10/40 show only that the toy encodes the answer.
- Hidden assumption: The rule treats the toy world as the real one: that "derived-from-game" is a cleanly checkable property, and that D1 and clickbait are separable. The 2/40 under IPM×D1 holds only because the author set clickbait D1 low enough to be penalized. A clickbait recut with a mid D1 would slip through that product.
- Would prove it wrong: Rerun with clickbait D1 raised to 70–90% of the legit recut's D1, over several seed batches. If off-game wins under IPM×D1 climb well above 2/40, "mostly redundant" fails. Also fails if the link check, run with a noisy or partly wrong derived-from-game label, loses the legit recut or lets clickbait through at a rate similar to the naive check.
- Break scenario: A clickbait recut whose noun is loosely game-adjacent (a real item name used out of context), plus a legit recut whose noun is derived from the game only by a non-obvious route. A link check with a realistic 15–20% mislabel rate then blocks the legit one and passes the clickbait. This is the case where the rule's own fix performs like the naive check it replaces.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest b3ed8c558960
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__fidelity-check-column-guards-ipm-d1-recut-rank.py
- Prediction: Clickbait recuts win at least 20 of 40 seeds even under IPM times D1 without a check, so the check column is needed there.
- Observed: RESULT: PASS (revised claim) IPM-only off-game 25/40 to 0 with link check; IPM x D1 off-game 2/40 to 0; naive check loses legit r3 (0 vs 10/40); flat world unchanged. The original prediction was refuted (2 not 20).
- Scenarios: 1) IPM alone no check; 2) IPM alone with link check; 3) IPM x D1 no check; 4) BREAK: naive new-noun check against the legitimate new-noun recut; 5) flat world without clickbait
- Link: brain train auto loop 1 pass 2; session_01S4WKoTG7YsrzCXAnXDQDg7

