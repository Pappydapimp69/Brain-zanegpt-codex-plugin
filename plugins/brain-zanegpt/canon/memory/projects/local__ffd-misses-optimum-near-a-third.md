# local/ffd-misses-optimum-near-a-third — lessons

Project: local/ffd-misses-optimum-near-a-third. Newest first.

---

## E1 — first fit decreasing misses the optimum often when items cluster near a third
- Date: 2026-10-15
- Project: local/ffd-misses-optimum-near-a-third
- Tags: [algorithm][packing][testing]
- What: Applied the PACKING kernel (first-fit decreasing matched the optimum on 458 of 462 tiny multisets;
  expect it almost always optimal) beyond its tiny integer instances: random lists of 12 and 20 items
  at capacity 100 with two size distributions, and Johnson's adversarial mix.
- Why built: The kernel's 'almost always optimal' came from sizes 1 to 6 with six items, where few hard cases
  exist; the classic hard cases for first-fit decreasing need items near a third or a quarter of
  capacity, which tiny integers cannot express.
- Design: Seeded random lists. First-fit decreasing against the lower bound ceil(sum/C); for 12-item lists
  above the bound, an exact branch-and-bound optimum on 40 cases. Johnson's mix (6 x 51, 6 x 27, 6 x
  26, 12 x 23) checked against an explicit 9-bin packing, which meets the lower bound and so is
  optimal.
- Got right: Johnson's mix needs 11 bins under first-fit decreasing against an optimum of 9 (ratio 11/9),
  reproducing the textbook worst case.
- Where/why it failed: My prediction that first-fit decreasing reaches the lower bound on at least 95 percent of uniform 1
  to 60 lists was wrong: 90.2 percent. With sizes clustered between 20 and 50 it reached the bound on
  only 53 percent of 20-item lists; on 12-item lists (75.6 percent at the bound) 28 of 40 cases above
  the bound were truly suboptimal, so roughly 17 percent of those lists cost an extra bin, against the
  kernel's 1 percent.
- Fix: Treat first-fit decreasing as near-optimal only when items are small relative to the bin or widely
  spread; when sizes cluster between a fifth and a half of capacity, run an exact search for small
  lists or a better heuristic, and always compare against the lower bound.
- Why this fix: The heuristic's failures concentrate where items pair and triple awkwardly, which is common in real
  stock (planks, crates, inventory slots), and the lower bound is free to compute.
- Rule of thumb: First-fit decreasing is near-optimal only for spread-out sizes: items clustered at 20-50 percent of
  capacity left about 17 percent of 12-item lists an extra bin above the optimum, and Johnson's mix
  needs 11 bins against 9; check the ceil(sum/C) bound and search exactly when it is not met.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; the 12-item suboptimal share is estimated from 40
  exact checks, not all cases.
- Composed: ideas:PACKING/bin-packing/first-fit-decreasing-beats-first-fit-on-average-but-not-on-every-list
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__first-fit-decreasing-misses-the-optimum-often-when-items-cluster-near-a-third.py
- Prediction: uniform 1-60, 20 items: at the lower bound on at least 95 percent; uniform 20-50: under 80 percent;
  Johnson mix FFD 11 against optimum 9.
- Observed: RESULT: FAIL 2/3; Johnson FFD 11 vs OPT 9; uniform 1-60 at LB 0.902; 20-50 at LB 0.532; 12 items
  20-50 at LB 0.756, above-LB cases optimal 12/40
- Scenarios: 1) 2,000 lists of 20 items uniform 1-60; 2) 2,000 lists uniform 20-50; 3) 500 lists of 12 items
  20-50 with exact checks; 4) built to BREAK the kernel: Johnson's mix (11 against 9)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 3 pass 1 (kernel apply PACKING), 2026-10-15
- Audited: 2026-10-15 · pass · Read the entry and ran its stored sandbox (reproduced every number: Johnson FFD 11 vs 9, uniform 1-60 at LB 0.902, 20-50 at LB 0.532, 12-item 20-50 at LB 0.756 with 12/40 above-LB cases optimal). The model computes everything: FFD is a real first-fit-decreasing, the 9-bin Johnson witness is asserted valid and meets ceil(sum/C) so it is optimal, and the 12-item optimum comes from a correct branch-and-bound (symmetry pruning by equal bin fill is sound). Nothing is built in. The 17 percent figure is derived correctly ((1-0.756) x 28/40) from the first 40 above-bound lists in seed order, which the entry discloses as an estimate. Scope note, not a fail: the 20-item results are lower-bound hits only, so 53 percent at the bound is not 47 percent suboptimal, and the entry words it correctly; the Rule's "only for spread-out sizes" is tested on two distributions plus one adversarial mix, slightly broader than covered. Pure algorithm claim, so modeled does not apply. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
