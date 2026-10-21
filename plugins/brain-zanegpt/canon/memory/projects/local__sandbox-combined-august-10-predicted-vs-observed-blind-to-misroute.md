# local/sandbox-combined-august-10-predicted-vs-observed-blind-to-misroute — lessons

Project: local/sandbox-combined-august-10-predicted-vs-observed-blind-to-misroute. Newest first.

---

## E1 — sandbox combined august 10 predicted vs observed blind to misroute
- Date: 2026-09-28
- Project: local/sandbox-combined-august-10-predicted-vs-observed-blind-to-misroute
- Tags: [observability][testing][simulation][method]
- What: Re-verified conjunct-rates-cannot-see-a-routing-defect#E1 from a new angle: not only the per-conjunct gauges but also the predicted-vs-observed multiply-and-compare (the detector the opticon/august-10 entry credits for catching a dead branch) is blind to a target misroute. The prediction is made at the fire rung, and a misroute fires exactly as often as predicted. Carrying the same prediction one rung further (expected hits on the intended target = predicted fires) catches both defect classes.
- Why built: brain train AIM listed the single-source edge sandbox-combined-august-10-brain-builder-conjunct-rates-cannot-see-a-routing-defect + august-10. That entry showed conjunct marginals miss a misroute; the sibling predicted-vs-observed entry claims multiply-and-compare is the real detector. Unverified: does that detector reach a routing defect?
- Design: Deterministic, no RNG: 20000 ticks, conjunct A = t%16==0 (1/16), conjunct B = (7t+3)%25==0 (1/25), independent by coprime residues. Three variants: healthy; dead (B cleared before the AND, opticon clear-before-read shape); misroute (action fires but targets self, brain-builder#E9 shape). Record marginals, predicted fires N*pA*pB, observed fires, hits on enemy; flag when observed deviates >50% from predicted, at the fire rung and at the hit rung.
- Got right: Marginals identical in all three variants (pA 0.0625, pB 0.0400, predicted 50.0), confirming the prior entry's gauge-blindness and the sibling entry's dead-branch detection (fires 0 vs 50 -> flagged).
- Where/why it failed: Misroute: fires 50 = predicted 50, so fire-rung predicted-vs-observed does NOT flag; hits_on_enemy 0. The detector inherits the rung it is applied at — a defect downstream of the compared quantity passes it exactly.
- Fix: Apply predicted-vs-observed at the outcome rung (intended-target hits), not only at the fire count; with that, healthy passes (50 vs 50), dead flags (0), misroute flags (0).
- Why this fix: The multiply-and-compare is sound but only certifies the quantity it compares; moving the comparison to the effect-on-target covers both the reachability class (dead branch) and the routing class (misroute) with one check.
- Rule of thumb: Predicted-vs-observed only certifies the rung it is computed at — compared at the fire count it catches a dead branch (0 vs 50) but passes a target misroute exactly (50 vs 50, 0 enemy hits); compute the prediction at the intended-effect rung.
- Provenance (verified/assumed): Verified first-hand — sandbox/pvo_vs_misroute.py in brainwork (deterministic, run twice, identical md5 b498ba00). Observed: healthy fires 50/hits 50/no flags; dead fires 0/hits 0/both flag; misroute fires 50/hits 0/fire-flag False, hit-flag True; predicted 50.0 in all. Assumed: the intended target is known at instrumentation time (true for side-targeting, less so for AoE).
- Composed: sandbox-combined-august-10-brain-builder-conjunct-rates-cannot-see-a-routing-defect/E1, pappydapimp69__august-10/E17, sandbox-combined-opticon-august-10-predicted-vs-observed-is-the-detection/E1, pappydapimp69__brain-builder/E9
- Link: brain train scheduled pass, 2026-09-28

