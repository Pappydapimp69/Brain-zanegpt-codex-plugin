# local/sandbox-combined-august-10-test-e29-names-the-axis-e8-leaves-to-judgement — lessons

Project: local/sandbox-combined-august-10-test-e29-names-the-axis-e8-leaves-to-judgement. Newest first.

---

## E1 — sandbox combined august 10 test e29 names the axis e8 leaves to judgement
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-test-e29-names-the-axis-e8-leaves-to-judgement
- Tags: [testing][database][method][correctness]
- What: A deterministic sandbox (fixed mutation schedules, no RNG) paginating a 50-item set with OFFSET under four mutation loads — balanced churn, insert-skewed, delete-skewed, and balanced churn at ten times the volume — counting duplicated and skipped rows.
- Why built: august-10#E29 records that OFFSET pagination corrupts as an exact function of NET shift before the cursor, so balanced insert/delete traffic is always perfectly correct and realistic mixed-load testing is the test that passes, prescribing skewed mutations to reproduce. test#E8 records that a comparative test gives a false tie unless inputs are adversarial to the baseline. This tests the relationship between the general rule and the specific one.
- Design: Five pages of ten over fifty items, with per-page mutations applied before the cursor. Balanced churn inserts and deletes equally; skewed loads do one or the other; heavy balanced churn multiplies the volume tenfold while keeping net shift at zero.
- Got right: A first construction paginated only half the set and reported 50 skipped rows in every load, which measured coverage rather than corruption; restricting the item count so pagination covers the whole set isolated the actual defect.
- Where/why it failed: Balanced traffic yields 0 duplicates and 0 skipped rows at both normal and tenfold volume — churn volume is not the variable. Insert-skewed traffic yields 12 duplicates and 15 skipped; delete-skewed yields 7 skipped. The intuitive way to strengthen a test, scaling realistic mixed load up, moves along an axis that changes nothing.
- Fix: Construct pagination tests from net cursor shift rather than from churn volume or realism, and generalise the habit: when test#E8 calls for an adversarial input, identify the axis the failure is an exact function of before generating load.
- Why this fix: test#E8 states that inputs must be adversarial but leaves the choice of axis to the tester, which is where the difficulty actually lives — a tester who scales realistic load tenfold has followed E8's instruction as they understand it and learned nothing. august-10#E29 supplies the missing half for this defect by naming the exact function (dups = max(0, ins-del), skipped = max(0, del-ins)), which makes the adversarial axis derivable rather than guessed.
- Rule of thumb: august-10#E29 is a worked instance of test#E8 that supplies the part E8 leaves to judgement — WHICH axis to skew; sandbox-confirmed balanced pagination churn is perfectly correct at both normal and 10x volume (0 dups, 0 skipped) while insert-skewed yields 12 dups and 15 skipped, so derive the adversarial axis from the function the failure follows, never from realism or volume.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b15/l33.py), including a first construction whose skipped metric measured pagination coverage rather than corruption; confirmed balanced loads yield (0, 0) at both volumes while insert-skewed yields (12, 15) and delete-skewed (0, 7). august-10#E29 and test#E8 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E29, pappydapimp69__test/E8
- Link: session_014mRpopK9xnhvk35tT8ozkX

