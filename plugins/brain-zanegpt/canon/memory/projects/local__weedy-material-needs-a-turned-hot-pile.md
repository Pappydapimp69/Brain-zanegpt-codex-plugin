# local/weedy-material-needs-a-turned-hot-pile — lessons

Project: local/weedy-material-needs-a-turned-hot-pile. Newest first.

---

## E1 — weedy material needs a turned hot pile a cold pile or a mulch layer never reaches 131f
- Date: 2026-10-15
- Project: local/weedy-material-needs-a-turned-hot-pile
- Tags: [garden][soil][compost][sandbox]
- What: A deterministic pile model with core, middle and rim zones reproduces the hot-versus-cold composting
  kernel: a hot pile at 150 F core with rim 25 F cooler kills weed seeds (131 F for 3 days) and
  pathogens (140 F for 3 days) in 3 of 3 seed batches when turned every 5, 7 or 14 days; a pile never
  turned leaves the rim batch alive (2 of 3); a cold pile (90 F) and a 2-4 inch mulch layer kill 0 of 3.
- Why built: Gap pick: the hot-vs-cold kernel and the mulch kernel had no memory entry applying them. Mulch is
  the in-place cousin of a cold pile, so the question was whether weedy material is safe to use as mulch
  if it is not safe in a cold pile.
- Design: Zone temperature is core temperature minus an offset (0, 10, 25 F). Core ramps to 150 F in 3 days,
  holds while aerated, then falls 4 F per day starting 10 days after the last turn (my assumed oxygen
  limit). Turning rotates rim to core. 56 days, three seed batches starting in each zone, no random numbers.
  Cold pile is capped at 90 F and a mulch layer is held at 80 F with no insulation offset.
- Got right: The kernel's rule held: only a hot, turned pile reached the kill thresholds in every zone, and a
  cold pile and mulch layer reached them nowhere, so mulch made from weedy material keeps its seeds.
- Where/why it failed: I expected a 14-day turn interval to leave a cool rim batch alive, and it did not: rotation still
  moved every batch through the core, so the kernel's 3-7 day turn interval was not needed to kill seeds
  in this model. The aeration limit, offsets and 3-day rule are my assumptions, so the interval result is not a finding.
- Fix: Route weedy or diseased material to a hot pile that is turned at all, never to a cold pile or
  straight onto the ground as mulch; keep the 3-7 day interval as the kernel states, since this model only shows
  that turning matters more than its exact spacing.
- Why this fix: Killing needs every piece of material to spend days in the hot core; turning is what moves rim
  material there, while a cold pile and a mulch layer never get hot in any zone.
- Rule of thumb: Weedy material is safe only after a hot, turned pile: in the model 3/3 seed batches died when turned and 0/3 in a cold pile or mulch layer, and 2/3 without turning.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; zone offsets, the oxygen limit and the 3-day rule are my own model assumptions and not measured, the 131 and 140 F thresholds come from the kernel.
- Composed: ideas:GARDEN/hot-vs-cold-composting-pathogen-kill, ideas:GARDEN/mulch-benefits-and-stem-clearance-rule
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__weedy-material-needs-a-turned-hot-pile-a-cold-pile-or-a-mulch-layer-never-reaches-131f.py
- Prediction: Hidden assumption: turning frequency decides the kill. Expected turned 5 and 7 days 3/3, never turned fewer than 3/3,
  cold and mulch 0/3, and a 14-day turn leaving fewer than 3/3 (the break case); it would be wrong if never-turned also killed 3/3.
- Observed: RESULT: PASS turned hot 5d/7d (3, 3) (3, 3) | 14d (3, 3) | never (2, 2) | cold (0, 0) | mulch (0, 0); the 14-day expectation was refuted
- Scenarios: 1) hot turned every 5 days; 2) every 7 days; 3) every 14 days, built to break the claim that a slow turn leaves the rim alive; 4) hot never turned; 5) cold pile; 6) mulch layer.
- Link: scheduled brain train auto loop 1 pass 5 (gap); session_01Twuh3aqxvcX5mmf7uhRTr7
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E311 · compatible · sandboxes/2026-10-15__hot-pile-kill-time-integer-ticks-vs-float.py · observed RESULT: PASS wrong verdicts of 32: float 6, round-ticks 4, floor-ticks 0 · brain train auto session 2026-10-15 loop 2 pass 2; session_01RMAaQPULLrY2w6iRwP967n
