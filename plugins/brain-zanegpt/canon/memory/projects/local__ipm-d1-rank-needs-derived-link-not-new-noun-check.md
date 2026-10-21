# local/ipm-d1-rank-needs-derived-link-not-new-noun-check — lessons

Project: local/ipm-d1-rank-needs-derived-link-not-new-noun-check. Newest first.

---

## E1 — ipm d1 rank needs derived link not new noun check
- Date: 2026-10-17
- Project: local/ipm-d1-rank-needs-derived-link-not-new-noun-check
- Tags: [game-ads][testing][model][sandbox]
- What: Sandbox of ranking six ad recuts per sheet on IPM times predicted D1, where predicted D1 comes from a fidelity check column: either the naive any-new-noun check or a derived-from-game link check.
- Why built: The IPM times D1 ranking only helps if the fidelity column is right, and the scene-check lesson says the new-noun check mislabels derived beats; unknown whether that carries into ad recut ranking.
- Design: Six deterministic sheets (two flashy-undelivering, two mixed, one stock-premise, one all-derived as the break case); flashy recuts get higher IPM but half the D1; each check picks the max of IPM times estimated D1 and is scored against true IPM times D1.
- Got right: The derived-from-game link check picked the true best in 5 of 6 sheets versus 3 of 6 for the new-noun check, and the new-noun check even failed the all-derived sheet where nothing should differ.
- Where/why it failed: My prediction of 6/6 for the link check was wrong: the stock-premise flag demoted a derived recut whose true D1 was fine, costing one sheet.
- Fix: Use the derived-from-game link as the fidelity column for IPM times D1 ranking, and treat a stock flag as a tiebreak warning rather than a hard demotion.
- Why this fix: The link tracks what the game delivers, which is what D1 measures, while novelty of nouns is independent of delivery.
- Rule of thumb: When ranking recuts on IPM times D1, feed it a derived-from-game fidelity link, not a new-noun check; in this toy model that was 5 of 6 sheets versus 3 of 6, and a stock flag should not hard-demote.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the retention numbers are a toy model, not real ad data.
- Composed: ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention, rank-ipm-times-d1-needs-fidelity-retention-link/E1, game-of-scene-hxe-check-column/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__ipm-d1-rank-needs-derived-link-not-new-noun-check.py
- Prediction: Assumed new nouns track fidelity; expected the naive check to miss at least 3 of 6 sheets and the link check to hit 6 of 6.
- Observed: RESULT: PASS naive exact 3/6, link-check exact 5/6; prediction of 6/6 missed on the stock sheet.
- Scenarios: 1) flashy sheet seed 1; 2) flashy seed 2; 3) mixed seed 3; 4) mixed seed 4; 5) stock-premise sheet built to break the link check; 6) all-derived sheet where checks should not matter.
- Link: brain train auto pass 1; session_011LtaNZCrPYhhAtwJpZ1y8i
- Audited: 2026-10-17 · fail · Read the entry and its stored sandbox. The answer is built in: the generator sets true D1 from the boolean derived (0.40 if derived else 0.20), and the link check reads that same derived field, so it can only score well by reading the cause of the outcome. The naive check reads a noun flag that the generator draws independently in the mixed, stock and all-derived sheets, so its 3 of 6 is partly random chance, and its failure on the all-derived sheet comes from that random flag rather than any property of a new-noun test. The sheet-5 miss is only the stock flag subtracting from the same field. Nothing tests whether a derived-from-game label can be produced reliably from real recuts, which is the claim that matters; the Rule of thumb's wider claim (feed ranking a derived link) goes beyond what a hand-written, self-labelled model covers. · brain train auto loop 1 pass 3 audit (session_01S4WKoTG7YsrzCXAnXDQDg7)
- Cited-by: 2026-10-17 · projects/local__derived-link-beats-sidecar-and-noun-check-until-link-noise-passes-a-threshold.md#E1 · compatible · sandboxes/2026-10-17__derived-link-beats-sidecar-and-noun-check-until-link-noise-passes-a-threshold.py · observed RESULT: PASS derived@0 1.000 sidecar@.25 0.667 noun 0.135 ipm 0.132; derived@.8 0.217; crossover noise 0.5; drift0 sidecar 1.000. At noise 0.2 derived 0.672 vs sidecar 0.642 (still slightly ahead). · brain train auto loop 1 pass 1; session_01RpeN38wP8qZN5F5czYD6HX
- Cited-by: 2026-10-18 · projects/pappydapimp69__brain.md#E212 · incompatible · sandboxes/2026-10-18__derived-link-gate-narrows-the-comic-engines-left-to-rank-on-ipm-times-d1.py · observed RESULT: FAIL distinct engines link 4.72 vs noun 6.64; top3 repeat gap 1.3 pts; value ratio 1.48; cap-1 loss 1.6%; flat-derivability distinct 4.90. Narrowing, value and cap-cost parts held; repeat gap and flat-control parts failed. · scheduled brain train session_01YL3uJX45U8L4Nh9fQf5qoD
