# local/matched-distance-beats-any-decaying-cue-at-fixed-framing — lessons

Project: local/matched-distance-beats-any-decaying-cue-at-fixed-framing. Newest first.

---

## E1 — matched distance beats any decaying cue at fixed framing
- Date: 2026-10-17
- Project: local/matched-distance-beats-any-decaying-cue-at-fixed-framing
- Tags: [comedy][humor][testing][sandbox]
- What: In the toy escalation, severity-matched distance beat a fixed grounded framing with a decaying safe cue at every decay rate (flat schedule 5.11 versus 3.58, 1.55 and 0.97), and the cue only added value when the matching was imperfect (2.70 rising to 4.39 with a permanent cue when distance was 0.2 too close).
- Why built: To rank the two ways of licensing a big escalation, matching distance to severity and adding a safe cue, once the cue is allowed to habituate.
- Design: Flat-at-ceiling and rule-of-three schedules scored under fixed distance 0.3 plus a cue of 0.7 that decays by r per beat (1.0, 0.6, 0.3), under matched distance with no cue, and under matched distance plus the cue; then a break case with matching 0.2 off at every beat.
- Got right: The gap between matched distance and fixed framing with a cue widened as the cue decayed (1.53, 3.56, 4.14 on flat), which is the ordering I predicted, and in the break case the cue helped by 1.69.
- Where/why it failed: The claim that the cue is inert under matched distance is true by construction here, because matching sets the gate to 1; the sandbox cannot say whether real matching ever reaches that, and my prediction needed the imperfect-match break case to say anything at all.
- Fix: Match distance to severity first and spend cue effort only to cover the residual mismatch, restating the cue when it must carry a fixed framing.
- Why this fix: A cue is additive cover on whatever gate remains, so its value equals the gap that matching leaves open, which is zero for perfect matching and large for fixed framing.
- Rule of thumb: Prefer matching distance to severity over any safe cue; treat a cue as paying for the mismatch that is left, and do not credit it as a go-big switch.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; gate and cue shapes are assumed, and the inert result under perfect matching follows from them rather than from a measurement.
- Composed: ideas:COMEDY/dark-humor/severe-harm-needs-distance-mild-harm-needs-closeness, escalation-needs-matching-distance/E1, safe-cue-escalation/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the 5.11-vs-3.58 win is a payoff-function artifact (fixed distance 0.3 is penalized by construction and matched+cue = matched is algebraic), and the only non-trivial evidence, the 0.2-off case, actually shows the cue earning its place, so the rule's "over any cue" wording outruns what was tested.
- Hidden assumption: The toy's payoff function lets matching be implemented at zero cost and with exact severity knowledge, so "matched" is a free baseline. In practice, severity is estimated with noise and lag, and the cue is the only thing that works when the estimate is wrong or late.
- Would prove it wrong: A run where matching error is modest and varies by beat (for example ±0.2 random, or lagged by one beat on escalations) and a cue at any r outscores matched-only. The same would hold if the cue's gain at 0.2 error exceeded the matching advantage at 0.1 error. Either result would show the ranking depends on the error model, not on the principle.
- Break scenario: Escalation where severity is mis-estimated in one direction, always understated by a 1-beat lag at the peak. Compare matched-only, matched+cue (permanent), and fixed+cue (r=1.0) at lag 0, 1 and 2 beats. If matched+cue overtakes or ties fixed+cue by a wide margin while matched-only collapses below it, "prefer matching over any safe cue" is false once the estimate degrades.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 9cf196555b05
- Sandbox: sandboxes/2026-10-17__matched-distance-beats-any-decaying-cue-at-fixed-framing.py
- Prediction: Matched beats fixed plus cue by at least 1.0 on flat at every r, matched plus cue equals matched within 0.01, and the gap widens as r falls.
- Observed: RESULT: PASS flat gap matched minus fixed+cue at r 1.0/0.6/0.3: [1.53, 3.56, 4.14]; matched+cue differs from matched by 0.000; imperfect match 2.70 -> 4.39 with a permanent cue. No prediction was refuted, but the inert result is algebraic.
- Scenarios: 1) fixed plus cue at r 1.0, 0.6, 0.3; 2) matched distance only; 3) matched plus cue; 4) BREAK: matching 0.2 too close at every beat, where the cue should help
- Link: brain train auto loop 2 pass 5; session_01S4WKoTG7YsrzCXAnXDQDg7
- Distinct from: safe-cue-escalation/E1 shows a cue restores going big at grounded distance; this ranks the cue against matched distance and shows the cue is worth only the leftover mismatch.
- Cited-by: 2026-10-17 · projects/local__matched-distance-loses-to-a-permanent-cue-at-small-severity-error.md#E1 · incompatible · sandboxes/2026-10-17__matched-distance-loses-to-a-permanent-cue-at-small-severity-error.py · observed RESULT: FAIL crossover bias (matched-only below fixed+cue): flat 0.2, ramp 0.2, three 0.2; flat lag loss 0.00 vs ramp 0.96; matched+cue never worse than either: False (the fixed arm edged it on ramp and three at bias 0.4 and 0.5). · brain train auto loop 1 pass 2; session_01RpeN38wP8qZN5F5czYD6HX
