# local/sandbox-combined-brain-builder-waiting-city-smoothness-blind-to-zero-variance — lessons

Project: local/sandbox-combined-brain-builder-waiting-city-smoothness-blind-to-zero-variance. Newest first.

---

## E1 — sandbox combined brain builder waiting city smoothness blind to zero variance
- Date: 2026-08-29
- Project: local/sandbox-combined-brain-builder-waiting-city-smoothness-blind-to-zero-variance
- Tags: [balance][testing][gamedesign][method]
- What: A deterministic sandbox (fixed win-rate tables, no RNG, no wall-clock) evaluating monotonicity, brain-builder#E5's prescribed smoothness assertion, and waiting-city#E5's variance check against three difficulty curves: E5's own reported step-function pathology, its reported AoE fix, and that fix extended into a zero-variance region.
- Why built: brain-builder#E5 diagnoses a step-function difficulty curve and prescribes asserting SMOOTHNESS rather than monotonicity, "since a step function is monotonic." waiting-city#E5 separately warns that extending a mechanic into a case producing no variance is relabeling, not rewarding. This tests whether E5's upgraded assertion also covers waiting-city#E5's pathology, or whether a flat (maximally smooth) dead region slips through the very assertion introduced to catch a curve-shape problem.
- Design: Three curves scored by three instruments. The smoothness threshold was calibrated so brain-builder#E5's OWN reported fix (the AoE curve, max_step 0.63) passes — an uncalibrated threshold would have failed the known-good curve and made the comparison meaningless. Variance is measured over the extended tail region specifically, not the whole curve.
- Got right: Calibrating the smoothness threshold against E5's reported working curve rather than picking a round number; the first run used 0.45 and rejected E5's own fix, which would have produced a false result about the assertion's coverage.
- Where/why it failed: The zero-variance extension passes both assertions cleanly — monotonic True, smooth True at max_step 0.63 (the flat tail contributes steps of 0.00, so appending it cannot ever increase max_step) — while the extended region carries variance 0.000000. brain-builder#E5's smoothness instrument is structurally incapable of detecting waiting-city#E5's pathology, because appending a flat segment strictly improves every smoothness metric it defines.
- Fix: Run waiting-city#E5's variance check per-region alongside brain-builder#E5's smoothness assertion, and require any newly-extended region of a curve to demonstrate nonzero variance in its own right — a global smoothness pass over the whole curve must not be read as coverage of a newly-added segment.
- Why this fix: The two instruments fail in opposite directions on the same artifact: smoothness penalizes large steps and therefore rewards flatness, while the pathology waiting-city#E5 names IS flatness. Adding a dead region to a curve makes it score BETTER on smoothness, so the metric does not merely miss the defect — it actively counts it as an improvement, which is why a single global assertion cannot be tightened into covering both.
- Rule of thumb: brain-builder#E5's smoothness assertion rewards flatness, so it scores waiting-city#E5's zero-variance dead region as an improvement rather than a defect — sandbox-confirmed a curve extended with a flat tail passes monotonicity and smoothness unchanged at variance 0.000000; assert nonzero per-region variance separately whenever a curve gains a new segment.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/sb8/s.py), including a first run whose 0.45 smoothness threshold incorrectly rejected brain-builder#E5's own reported AoE fix (max_step 0.63), recalibrated to 0.65 so the known-good curve passes; confirmed the step-function curve is monotonic but not smooth (correctly caught), and the zero-variance extension passes both assertions at tail variance 0.000000. brain-builder#E5 and the-game-the-waiting-city#E5 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__brain-builder/E5, pappydapimp69__the-game-the-waiting-city/E5
- Link: session_014mRpopK9xnhvk35tT8ozkX

