# local/sandbox-sentinel-and-failfast-coverage-sweep — lessons

Project: local/sandbox-sentinel-and-failfast-coverage-sweep. Newest first.

---

## E1 — sentinel and failfast coverage sweep
- Date: 2026-09-30
- Project: local/sandbox-sentinel-and-failfast-coverage-sweep
- Tags: [testing][state][determinism]
- What: Sandbox composing the no-winner sentinel lesson from the combat sandbox with the fail-fast sweep truncation lesson from the edges sandbox, on one coverage sweep over twelve cases.
- Why built: Both lessons are about a per-case sweep silently misreporting its aggregate, one through a coerced sentinel and one through early abort, and their combined effect on a single tally was untested.
- Design: Deterministic, no RNG. Twelve cases each score four options; cases 3, 7 and 10 have all-zero scores so no winner (None), and case 5 raises a divergent error. Three tallies: naive with fail-fast, naive continuing, and guarded (sentinel counted as its own category, errors counted, loop continues). A no-sentinel world is the breaker.
- Got right: Guarded processed 11 cases and reported 4 distinct winners, 3 no-winner and 1 error. Naive continuing reported 5 distinct because the sentinel was coerced into a phantom member. Naive fail-fast stopped at case 5 having seen 5 cases, reporting 4 distinct including the phantom.
- Where/why it failed: The two bugs stack: the phantom member inflates coverage by one and the early abort discards the remaining 7 cases, so the naive fail-fast tally looked like healthy coverage of 4 while it had actually seen 3 real winners in 5 cases.
- Fix: Count the no-winner and error cases as their own categories, never coerce the sentinel into the set, and run the sweep to completion collecting errors instead of aborting on the first divergent case.
- Why this fix: The no-winner and divergent cases are the informative ones, and a tally that hides them or stops before them reports a success that was not measured.
- Rule of thumb: A coverage sweep needs three separate counters (winners, no-winner, errors) and must not abort at the first divergence; the naive tally here read 5 distinct against the true 4 and the fail-fast one saw only 5 of 12 cases.
- Provenance (verified/assumed): Verified first-hand by running the sandbox and copying its counts; one twelve-case synthetic sweep, real combat data and real shell loops not run.
- Composed: sandbox-dbz-combat/E3, sandbox-edges/E2
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__sentinel-and-failfast-coverage-sweep.py
- Prediction: naive fail-fast processes 5 of 12 cases, naive continuing reports 5 distinct including a phantom None against a true 4, guarded reports 11 cases with 3 no-winner and 1 error.
- Observed: RESULT: PASS naive tally counts phantom 'None' (distinct 5 vs true 4) and fail-fast covers 5 of 12 cases; guarded covers 11 with no_winner=3 errors=1
- Scenarios: 1) naive fail-fast 2) naive continuing with coerced sentinel 3) guarded with separate counters 4) world with no no-winner cases built to break the claim that the coercion always inflates coverage
- Link: scheduled train pass 5
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__sentinel-failfast-sweep-rebuild.py · observed RESULT: PASS guarded sweep accounts 15/15 (distinct=3 no_winner=3 errors=1); naive continuing reads 4 vs true 3; fail-fast saw 7/15; inflation is +1 only when a sentinel exists AND coerces to a non-colliding value (int-0 coercion reads 3==true while hiding 3 no-winner cases); truncation cost depends on error position (last: 15/15, first: 1/15) · Rebuilt from What / Rule of thumb / Prediction only, with my own fixture: 15 cases over 5 int-indexed options (winners cycle over 3 of them), no-winner (all-zero) cases at 2, 8 and 13, a divergent case at 6, a custom Divergent exception, and None kept as a raw value rather than str-coerced. The rule holds. The guarded sweep with three counters accounts for 15/15 cases (3 winners, 3 no-winner, 1 error). Naive-continuing reads one phantom distinct (4 vs a true 3). Fail-fast stops at the divergence (7/15 seen including the failing case). I then pushed on the entry's specific numbers. (a) In a world with no sentinel cases, naive equals the truth, which agrees with the entry's own breaker. (b) If the sentinel coerces to a value that collides with a real winner (None->0), distinct does NOT inflate. Naive then reads 3 == true while silently booking 3 no-winner cases as winner 0, so the "+1 phantom" symptom is fixture-specific. The underlying failure is worse because it is invisible, which strengthens the need for a separate no-winner counter. (c) The cost of truncation depends on where the divergence falls: 15/15 if it is last, 1/15 if it is first. So "saw 5 of 12" is a property of the fixture, not of fail-fast in general. Differences from the original sandbox (opened after the run): it uses 12 cases, 4 letter options, ValueError, str() coercion, and divergence at index 5. Its fail-fast count of 5 counts only successful cases before the abort, while mine counts cases attempted (7, including the error). Its breaker checks only the no-sentinel world and never tries a colliding coercion or other error positions. · session; brain train rebuild pass round 2; session_01QGT1LfmPHPG99JEGaPhBwB
