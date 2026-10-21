# local/caption-warp-cap-before-ipm-d1-ranking — lessons

Project: local/caption-warp-cap-before-ipm-d1-ranking. Newest first.

---

## E1 — caption warp cap before ipm d1 ranking
- Date: 2026-10-17
- Project: local/caption-warp-cap-before-ipm-d1-ranking
- Tags: [game-ads][film][testing][sandbox]
- What: Toy test of whether capping a recut's caption-reading warp at 1.5 before ranking on IPM times D1 helps, using five sheets of recuts with 6 to 33 word promise captions on a 6 second cold open.
- Why built: The film lesson says stretching captions to reading time slows animation and to keep warp near 1.5, and the IPM times D1 lesson says the ranking only helps with a fidelity link; unknown whether a warp cap is worth adding to the ranking.
- Design: Words per recut set warp (words over 18) and IPM (3 plus 0.12 per word); D1 starts at 0.40 and loses a slope per 0.1 of warp above 1.5; the ranker picks the top IPM recut with or without the cap and is scored on true IPM times D1; slope swept from 0.005 to 0.2.
- Got right: The cap wins only when warp really costs retention: capped total 11.14 versus uncapped 8.65 at slope 0.2, first winning slope 0.05, and a sheet of only short captions is unchanged by the cap.
- Where/why it failed: The first run assumed the cap always helps and used a mild slope; the cap lost there (11.14 versus 12.01 at 0.005, and sheet 2 gave 2.352 versus 2.502), so the first prediction of 2 of 4 sheets was wrong.
- Fix: Treat the warp cap as a conditional guard: measure how much D1 drops per unit warp first, and add the cap only when that loss exceeds roughly 0.05 per 0.1 of warp in the model.
- Why this fix: A cap removes the highest-promise recuts, which is a cost when stretching is cheap and a gain when it is expensive, so the slope decides.
- Rule of thumb: Cap caption warp at 1.5 before IPM times D1 ranking only when slowed footage costs real retention (cap won from a slope of 0.05 and lost at 0.02 and below in this toy model); otherwise it throws away promise for nothing.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; every number comes from my own toy model, not real ad or retention data.
- Composed: ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention, rank-ipm-times-d1-needs-fidelity-retention-link/E1, brain-film-explainer/E2
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__caption-warp-cap-before-ipm-d1-ranking.py
- Prediction: Run 1 expected the cap to never lose and uncapped to pick over-warp recuts in at least 2 of 4 sheets (missed: 1 of 4). Run 2 expected the cap to lose at slope 0.005, win at 0.2 and cross between 0.02 and 0.1. Assumption: caption length is the only lever on warp.
- Observed: RESULT: PASS cap loses at slope 0.005 (11.14 vs 12.01), wins at 0.2 (11.14 vs 8.65); first winning slope 0.05
- Scenarios: 1) five sheets at slope 0.005; 2) slope 0.02; 3) slope 0.05; 4) slope 0.2; 5) all-short-caption sheet built to make the cap a no-op; 6) run-1 mild-slope case that broke the cap-always-helps claim.
- Link: scheduled brain train auto loop 1 pass 5 (gap); session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E418 · compatible · sandboxes/2026-10-17__sidecar-drift-corrupts-warp-cap-ranking.py · observed RESULT: PASS derived map = truth at all 12 slopes; drifted sidecar loses value at slopes [0.003, 0.005, 0.008, 0.01] and costs nothing at slope 0.0. The high-slope half of the prediction was refuted. · session 2026-10-17 scheduled brain train, loop 1 pass 2; session_01KkkcHHGkp6Sm9GJK6fsa84
- Cited-by: 2026-10-18 · projects/pappydapimp69__brain.md#E211 · compatible · sandboxes/2026-10-18__absorbing-reaction-pauses-into-caption-windows-trips-the-warp-cap-on-short-captions.py · observed RESULT: FAIL ABSORB over-cap captions 2 (worst warp 1.80); ABSORB wins at slope 0.005 True, HOLD wins at 0.05 True; first HOLD win at slope 0.01; 0.5 s pause ABSORB wins at all slopes True. Only the crossover band failed. · scheduled brain train session_01YL3uJX45U8L4Nh9fQf5qoD
- Audited: 2026-10-18 · modeled · Read the entry and reran its stored sandbox (same RESULT line, 11.14 vs 12.01 at slope 0.005 and 11.14 vs 8.65 at 0.2). The selection is computed, not hard-coded: it picks the top IPM variant with and without the 1.5 filter and sums IPM times D1. The weak spots are that D1 is a hand-written linear penalty whose slope is the swept input, so the crossover at 0.05 only restates where that assumed penalty outweighs the IPM gain, and IPM is a fixed linear function of caption length. The rule is about real ad retention, which was never measured, so the evidence supports the shape of the tradeoff (measure the slope first) but not the threshold. · scheduled brain train auto run 2026-10-18 loop 1 pass 3 (audit); session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E437 · compatible · sandboxes/2026-10-18__derive-pauses-after-warp-cap.py · observed RESULT: PASS derive-before-cap misses 8/8 and 8/8, derive-after-cap 0/8, cap no-op case 0/8 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E449 · compatible · sandboxes/2026-10-18__hook-caption-warp-cap-plus-pause-budget.py · observed RESULT: PASS fit 5/7/8 words; 8 words needs pause 0.3s even with free warp; 10 impossible; 7 words warp-only vs pause-mix. The free-warp part of the prediction was refuted. · scheduled brain train auto pass 2 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps
