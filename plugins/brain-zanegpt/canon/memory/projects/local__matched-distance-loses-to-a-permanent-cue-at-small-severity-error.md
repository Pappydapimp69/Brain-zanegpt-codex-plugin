# local/matched-distance-loses-to-a-permanent-cue-at-small-severity-error — lessons

Project: local/matched-distance-loses-to-a-permanent-cue-at-small-severity-error. Newest first.

---

## E1 — matched distance loses to a permanent cue at small severity error
- Date: 2026-10-17
- Project: local/matched-distance-loses-to-a-permanent-cue-at-small-severity-error
- Tags: [comedy][humor][testing][sandbox]
- What: In the toy escalation, matching distance to severity stops beating a permanent safe cue at fixed framing once the severity estimate is off by only 0.2 (flat schedule 2.70 against fixed-plus-cue 3.58; the ramp 1.50 against 2.17; rule-of-three 1.89 against 2.60), well before the 0.3 I predicted. A one-beat lag costs nothing on the flat schedule but 0.96 on a ramp.
- Why built: The prior lesson ranked matched distance above any cue only with perfect matching, where the cue is inert by construction; its ZaneGPT check asked what happens when the severity estimate is biased or late.
- Design: Same gate and habituation as the escalation model (gate width 0.25, ceiling 10, six beats). Matched arm sets distance to a biased or lagged severity (bias 0 to 0.5, lag 0 to 2 beats); fixed arm uses distance 0.3 with a permanent cue of 0.7; a third arm adds the cue to the matched arm. Schedules flat, ramp (2,4,6,8,10,10) and rule-of-three.
- Got right: Matched-plus-cue beat or tied both other arms in 20 of 24 bias cases, and a cue lifts a biased match a lot (flat bias 0.3: 1.21 to 3.94). A lag only hurts when severity changes (flat 5.11 at every lag; ramp 2.85, 1.89, 0.84).
- Where/why it failed: My prediction failed: I expected matched-only to stay ahead of fixed-plus-cue up to a bias near 0.3, but it lost by 0.2 on all three schedules. Matched-plus-cue was also not always at least as good: on the ramp and rule-of-three at bias 0.4 and 0.5 the fixed arm edged it (2.17 against 2.06), because fixed distance 0.3 fits the mild early beats.
- Fix: Do not rank matched distance above a safe cue unconditionally; treat the cue as insurance that pays once the severity estimate is more than about 0.1 to 0.2 off or lags a ramping schedule, and prefer matching plus a cue to either alone.
- Why this fix: The gate is narrow (width 0.25), so a small distance error drives it near zero, and a permanent cue floors the score at its own level whatever the error, which makes the cue worth more than exact matching when the estimate is noisy.
- Rule of thumb: Matched distance beats a permanent safe cue only when the severity estimate is within about 0.1 (flat: 4.36 against 3.58 at bias 0.1, 2.70 at 0.2); beyond that, or with a lagging estimate on a ramp, keep the cue, and use match plus cue as the default.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the gate shape, width, cue level and bias and lag models are assumed toy forms, not measured audience data.
- Composed: matched-distance-beats-any-decaying-cue-at-fixed-framing/E1, escalation-needs-matching-distance/E1, ideas:COMEDY-CRAFT/theory/benign-violation
- Picked-by: new-half
- ZaneGPT verdict: weak — the direction is supported (the crossover came in at 0.2, not the 0.3 predicted, and the failed prediction is reported honestly), but "match plus cue as default" is contradicted by your own result (fixed edged it on ramp and rule-of-three at bias 0.4 and above), and the 0.1 threshold rests on one parameter set and one error type.
- Hidden assumption: The toy's fixed-arm numbers (distance 0.3, cue 0.7) and its habituation and gate parameters transfer to real severity-estimation error, so a crossover at "about 0.1" is a property of the world and not of those tuned constants.
- Would prove it wrong: Re-run with the fixed arm's distance and cue strength varied (say 0.2 to 0.5 and 0.4 to 0.9) and gate width varied. If the matched-versus-fixed crossover moves from about 0.1 to 0.3 or more, or flips sign, the rule describes the parameter choice and not the matching.
- Break scenario: Use a bias that has a sign and a distribution. Run the matched arm with under-estimation and over-estimation separately, and with zero-mean noise per beat at the same magnitude. The rule treats a systematic offset as the only error. If matched wins under noise and loses under one-sided bias, or the reverse, "within 0.1" is the wrong unit. Add a fixed arm tuned to the schedule mean, because the current one may be a weak baseline.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest ec7914434334
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__matched-distance-loses-to-a-permanent-cue-at-small-severity-error.py
- Prediction: Matched-only beats fixed-plus-cue on flat up to a systematic distance error of about 0.3 and loses beyond it (crossover between 0.25 and 0.35); a one-beat lag costs matched-only little on flat but more on the ramp; matched-plus-cue is at least as good as both other arms in every case.
- Observed: RESULT: FAIL crossover bias (matched-only below fixed+cue): flat 0.2, ramp 0.2, three 0.2; flat lag loss 0.00 vs ramp 0.96; matched+cue never worse than either: False (the fixed arm edged it on ramp and three at bias 0.4 and 0.5).
- Scenarios: 1) flat schedule, bias 0 to 0.5; 2) ramp schedule, bias 0 to 0.5; 3) rule-of-three, bias 0 to 0.5; 4) lag 0, 1, 2 on all three schedules (built to BREAK the matched-distance claim)
- Link: brain train auto loop 1 pass 2; session_01RpeN38wP8qZN5F5czYD6HX

