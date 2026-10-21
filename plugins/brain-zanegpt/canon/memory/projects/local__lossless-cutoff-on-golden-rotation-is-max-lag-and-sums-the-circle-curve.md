# local/lossless-cutoff-on-golden-rotation-is-max-lag-and-sums-the-circle-curve — lessons

Project: local/lossless-cutoff-on-golden-rotation-is-max-lag-and-sums-the-circle-curve. Newest first.

---

## E1 — lossless cutoff on golden rotation is max lag and sums the circle curve
- Date: 2026-10-18
- Project: local/lossless-cutoff-on-golden-rotation-is-max-lag-and-sums-the-circle-curve
- Tags: [gamedev][input][state][testing]
- What: On a golden-rotation legality word with lag set 3, 21, 55, 89, 144, an age cutoff on top of validity is lossless first at the largest lag, 144, while a cutoff of 21 loses about 1650 valid presses; the gate-only invalid count summed up to a cutoff equals the sum of the circle-form curve N x min(x, 1 - density) within 0.52 ticks per lag, rising 131, 150, 157, 161, 164 but flattening beyond lag 21.
- Why built: Train pick joining the lossless-threshold-exceeds-period lesson and the lossless-cutoff-is-worst rule with the Fibonacci circle-form curve, to see whether the max-lag cutoff rule and the cumulative gate cost still pair up on an aperiodic signal that has no period to confuse them.
- Design: Sturmian word floor((n+1)a+b) minus floor(n a+b) with a = 1/phi at offsets b 0 and 0.31, 900 presses per lag; valid means legal at issue and at use, invalid means legal at issue and illegal at use; lossless cutoff is the smallest cutoff leaving no valid press above it; circle curve predicted from the rotation distance of each lag; 10 Bernoulli(0.618) signals as control.
- Got right: Lossless cutoff 144 on both offsets, cutoff 21 lost 1654 and 1653 valid presses, per-lag invalid counts 131, 19, 7, 4, 3 sat within 0.52 of the circle curve, and the cumulative invalid count was nondecreasing with its maximum at the lossless cutoff.
- Where/why it failed: The lossless cutoff is worst only nominally here: raising the cutoff from 21 to 144 adds 14 invalid presses to 150 (131 already enter at lag 3), so the rule that the lossless cutoff is worst for the gate is true but nearly flat past the dip lags; the Bernoulli control missed the curve by 100 or more at lag 55 in all 10 seeds, which confirms the curve needs rotation structure.
- Fix: On a rotation signal pick the validity cutoff from the largest lag in use, and size a validity-free gate by summing N x min(x, 1 - density) over the lag set instead of assuming the worst case grows with the cutoff; scan per lag when the signal is not a rotation.
- Why this fix: Every lag on a density-0.618 rotation has valid presses because the rotation distance never exceeds one half, so the cutoff is set by the largest lag in use, while the gate cost is dominated by the lags with large rotation distance, which are not the large lags.
- Rule of thumb: On a golden rotation signal the lossless validity cutoff is the largest lag in use and the gate-only invalid count is the sum of N x min(x, 1 - density) over lags up to the cutoff, so late large lags can add almost nothing; do not read that as a rule for random legality.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session: one golden rotation at two offsets, one five-lag set, 900 presses per lag, 10 Bernoulli seeds; other slopes and lag sets were not run.
- Composed: age-cutoff-lossless-threshold-exceeds-period-p12/E1, lossless-cutoff-is-worst-without-validity/E1, fibonacci-gate-curve-is-the-circle-form-of-the-periodic-min-formula/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — Two offsets, one irrational, and a lag set that is Fibonacci-adjacent to phi show the rule works there, but the "largest lag" claim is untested off that structure, and the Bernoulli control only tests that random legality misses one curve, not that the rule is specific to rotation.
- Hidden assumption: The rule treats "largest lag in use" as the lossless cutoff because a valid press can sit at any age up to the lag. That assumes the press's age is bounded by its own lag and the word is a pure Sturmian sequence with a = 1/phi, a fixed lag set, and a fixed 900 presses per lag. Nothing else is assumed to shift the age distribution. Two other things are also assumed: that "valid" is defined only by legality at issue and at use, and that the 144 result generalizes beyond five Fibonacci-adjacent lags that are themselves tied to phi.
- Would prove it wrong: Add a lag larger than 144, such as 233, or a non-Fibonacci lag set (say 50, 100, 200), and the lossless cutoff does not equal the new maximum lag. Another refutation is a rotation with a different irrational (e.g. 1/√2) or a very different offset, where the gate-only sum drifts more than about 1.5 ticks per lag from N x min(x, 1 - density). Either would show the result depends on the golden/Fibonacci structure, not on the max-lag rule.
- Break scenario: Keep the golden word but use a lag set that is not Fibonacci and not nested, e.g. 34, 77, 120, 200, 310, with a press count that is not a round 900 and a third offset such as 0.97. Check whether lossless cutoff = 310 and whether the cumulative gate-only invalid count still tracks the circle curve within 1.5 ticks per lag. Also run a Bernoulli control matched to the same density, so the 10/10 miss is not just a consequence of the specific lag-55 comparison.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest cb8de7e53245
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__lossless-cutoff-on-golden-rotation-is-max-lag-and-sums-the-circle-curve.py
- Prediction: Lossless cutoff 144 on both offsets, a cutoff of 21 loses valid presses at lags 55, 89 and 144, gate-only invalid summed to each cutoff is within 1.5 ticks per lag of the circle curve and nondecreasing with its maximum at 144, and at least 8 of 10 Bernoulli seeds miss the lag-55 curve by 100 or more.
- Observed: RESULT: PASS lossless cutoff 144 on both offsets, cutoff 21 loses valid presses (1654, 1653), summed circle curve within 0.52 ticks per lag, cumulative 131, 150, 157, 161, 164 (b 0), Bernoulli off the curve in 10/10 seeds.
- Scenarios: 1) golden rotation offset 0; 2) offset 0.31; 3) cutoff 21 as a period-like cutoff, built to break the max-lag rule if it held only at the period; 4) 10 Bernoulli seeds as random-legality control
- Link: scheduled brain train auto loop 1 pass 5; session_01FjbQokSDjejDZsbW36mBhq

