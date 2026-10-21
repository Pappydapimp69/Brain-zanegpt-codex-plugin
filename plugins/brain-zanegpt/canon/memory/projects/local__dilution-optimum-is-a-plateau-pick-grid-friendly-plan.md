# local/dilution-optimum-is-a-plateau-pick-grid-friendly-plan — lessons

Project: local/dilution-optimum-is-a-plateau-pick-grid-friendly-plan. Newest first.

---

## E1 — dilution optimum is a plateau pick grid friendly plan
- Date: 2026-10-17
- Project: local/dilution-optimum-is-a-plateau-pick-grid-friendly-plan
- Tags: [lab-dilution][sandbox][numerics][model]
- What: For a two-step 1000-fold dilution at small-volume constant a=0.1 uL, the worst-case random error is a plateau of 1.97 percent for 20x50, 25x40, 31.6x31.6, 40x25 and 50x20, with 10x100 and 100x10 worse at 2.45. Forcing the pipette onto a whole-microlitre grid adds a systematic factor error only to the non-round plan: 31.6x31.6 rises from 1.97 to 4.31 percent (2.34 percent systematic), while 20x50 and 25x40 stay at 1.97 because their transfers (50, 40, 20 and 25 uL) are whole.
- Why built: The earlier step-count lesson found the best split near 32-fold steps and the audit showed that lesson was fragile. I wanted to see whether a volume resolution that the model ignored would change the recommended split.
- Design: Same floor model as the earlier lesson (relative error max(0.005, a/volume) for transfer plus diluent share), seven two-step plans whose factors multiply to 1000, transfers rounded to a grid of 0, 1 and 5 uL, delivered factor product compared with 1000 as systematic error added to the random bound. Scenarios: continuous, 1 uL grid, 5 uL grid (the last built to BREAK the claim that a plateau plan stays free). No randomness.
- Got right: The plateau is real: five plans tie at 1.97 percent in the continuous model, so a recommendation of 32x32 was an arbitrary point on a flat set rather than a sharp optimum.
- Where/why it failed: My prediction was that the grid would push the best plan to 10x100; it did not, the best stays among the plateau plans because they stay exact on the grid. The prediction also assumed 32x32 was optimal, but 32x32 is 1024-fold, which is not a 1000-fold plan at all; the exact balance 31.6x31.6 is not whole in microlitres.
- Fix: Pick, from the plateau of near-equal random-error plans, one whose transfer volumes are whole on the pipette grid (here 20x50 or 25x40), and compute the delivered factor rather than the intended factor.
- Why this fix: The random-error bound is flat across the plateau while the rounding error is not, so the grid is the tie-breaker; the 5 uL grid shows it dominates for the round-number-hostile plan (13.08 percent for 31.6x31.6, 1.97 for the rest).
- Rule of thumb: The best two-step dilution split is a plateau (1.97 percent for 20x50 to 50x20 at a=0.1) rather than a point, so choose the plan whose transfers are whole on the pipette's volume grid; the balanced square-root split lost to rounding (4.31 percent at 1 uL, 13.08 at 5 uL).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the error model, constant a=0.1 and the grid values are assumed and no real pipette was measured.
- Composed: local/2026-10-13__serial-dilution-step-count-worst-case-error-crossover-with-pipette-floor/E1, pappydapimp69__brainwork/E234
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__dilution-volume-grid-forces-integer-plans.py
- Prediction: At a=0.1 the continuous best is the balanced square-root split; on a 1 uL grid its systematic error pushes the best plan to 10x100 (or 20x50). Assumption: the balanced split is a unique optimum; a tie among several plans would prove it wrong.
- Observed: RESULT: FAIL best plan continuous (20, 50), 1 uL grid (20, 50), 5 uL grid (20, 50); 31.6x31.6 error 1.97 -> 4.31 (a tie among five plans, 10x100 never best)
- Scenarios: 1) continuous volumes; 2) 1 uL grid; 3) 5 uL grid (BREAK: round-number-hostile plan gets 13.08 percent)
- Link: session_01FKz3vbJ5KozVVes2fUyYJ8
- Audited: 2026-10-17 · modeled · Read the entry and reran its stored sandbox. The best plan is computed by a min over seven candidate splits at grid 0, 1 and 5 uL, not built in, and the quoted figures (1.97, 2.45, 4.31 with 2.34 systematic, 13.08 percent) reproduce exactly; the tested scope (two steps, a=0.1, whole-uL grids) matches what the Rule of thumb states. Two points: the script's final line reads RESULT: FAIL because it asserts the original wrong prediction, which the entry discloses but a reader of the script alone could misread as a failed claim; and the claim concerns real pipette volume grids while only an assumed error model with no measured pipette was tested, so the verdict is modeled rather than pass. · scheduled brain training run 2026-10-17, loop 2 audit pass 3; session_01MUFH1b1Lc27PXz6rjHHodQ
