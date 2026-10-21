# local/gate-invalid-dip-tracks-each-rotations-own-slope-not-phi — lessons

Project: local/gate-invalid-dip-tracks-each-rotations-own-slope-not-phi. Newest first.

---

## E1 — gate invalid dip tracks each rotations own slope not phi
- Date: 2026-10-18
- Project: local/gate-invalid-dip-tracks-each-rotations-own-slope-not-phi
- Tags: [gamedev][input][state][testing]
- What: Ran the rotation-proximity lesson on five rotation slopes (golden, silver, e minus 2, pi minus 3 plus 0.3, and 1/12 plus 0.0003) and found the gate-only invalid count follows each slope's own distance of lag times slope to an integer (correlation 1.000) and is uncorrelated with the golden-ratio distance (about 0 on the other four), so the dip is a rotation fact, not a Fibonacci one.
- Why built: Train pick: the rotation-proximity lesson's own ZaneGPT check named a different irrational slope as the case that would make its rule a general rotation fact, and the period lesson's lossless threshold had never been compared with a near-periodic rotation.
- Design: legal(t) = frac(0.21 + t x alpha) < 0.4, N 1000 uses per lag, lags 1 to 120, hint invalid iff legal at issue and illegal at use; correlation of invalid with min(0.4, distance of lag x alpha to nearest integer) and with the same quantity for phi; validity-based lossless lag as the largest lag with any valid hint.
- Got right: Own-slope correlation was 1.000 on all five slopes, golden-distance correlation on the others was between -0.045 and 0.014, minima fell at lag 89 for golden, 70 for silver, 71 for e minus 2, 77 for the pi slope and 12 for the near-1/12 slope, where it behaves like the period-12 wave.
- Where/why it failed: The correlation of 1.000 is nearly true by construction, since invalid presses are the measure of an interval overlap, so it confirms the model rather than finding a new law; the near-periodic slope had a lossless lag of 120 (the scan limit), not the 11 of an exactly periodic P12 wave, because a rotation never recovers exactly yet always has some valid hints.
- Fix: For any rotation-like legality, scan lags with the slope's own distance function, expect dips at denominators of its continued-fraction convergents (89, 70, 71, 77, 12 here), and set the cutoff from the per-lag table rather than from a period or from Fibonacci numbers.
- Why this fix: The invalid count is the overlap of an interval with its shifted copy, which depends on the shift, lag times slope modulo one, and nothing else about the slope.
- Rule of thumb: Gate-only invalid dips at the lags where lag times the signal's slope is near an integer, for any slope; use the signal's own slope, not phi, to find them, and a near-periodic slope still never gives an exact lossless lag.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below; five slopes, one interval width 0.4, one phase, N 1000; Sturmian words other than interval rotations were not run.
- Composed: age-cutoff-lossless-threshold-exceeds-period-p12/E1, lossless-cutoff-is-worst-without-validity/E1, fibonacci-gate-drop-is-rotation-proximity-not-fibonacci-lags/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the "rotation fact, not Fibonacci" claim is plausible, but r = 1.000 against a metric that restates the generator is a tautology check, and "lossless lag 120" for the near-1/12 slope sits inside the tested range, so it shows no ceiling and doesn't back the "never exact" claim.
- Hidden assumption: Invalid count depends only on frac(lag × alpha), which holds because uses are uniformly spread over phase (or the lag-to-use map is a pure rotation). The correlation was measured against a metric the design itself builds from that distance, so r = 1.000 is partly circular. The metric, min(0.4, dist), is the exact measure of the overlap between the legal window and its shift. It is a restatement of the generator, not evidence about a signal.
- Would prove it wrong: A slope where the own-slope r falls below 0.95 once the clip at 0.4 is removed, or once uses are sampled from a non-uniform or finite, aliased set. A near-periodic slope whose invalid count has structure at lags not near an integer multiple of the slope would also refute it.
- Break scenario: Use alpha = 1/12 + 0.0003 with N = 1000 uses, starting phase fixed at 0.21 (not randomised), and a legal window straddling the 0/1 wrap. Add an irrational slope near 0.5, where lag × alpha sits near a half-integer for odd lags. If the count tracks distance to the nearest integer rather than distance to the nearest half-integer, the rule is wrong for period-2 structure. Also test a slope where legal(t) uses a threshold of 0.9 instead of 0.4, so that min(0.4, d) saturates and the metric becomes uninformative.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest d335a4998b97
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__gate-invalid-dip-tracks-each-rotations-own-slope-not-phi.py
- Prediction: Written before the first run: own-slope correlation above 0.95 on all five slopes, golden-distance correlation below 0.6 on the four others, and a lossless lag above 12 for the near-1/12 slope.
- Observed: RESULT: PASS own-slope r 1.0 on five slopes, phi-distance r between -0.04 and 0.01 on the other four, near-periodic 1/12 slope lossless lag 120.
- Scenarios: 1) golden slope; 2) silver slope, e minus 2 and pi minus 3 plus 0.3, built to break the phi-specific reading; 3) near-1/12 slope against the period-12 lesson.
- Link: https://claude.ai/code/session_01MRoVc2AE75bu8wwdpoV7jJ

