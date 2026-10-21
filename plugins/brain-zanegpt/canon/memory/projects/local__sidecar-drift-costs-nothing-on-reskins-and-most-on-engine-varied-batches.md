# local/sidecar-drift-costs-nothing-on-reskins-and-most-on-engine-varied-batches — lessons

Project: local/sidecar-drift-costs-nothing-on-reskins-and-most-on-engine-varied-batches. Newest first.

---

## E1 — sidecar drift costs nothing on reskins and most on engine varied batches
- Date: 2026-10-17
- Project: local/sidecar-drift-costs-nothing-on-reskins-and-most-on-engine-varied-batches
- Tags: [game-ads][testing][model][sandbox]
- What: In a toy IPM times D1 recut ranking over 2000 six-variant batches, a hand-kept fidelity sidecar with 25% stale entries picked the true best in 100% of batches made of reskins of one engine, 72.5% of mixed batches (three reskins plus three different engines) and 64.2% of engine-varied batches, losing 0.348 of score on average in the varied case; a column derived from the game was exact (100%) in all three. In varied batches the sidecar fell from 84.4% at 10% drift to 40.6% at 50%.
- Why built: The sidecar lesson says derive the map instead of hand-keeping it, and the engine kernel says vary the engine not the topic; together they predict that how much drift matters depends on how different the variants are.
- Design: Fidelity from {0.2, 0.5, 1.0}; IPM = 10 x hook x (1.6 - 0.6 f); D1 = 0.15 + 0.25 f; a stale sidecar entry copies a random variant's fidelity. Three batch kinds, seeded, with drift 0.1, 0.25 and 0.5 on the varied batches.
- Got right: Reskins are immune to sidecar drift because a stale entry copies an equal value; the cost of the drift rises with how different the engines are, which is why a hand sidecar is safest exactly where ranking is least needed.
- Where/why it failed: My mixed-batch prediction (80 to 95% exact) was wrong at 72.5%, because the three varied variants hold all the contenders and drift among them is as costly as in the fully varied batch. The reskin result is true by construction (identical fidelities), so only the mixed and varied numbers are evidence.
- Fix: Derive the fidelity column from the game for any batch that mixes engines; a hand sidecar is acceptable only for batches of reskins of one engine.
- Why this fix: The same variety that gives the ranking something to rank is what makes a stale entry change the pick, so the two cannot be traded off by trusting the sidecar.
- Rule of thumb: Hand-kept fidelity sidecars cost nothing on pure reskin batches and cost a third of the score in engine-varied ones (64% exact at 25% drift, 41% at 50%), so derive the column whenever the engines differ.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; fidelity levels, the IPM and D1 forms and the drift model are assumed toy forms, not real ad data.
- Composed: collective-reference/E1, rank-ipm-times-d1-needs-fidelity-retention-link/E1, ideas:COMEDY-CRAFT/vary-the-comic-engine-not-the-topic
- Picked-by: new-half
- ZaneGPT verdict: weak — the direction is plausible, but the 100% vs 64% gap is partly built in (a perfect derived column against a sidecar with random corruption). The "cost a third of the score" figure and the 80 to 95% mixed prediction miss both come from the toy's own parameters, not from evidence about real games.
- Hidden assumption: Staleness is random and independent of the outcome, and the sidecar's only failure is a wrong fidelity value. The toy builds that in: a stale entry copies a random variant's fidelity, and the "derived" column is exact by construction. Real drift is probably correlated (it hits the variants that were recut most), and a derived column is only as good as its extraction from the game. The rule also assumes the three-level fidelity model (IPM falling and D1 rising with f) matches real games.
- Would prove it wrong: Run the same comparison with the real fidelity-to-score map, or with staleness concentrated on the top-ranked variants. If the sidecar's exactness on varied batches is no worse than the derived column's, or if the derived column's own extraction errors (even 5 to 10% noise) cost as much as the sidecar's, the "derive whenever engines differ" rule falls apart. Also, if the 100% reskin result is the same for any drift level, that shows the toy cannot fail there, so it says nothing about "costs nothing".
- Break scenario: Varied batches where the derived column carries its own 15 to 25% extraction error, compared against a sidecar at 10% drift. That tests whether "derived beats sidecar" survives once derivation is imperfect. Add a batch where the top two variants differ only by hook, so fidelity staleness barely changes the ranking, to check that the 0.348 loss isn't mostly fidelity-spread noise.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 0de9266cdcc0
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__sidecar-drift-costs-nothing-on-reskins-and-most-on-engine-varied-batches.py
- Prediction: At drift 0.25 the sidecar is exact in 100% of reskin batches and about 65% of varied batches, derived is 100% in both, and mixed batches land at 80 to 95%.
- Observed: RESULT: FAIL sidecar exact at drift 0.25: reskin 1.0, mixed 0.725, varied 0.642; derived varied 1.0; mean value lost reskin 0.0, varied 0.348 (only the mixed-batch range was missed).
- Scenarios: 1) reskin batches; 2) mixed batches; 3) engine-varied batches (built to BREAK the sidecar); 4) varied batches at drift 0.1 and 0.5
- Link: brain train auto loop 2 pass 1; session_01RpeN38wP8qZN5F5czYD6HX

