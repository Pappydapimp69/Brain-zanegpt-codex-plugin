# local/dilution-step-thresholds-are-not-one-per-doubling — lessons

Project: local/dilution-step-thresholds-are-not-one-per-doubling. Newest first.

---

## E1 — dilution step thresholds are not one per doubling
- Date: 2026-10-17
- Project: local/dilution-step-thresholds-are-not-one-per-doubling
- Tags: [lab-dilution][sandbox][numerics][model]
- What: Sandbox sweeping the small-volume constant a from 0.001 to 20 uL in 0.001 steps for a 1000-fold dilution in n equal-factor steps (n 1 to 8), recording where the best step count changes and whether it keeps rising with a.
- Why built: The grows-with-pipette-constant lesson ends with a fix of one more step per roughly doubling of a, and the crossover lesson claims two steps beat one near a=0.024; I wanted the exact switch points and the behaviour past the a=2 row that was last tested.
- Design: Same worst-case model as both source lessons (floor 0.5 percent, a/volume for transfer and diluent, diluent scaled by its fraction of 1000 uL), best n by minimum summed error, 20000 values of a, no randomness. I first tried bisection for the switch points, which silently failed, and replaced it with a full grid scan.
- Got right: Switch points were 1 to 2 steps at a=0.015, 3 steps at 0.298, 4 at 0.765, 5 at 1.213 and 6 at 1.925 uL, matching the stored 0.0145 correction and the stored best counts at a=0.5, 1.0 and 2.0.
- Where/why it failed: My prediction of a monotone climb was wrong. The best step count peaks at 6 up to a=3.69 uL and then falls to 5 and stays there to a=20 (a=4: 5 steps 9.96 percent vs 9.99 for six), because for large a every transfer is volume-limited and the extra steps only add error. The ratios between successive switch points were 20.3, 2.6, 1.6 and 1.6, so one step per doubling is not the pattern either.
- Fix: State the step-count rule as a table of switch points (0.015, 0.30, 0.77, 1.2, 1.9 uL) with a cap near 6 steps, and say the rule stops rising beyond a of about 3.7 uL; do not extrapolate it past the swept range.
- Why this fix: Past a of about 3.7 uL, relative error is set by a/volume in every step, so total error is nearly proportional to a and the optimum is the step count that minimizes the sum of the transfer and diluent volume fractions, not a function of the floor.
- Rule of thumb: The best dilution step count is not monotone in the pipette constant (1 step to 0.015 uL, then 2, 3, 4, 5, 6 up to 3.69 uL, then 5 to 20 uL in this model), so grows-with-a describes a regime that ends; compute the table, and expect a plateau rather than a ladder.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the error model and constants are assumptions copied from the source lessons, no real pipette was measured.
- Composed: local/2026-10-13__serial-dilution-step-count-worst-case-error-crossover-with-pipette-floor/E1, dilution-best-step-count-grows-with-pipette-constant/E1, brainwork/E234
- Picked-by: current-half
- Distinct from: dilution-best-step-count-grows-with-pipette-constant/E1 - that entry stops at a=2 uL and says the best step count only rises; this one sweeps to 20 uL on a 0.001 grid, gives the exact switch points and finds the count peaks at 6 until 3.69 uL and then falls to 5.
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__dilution-step-thresholds-are-not-one-per-doubling.py
- Prediction: Switch points near 0.0145, 0.3, 0.7, 1.3 and 1.8 uL with a monotone climb in n; assumed the model generalizes past a=2 with the same floor, and a decline in n would prove that wrong.
- Observed: RESULT: FAIL best n is not monotone in a: peak 6 until a=3.69, then 5 at a=20; first decrease at a=3.693
- Scenarios: 1) fine grid a=0.001 to 20 uL; 2) first-appearance table for n=2 to 6 compared with the stored crossovers; 3) BREAK: the a above 2 uL region, built to test whether the ladder keeps climbing
- Link: brain train auto loop 1 pass 2, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1

