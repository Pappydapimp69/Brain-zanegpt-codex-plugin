# local/dilution-best-step-count-grows-with-pipette-constant — lessons

Project: local/dilution-best-step-count-grows-with-pipette-constant. Newest first.

---

## E1 — dilution best step count grows with pipette constant
- Date: 2026-10-17
- Project: local/dilution-best-step-count-grows-with-pipette-constant
- Tags: [lab-dilution][sandbox][numerics][model]
- What: A worst-case error sweep for a 1000-fold dilution in n equal-factor steps (n 1 to 8) as the pipette small-volume constant a grows from 0 to 2 uL. The best step count is 1 at a=0, 2 for a from 0.02 to 0.2, 3 at a=0.5, 4 at a=1.0 and 6 at a=2.0, so the earlier rule that extra steps beyond two only add error holds only up to about a=0.2.
- Why built: The earlier dilution lesson was failed in audit because its rule of thumb reached beyond the swept range of a. This sandbox tests the rule outside that range and records exactly where it stops holding.
- Design: Per step relative error is max(0.005, a/volume) for the transfer plus the same for the diluent scaled by its fraction of a 1000 uL final volume, summed over n steps of equal factor 1000 to the 1/n. Eight values of a, n from 1 to 8, no randomness. The a=0.5 to 2.0 rows are the part built to BREAK the two-steps-is-enough rule.
- Got right: Rows at a=0 to 0.2 reproduce the earlier numbers (1.97 percent for two steps, 2.85 for three, 5.05 for six), so this model matches the stored lesson inside its tested range.
- Where/why it failed: The stored rule fails outside its range: at a=0.5 three steps give 2.85 percent against 4.13 for two, at a=1.0 four steps give 3.89 against 4.35 for three and 7.29 for two, and at a=2.0 six steps give 5.85 against 6.14 for four. The error of each step is capped by the floor, so once a/volume dominates, more steps keep paying.
- Fix: State the step-count rule as a function of a: one step at the pure floor, two steps while a is at most about 0.2 uL, and then one more step for each roughly doubling of a; compute the sum for the actual pipette.
- Why this fix: The sweep shows the optimum moving monotonically upward with a (1, 2, 3, 4, 6), which is the interior-optimum shape the earlier entry described but never followed past a=0.2.
- Rule of thumb: The best dilution step count rises with the small-volume constant (2 steps up to a=0.2 uL, 3 at 0.5, 4 at 1.0, 6 at 2.0 in this model), so two steps is a regime rather than a law; recompute for your own pipette.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the error model and every constant are assumptions and no real pipette was measured.
- Composed: local/2026-10-13__serial-dilution-step-count-worst-case-error-crossover-with-pipette-floor/E1, pappydapimp69__brainwork/E234
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__dilution-optimal-steps-grow-with-pipette-constant.py
- Prediction: Best equal-factor step count is 1 at a=0, 2 for a=0.05 to 0.2, 3 at a=0.5 and 4 at a=1.0. Assumption: the earlier model generalizes to larger a with the same floor; it would be wrong if two steps still won at a=0.5.
- Observed: RESULT: PASS best step count by a: {0: 1, 0.02: 2, 0.05: 2, 0.1: 2, 0.2: 2, 0.5: 3, 1.0: 4, 2.0: 6}
- Scenarios: 1) a=0 pure floor; 2) a=0.02 to 0.2 inside the earlier range; 3) a=0.5 (BREAK of the two-steps rule); 4) a=1.0; 5) a=2.0
- Link: session_01FKz3vbJ5KozVVes2fUyYJ8
- Audited: 2026-10-17 · modeled · Read the entry and reran its stored sandbox. The best step count is computed by a min over n of a summed error formula, not built in, and every figure quoted in the entry (1.97, 2.85, 5.05, 4.13, 4.35, 7.29, 3.89, 6.14, 5.85 percent) reproduced exactly; the tested range of a (0 to 2 uL) and n (1 to 8) covers what the Rule of thumb states. The caveat is that the claim concerns real pipettes, but only a hand-written error model with assumed constants was tested and the entry itself admits no pipette was measured, so the verdict is modeled rather than pass. · scheduled brain training run 2026-10-17, audit pass 3; session_01MUFH1b1Lc27PXz6rjHHodQ
- Cited-by: 2026-10-17 · projects/local__dilution-step-thresholds-are-not-one-per-doubling.md#E1 · incompatible · sandboxes/2026-10-17__dilution-step-thresholds-are-not-one-per-doubling.py · observed RESULT: FAIL best n is not monotone in a: peak 6 until a=3.69, then 5 at a=20; first decrease at a=3.693 · brain train auto loop 1 pass 2, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1
