# local/fibonacci-gate-invalid-count-scales-linearly-with-horizon-while-random-drifts — lessons

Project: local/fibonacci-gate-invalid-count-scales-linearly-with-horizon-while-random-drifts. Newest first.

---

## E1 — fibonacci gate invalid count scales linearly with horizon while random drifts
- Date: 2026-10-18
- Project: local/fibonacci-gate-invalid-count-scales-linearly-with-horizon-while-random-drifts
- Tags: [gamedev][input][state][testing]
- What: On a Fibonacci-word legality signal the gate-only invalid count at the dip lags 55, 89 and 47 grows linearly with the horizon N (counts 5, 10, 20, 39 at N 600, 1200, 2400, 4800 for lag 55), deviating from a straight line by at most 0.5 presses, while a density-matched Bernoulli signal deviates by more than 3 in 17 of 20 seeds.
- Why built: Train pick joining the rotation-proximity dip with the lossless-cutoff-is-worst rule and the per-period-constant lesson, to see whether the per-period-constant invalid rate carries over from a periodic wave to a quasi-periodic one where no period exists.
- Design: Fibonacci word by substitution to 5530 ticks; invalid(L, N) counts t in 130..130+N-1 with legal at t-L and illegal at t; lags 55, 89 and 47 at N 600, 1200, 2400, 4800; line fitted from N 4800; dip checked against the median over lags 40 to 70 at each N; 20 seeded Bernoulli(0.618) signals as control.
- Got right: Fibonacci lags 55 and 47 stayed within 0.5 of the line and lag 89 within 0.0 across all four horizons, the dip stayed under a quarter of the window median at every N, and 17 of 20 random seeds drifted off the line by more than 3.
- Where/why it failed: My prediction allowed up to 3 presses of deviation for the Fibonacci word and the real value was 0.5, so the bound was loose, and 3 of the 20 random seeds stayed within the bound at lag 55, so the random control separates by tendency, not absolutely.
- Fix: Treat the gate-only invalid rate as a per-horizon constant on rotation signals too, so a count measured at one N predicts the count at another by scaling, and keep the per-lag scan for random legality where the count only follows in expectation.
- Why this fix: A rotation signal has bounded discrepancy, so counts of the legal-then-illegal pattern differ from N times the rate by a bounded amount, whereas a random signal's count differs by an amount growing with the square root of N.
- Rule of thumb: On a Fibonacci-word signal the gate-only invalid count scales with the horizon to within one press at lags 47, 55 and 89, so extrapolate it from a short run, but on random legality of the same density do not extrapolate an exact count.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session: one Fibonacci word, three lags, four horizons and 20 Bernoulli seeds; other rotation numbers and lags were not run.
- Composed: fibonacci-gate-drop-is-rotation-proximity-not-fibonacci-lags/E1, lossless-cutoff-is-worst-without-validity/E1, gate-invalid-count-is-per-period-constant-and-cutoff-scales-it-linearly/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the Bernoulli contrast is real but easy, since any Sturmian word is expected to scale linearly, and the rule is tested at one start offset with a self-anchored fit and no deterministic control, so "Fibonacci-specific, extrapolate from a short run" is not supported.
- Hidden assumption: Linear scaling of an invalid count is a property of the signal and lag. The counts are really tied to the Fibonacci word's quasi-periodic structure and the fixed start at t=130. A different offset, a different horizon grid, or a lag that is not a Fibonacci number (47 is Lucas) could break it, and the 130 start is not varied.
- Would prove it wrong: Shifting the window start (say 130 to 131, 177 or 1000), or fitting the line from N 600 instead of N 4800, gives deviations well above 1 press at lags 55, 89 or 47. Deviations that large would show the 0.5 result comes from one offset and one fit anchor. The fit is also circular, because the line is fitted from the N 4800 point it is judged against.
- Break scenario: Run lag 55, 89 and 47 over 20 or more start offsets (0 to 1000), fitting from N 600 and testing at N 4800, against a deterministic non-Fibonacci quasi-periodic control (an irrational rotation with a different slope, or a Sturmian word at another density). If the control also scales linearly within 1 press, the property is generic to low-complexity words, not specific to Fibonacci. If Fibonacci fails at other offsets, the rule is an artifact of the window. Either result removes the stated contrast with random legality.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest bda0b9c4b980
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__fibonacci-gate-invalid-count-scales-linearly-with-horizon-while-random-drifts.py
- Prediction: Fibonacci counts at lags 55, 89 and 47 deviate by at most 3 presses from the line fitted at N 4800, the dip stays under a quarter of the window median at every N, and at least 15 of 20 Bernoulli seeds deviate by more than 3 at lag 55.
- Observed: RESULT: PASS fib lag55/89/47 max dev 0.5, 0.0, 0.5; dip at every N True; Bernoulli deviation over 3 in 17 of 20 seeds. Counts lag 55: 5, 10, 20, 39; lag 89: 3, 6, 12, 24; lag 47: 28, 57, 114, 228.
- Scenarios: 1) Fibonacci lag 55 over four horizons; 2) Fibonacci lag 89; 3) Lucas lag 47; 4) 20 Bernoulli seeds at lag 55, built to break the claim by showing the same linear scaling on random legality
- Link: scheduled brain train auto loop 1 pass 2; session_01FjbQokSDjejDZsbW36mBhq
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E463 · incompatible · sandboxes/2026-10-18__fib-linear-scaling-is-generic-to-rotations-offsets-and-fit-anchor.py · observed RESULT: FAIL fib dev<=10.0 rot_sqrt2 dev<=9.0 bernoulli dev<=153.0 over 25 offsets fit at N600; lossless cutoff 89 == max valid lag 89 · brain train auto session 2026-10-18; session_017XK4iPJB1weWKi2R7K4DfL
