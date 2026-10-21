# local/fibonacci-gate-curve-is-the-circle-form-of-the-periodic-min-formula — lessons

Project: local/fibonacci-gate-curve-is-the-circle-form-of-the-periodic-min-formula. Newest first.

---

## E1 — fibonacci gate curve is the circle form of the periodic min formula
- Date: 2026-10-18
- Project: local/fibonacci-gate-curve-is-the-circle-form-of-the-periodic-min-formula
- Tags: [gamedev][input][state][testing]
- What: On a Fibonacci-type rotation word with legal density 0.618 the gate-only invalid count is N times min(x, 1 minus density), where x is the distance of lag times 1/phi to the nearest integer, within 1.3 ticks of 900 across lags 1 to 144 at two offsets, with a flat plateau of 229 on the 68 lags with x at least 0.382 and the symmetric count twice it within the lag bound.
- Why built: New-half train pick joining the Fibonacci rotation-proximity dip, the lossless-cutoff-is-worst rule and the symmetric-twice law, to see whether the periodic min(L, W, P-L, P-W) law has an exact aperiodic counterpart instead of only a correlation of 0.98.
- Design: Deterministic Sturmian word floor((n+1)a+b) - floor(n a + b), a = 1/phi, N 900, offsets b 0 and 0.31; one-sided counts legal now and illegal L later, symmetric counts any change; curve N times min(x, 1-a) where x = min(frac(L a), 1 - frac(L a)); 10 seeded Bernoulli 0.618 signals as the control.
- Got right: Maximum deviation 1.14 and 1.33 ticks over 144 lags at the two offsets, plateau deviation 0.8 on 68 lags, zero symmetric-bound violations, and the Bernoulli control was at least 190 off the curve at the dip lag 55.
- Where/why it failed: Nothing broke the curve on rotation words; it breaks on random legality of the same density (the control), so the law needs the rotation structure and not just the density.
- Fix: For rotation-structured legality size a validity-free gate from N times min(x, 1 minus density) per lag, which replaces the correlation-only statement, and scan per lag for any legality that is not a rotation.
- Why this fix: A rotation by a moves the legal arc by x, and the legal-then illegal-now overlap of two arcs on a circle is min(x, 1-density), the circle form of the periodic min law with window width replaced by arc length.
- Rule of thumb: Predict a rotation-structured wave's validity-free invalid count per lag in closed form as N x min(x, 1 - density), with x the rotation distance of the lag; it caps at N(1 - density) and is exact to a few ticks on a golden rotation, but means nothing for a random wave of equal density.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; golden-ratio rotation only, two offsets, N 900, lags to 144; other rotation numbers are not tested.
- Composed: fibonacci-gate-drop-is-rotation-proximity-not-fibonacci-lags/E1, lossless-cutoff-is-worst-without-validity/E1, symmetric-mismatch-is-twice-the-one-sided-invalid-count-and-lossless-cutoff-sets-its-peak/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — The fit is tight (max dev 1.3), but it is confirmed on one slope, one N and two offsets, and the Bernoulli control only shows the rule is not about density alone. It doesn't show that the rule holds for rotation-structured waves in general, which is how the rule of thumb is worded.
- Hidden assumption: The word's one-sided count is a pure function of the rotation (three-gap/Sturmian structure), so the closed form generalizes to any "rotation-structured" wave. The test only covered one slope, a = 1/phi, one length, N = 900, and two offsets, on a word whose symbol is a deterministic floor-difference. The count's dependence on a, N and the gate definition is assumed, not shown. "Validity-free" is also assumed to mean nothing beyond the gate affects the count.
- Would prove it wrong: A different slope, such as a = 1/sqrt(2) or a rational near 0.618, or a different N, where max deviation from N*min(x, 1-a) exceeds about 12 ticks. So would an offset b that moves the plateau off 229, or a symmetric count that isn't twice the one-sided count at lags where x is near 0.5.
- Break scenario: Keep density at 0.618 but swap the rotation: a = 0.618 from a non-golden continued fraction (e.g. [0;1,1,1,1,2,...]) or a quasi-periodic word with a small perturbation (flip 1% of symbols). Run lags 1..144 at N = 900 and 9000. If the closed form is really about rotation distance, deviation should grow smoothly with the perturbation. If it jumps, the rule is fitted to the golden case.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 93d9ec3722a3
- Polarity: compatible
- Distinct from: fibonacci-gate-drop-is-rotation-proximity-not-fibonacci-lags/E1 - that entry reports a 0.98 correlation of the dip with distance to an integer; this one gives the exact per-lag curve N times min(x, 1 minus density), its 229 plateau and a max deviation of 1.3 ticks, which that entry does not state.
- Sandbox: sandboxes/2026-10-18__fibonacci-gate-curve-is-the-circle-form-of-the-periodic-min-formula.py
- Prediction: Maximum deviation of the one-sided count from N min(x, 1-rho) at most 12 for both offsets over lags 1 to 144; symmetric within the lag bound of twice one-sided; plateau of 229 within 12 on lags with x at least 0.382; Bernoulli more than 100 off the curve at lag 55.
- Observed: RESULT: PASS circle curve N*min(x,1-rho) max dev 1.1 / 1.3 over lags 1..144, plateau (68 lags) max dev 0.8, sym bound violations 0, Bernoulli dev at lag 55 >= 190
- Scenarios: 1) offset 0 lags 1..144; 2) offset 0.31 lags 1..144; 3) plateau lags with x at least 0.382; 4) BREAK: 10 Bernoulli seeds of equal density at the dip lag 55
- Link: scheduled brain train auto loop 2 pass 2; session_014AVjf81yxBZXZ5b84ovVC5
- Cited-by: 2026-10-18 · projects/local__lossless-cutoff-on-golden-rotation-is-max-lag-and-sums-the-circle-curve.md#E1 · compatible · sandboxes/2026-10-18__lossless-cutoff-on-golden-rotation-is-max-lag-and-sums-the-circle-curve.py · observed RESULT: PASS lossless cutoff 144 on both offsets, cutoff 21 loses valid presses (1654, 1653), summed circle curve within 0.52 ticks per lag, cumulative 131, 150, 157, 161, 164 (b 0), Bernoulli off the curve in 10/10 seeds. · scheduled brain train auto loop 1 pass 5; session_01FjbQokSDjejDZsbW36mBhq
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E452 · compatible · sandboxes/2026-10-18__circle-min-formula-caps-at-n-times-min-density-and-complement-so-low-density-rotations-saturate-early.py · observed RESULT: PASS new form N*min(x,a,1-a) max err 1.1/1.6/2.0/0.9 ticks; old N*min(x,1-a) err 319/76 at a=0.142,0.414 (phi 1.1); periodic True · brain train auto pass 5, session_01K8wZ3EDWp7o2YCk1kac5LF
