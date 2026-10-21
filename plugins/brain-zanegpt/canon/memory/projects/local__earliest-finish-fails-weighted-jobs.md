# local/earliest-finish-fails-weighted-jobs — lessons

Project: local/earliest-finish-fails-weighted-jobs. Newest first.

---

## E1 — earliest finish fails weighted jobs
- Date: 2026-10-15
- Project: local/earliest-finish-fails-weighted-jobs
- Tags: [algorithm][scheduling][sandbox][testing]
- What: Earliest-finish greedy, never beaten for fitting the most jobs, was optimal for total weight
  on only 38.5% of 20,000 small weighted instances; heaviest-first reached 85.7% and weight
  per length 66.4%, while the standard weighted-interval DP matched the brute-force optimum on
  100%.
- Why built: Weakest-link train pick: the activity-selection kernel proves earliest finish for counting
  jobs; real schedules weigh jobs (pay, priority), and the kernel's 'only safe greedy' framing
  invites reusing it there.
- Design: 20,000 six-job instances from a deterministic LCG (start 0-11, length 1-6, weight 1-9).
  Exhaustive bitmask optimum for count and for total weight; greedies by earliest finish,
  highest weight, highest weight/length; weighted DP sorted by finish with binary search for
  the last compatible job.
- Got right: Re-verified the kernel on the same instances: earliest finish was optimal for job count on
  100%, and the DP that generalises it (take or skip each job in finish order) is exact for
  weights.
- Where/why it failed: No greedy order is safe once jobs carry weights: earliest finish fell to 38.5%, heaviest-
  first, the best greedy, still missed 14.3% of instances, and weight/length 33.6%, because
  one heavy long job can be worth more than several short ones and greedy commitments cannot
  be undone.
- Fix: Use earliest-finish greedy only when every job counts the same; for weighted jobs use the
  O(n log n) weighted-interval DP (sort by finish, binary search, take-or-skip), which costs
  barely more than the greedy.
- Why this fix: The exchange argument behind earliest finish needs every job to be interchangeable; weights
  break it, while the DP's recurrence keeps both branches and so is exact for any weights.
- Rule of thumb: Earliest-finish greedy is only safe for unweighted jobs: with weights it was optimal on
  38.5% of instances (best greedy 85.7%); use the weighted-interval DP instead.
- Provenance (verified/assumed): Verified first-hand by the sandbox below against an exhaustive optimum; small instances only
  (six jobs); the LCG distribution is my choice.
- Composed: ideas:ACTIVITY-SELECTION/interval-scheduling
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__earliest-finish-fails-weighted-jobs.py
- Prediction: Written before running: unweighted earliest finish optimal on 100%; weighted earliest finish
  under 70% and no greedy above 90%; DP 100%.
- Observed: RESULT: PASS unweighted earliest-finish optimal 100.0%; weighted: earliest-finish 38.5%,
  heaviest-first 85.7%, weight/length 66.4%, DP 100.0%.
- Scenarios: 1) unweighted count (re-verifies the kernel); 2) weighted, three greedy orders, built to
  find any safe greedy; 3) weighted DP against brute force.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E375 · compatible · sandboxes/2026-10-17__earliest-finish-optimality-vs-weight-spread.py · observed RESULT: PASS earliest-finish optimal 100.0% at W=1, 64.3% at W=2, 38.4% at W=9; length-tied weights 24.6%, inverse-length 59.8% · brain train auto loop 2 pass 2; session_01LG4GQFTi9A1QxnCzb5c6CV
