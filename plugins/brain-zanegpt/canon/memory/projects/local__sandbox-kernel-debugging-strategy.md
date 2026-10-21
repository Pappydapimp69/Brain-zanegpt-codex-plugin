# local/sandbox-kernel-debugging-strategy — lessons

Project: local/sandbox-kernel-debugging-strategy. Newest first.

---

## E2 — bisect skip candidate set is 2s ambiguous iid but clusters trade rate for size
- Date: 2026-10-12
- Project: local/sandbox-kernel-debugging-strategy
- Tags: [debugging][git][regression][algorithm]
- What: Tested bisection when some commits cannot be built or tested (git bisect skip). The search
  then ends on a candidate range, not one commit: everything after the last tested-good commit up
  to the first tested-bad one. With i.i.d. skips at rate s the range held more than one commit
  2s - s^2 of the time (0.195 at s=0.10) with mean size 1 + 2s/(1-s), for n from 64 to 5000 and
  for three different ways of choosing which testable commit to try next.
- Why built: The bisection kernel and debugging-strategy/E1 cover a flaky test and a masked bug,
  both assuming every commit can be tested. Real histories have broken builds, and nothing in
  Brain said how often skipping turns the answer into a range, or whether the way the next
  commit is picked around a skipped one changes the answer.
- Design: Commits 0..n, 0 good, n bad, first bad t uniform. Skipped commits drawn i.i.d. at
  s = 0.05, 0.10, 0.20 (n=1000, 3000 seeded trials each), and at s=0.10 for n=64 and 5000.
  Three skip policies on the same history: testable commit nearest the midpoint (git-like), a
  random testable commit, and the first testable at or above the midpoint. Scope scenario: skips
  in runs of 10 (a broken-build stretch) at about the same skipped fraction.
  It also reran E1's no-skip worst case (ceil(log2 n) = 10 tests for n=1000) and treated a skipped
  commit as a search with detection 0, checking that its share of a two-commit range stays at its
  prior as the search-theory kernel says an undetecting search should leave it.
- Got right: Predicting the exact formula from where the range must end: the final range is fixed
  by the testable commits on either side of t, so any bisection that runs until only skipped
  commits remain must land on the same range. All three policies gave identical ranges in every
  trial; only their test counts differed (9.80 nearest-midpoint vs 12.69 random at s=0.10).
- Where/why it failed: The bound held, but the premise behind it (skips add tests) was backwards: with fewer
  testable commits nearest-midpoint used FEWER tests (9.97 at s=0, 9.80 at 0.10, 9.59 at 0.20).
  Skipping costs no tests; it costs a definite answer. And the i.i.d. formula does not carry to
  clustered skips: runs of 10 at skipped fraction 0.091 gave ambiguity 0.102 (formula 0.174) but
  mean range size 2.040 (formula 1.201), because one broken stretch next to t hands back the
  whole stretch.
- Fix: Count a skip-ended bisect result as a range and report its size. Estimate how often that
  happens from the skip pattern, not just the skip fraction: scattered skips give frequent small
  ranges (about 2s), a broken-build stretch gives rare, wide ones (about its length). When a
  range comes back, build-fix the commits in it or test them in a patched tree; choosing a
  different next commit does not shrink it.
- Why this fix: The range is set by the history (where the skipped commits sit next to the
  bug), not by the search, so effort spent tuning the pick order only changes test count. The
  only lever on ambiguity is making the skipped commits testable.
- Rule of thumb: Untestable commits do not make bisection take more tests; they turn its answer
  into a range set only by the skips next to the bug. Scattered skips at rate s give a range 2s-s^2
  of the time (0.195 at s=0.10, mean 1.23 commits) whatever pick order is used; a 10-commit broken
  stretch gives a range less often (0.102) but twice as wide (2.04).
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry: 3000 seeded
  trials per configuration, all three pick orders returned identical ranges in every trial, and
  the true first-bad commit was inside the range in every trial. Assumptions are separate: the
  test is deterministic and monotone here (flakiness is debugging-strategy/E1's ground), and real
  broken builds may be neither i.i.d. nor fixed-length runs.
- Composed: ideas:DEBUGGING/strategy/bisection/bisect-narrows-a-search-space-logarithmically, sandbox-kernel-debugging-strategy/E1, ideas:SEARCH-THEORY/bayesian-search/a-failed-search-lowers-a-cell-by-1-minus-POD-it-does-not-clear-it
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__bisect-skip-candidate-set-is-2s-ambiguous-iid-but-clusters-trade-rate-for-size.py
- Prediction: Written before the first run: i.i.d. ambiguity 2s - s^2 (0.0975, 0.190, 0.360 for
  s = 0.05, 0.10, 0.20, within 0.01) and mean range 1 + 2s/(1-s) (1.105, 1.222, 1.500, within
  0.03); identical ranges across the three pick orders; extra tests under 1 at s=0.10; clustered
  runs of 10 at s about 0.1 give ambiguity about 0.11 and mean size about 2.0.
- Observed: RESULT: PASS iid skip ambiguity tracks 2s-s^2 and size 1+2s/(1-s) for all 3
  policies (sets identical); clustered s~0.1 amb=0.102 size=2.040. Ambiguity 0.0933/0.1947/0.3600
  and size 1.100/1.229/1.506 for s=0.05/0.10/0.20; n=64 0.1917, n=5000 0.1960; tests at n=1000
  9.97 (s=0), 9.89, 9.80, 9.59 nearest-midpoint, 12.6 to 13.0 random; same-range 1.0000 in all.
  Worst case with no skips 10 tests for n=1000 over every t; in 805 two-commit ranges at s=0.20
  the bug sat in the first slot 0.511 of the time (prior 0.5).
- Scenarios: 1) no skips, n=1000, baseline test count; 2) i.i.d. skips s=0.05/0.10/0.20 under
  three pick orders, the random order built to BREAK the claim that the range is
  path-independent; 3) s=0.10 at n=64 and n=5000 for n-independence; 4) clustered skips in runs
  of 10 at skipped fraction 0.091, the scope case where the i.i.d. formula fails; 5) where the
  bug sits inside two-commit ranges at s=0.20, checking a skipped commit keeps its prior share
- Link: session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB

## E1 — bisection log2 count assumes a monotone deterministic test
- Date: 2026-09-28
- Project: local/sandbox-kernel-debugging-strategy
- Tags: [debugging][git][regression][algorithm]
- What: Applied the ideas kernel that bisection narrows a good..bad range by half per test, citing git's example of 675 revisions in roughly 10 steps. The step count reproduced exactly; the result is only right while the test is deterministic and the bug stays present once introduced.
- Why built: brain train gap listed the kernel as unapplied, and brain query bisect returned no memory entries. The kernel itself marks the logarithmic behaviour as inferred rather than stated.
- Design: Bisection over histories of n commits with good at 0 and bad at n, checked against every first-bad position (sampled for large n). Then n=676 with a flaky test that reads a bad commit as good with probability p (0.01, 0.05, 0.10), 4000 seeded trials each, single verdict versus best-of-3 vote. Then 19920 non-monotone histories where the bug appears at a, is masked at b and returns at c.
- Got right: Measuring wrong answers rather than step counts once the test was flaky. The step count barely changes (9.3 to 9.5 tests), so a step-count check alone would call the flaky runs fine.
- Where/why it failed: With an exact test, worst-case tests were exactly ceil(log2 n): 10 for 676, 14 for 10000, 17 for 100000, against 675, 9999 and 99999 for a linear scan. A flaky test named the wrong commit 4.2% of the time at p=0.01, 20.3% at 0.05 and 37.7% at 0.10, because one wrong verdict discards the half holding the answer and nothing later recovers it. Best-of-3 cut these to 0.1%, 3.1% and 11.4% at three times the test runs. On the masked histories bisection returned the reintroduction c in 50.3% of cases and the true introduction a in 49.7%.
- Fix: When the test is flaky, vote each verdict (best-of-3 measured here). Treat a bisect result as one good-to-bad transition, not the first one, whenever the bug could have been masked and come back.
- Why this fix: Bisection makes each verdict final, so its error rate compounds with the number of steps instead of averaging out. Voting per step pays linearly in test runs to cut that compounding.
- Rule of thumb: Bisection's ceil(log2 n) tests (10 for 676 commits, 17 for 100000) hold only for a deterministic, monotone test: a test that misreads a bad commit 5% of the time names the wrong commit 20.3% of the time (best-of-3 votes: 3.1%), and when the bug was masked and came back it names the reintroduction instead of the introduction about half the time (50.3%).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b02.py loop 7 in Pappydapimp69/Brain, deterministic seeded trials. Observed: worst-case tests equal ceil(log2 n) for n from 10 to 100000; wrong-commit rates 4.2/20.3/37.7% single and 0.1/3.1/11.4% best-of-3; masked histories 49.7% a, 50.3% c. Assumed: the flake model (bad reads good only) is a simplification; real flaky tests can also misread good commits.
- Composed: ideas:DEBUGGING/strategy/bisection/bisect-narrows-a-search-space-logarithmically
- Link: session 2026-09-28, brain train gap batch 2 loop 7
- Sandbox: sandboxes/2026-09-28__train-gap-b02.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-debugging-strategy.md#E2 · compatible · sandboxes/2026-10-12__bisect-skip-candidate-set-is-2s-ambiguous-iid-but-clusters-trade-rate-for-size.py · observed RESULT: PASS iid skip ambiguity tracks 2s-s^2 and size 1+2s/(1-s) for all 3 policies (sets identical); clustered s~0.1 amb=0.102 size=2.040. Ambiguity 0.0933/0.1947/0.3600 and size 1.100/1.229/1.506 for s=0.05/0.10/0.20; n=64 0.1917, n=500… · session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB
