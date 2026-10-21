# local/sandbox-kernel-inventory — lessons

Project: local/sandbox-kernel-inventory. Newest first.

---

## E2 — newsvendor fractile breaks with salvage and fixed cost
- Date: 2026-10-12
- Project: local/sandbox-kernel-inventory
- Tags: [inventory][newsvendor][sandbox]
- What: Re-verified the newsvendor critical-fractile kernel on Poisson demand and mapped where the plain CR=(p-c)/p formula stops being right.
- Why built: The kernel was untested by any later memory entry; I wanted its boundary, not just a repeat of inventory/E1.
- Design: Deterministic Poisson pmf, brute-force expected profit over every integer q, compared with the CDF-quantile order; then added salvage value and a fixed order cost.
- Got right: Without salvage or fixed cost the fractile order equalled brute force in 3/3 cases (mean 2, 50, 20); stocking the mean at CR 0.95 lost 21.4% at mean 2 and 4.4% at mean 50.
- Where/why it failed: With salvage s=4 (p=10,c=6,mean 20) the kernel CR=(p-c)/p ordered 19 against optimum 22, a 2.8% loss; with fixed order cost K=15 at mean 2 the fractile order of 2 earned -10.41 while ordering nothing earned 0.
- Fix: Use CR=(p-c)/(p-s) when leftovers have salvage value s, and compare the fractile profit with zero whenever a fixed per-order cost exists.
- Why this fix: Underage cost is p-c and overage cost is c-s, so the critical ratio is underage/(underage+overage); the salvage-adjusted order hit the brute-force optimum 22 exactly.
- Rule of thumb: Order the demand quantile at (p-c)/(p-s), treat s=0 as the special case, and check the fractile order against not ordering when a fixed order cost exists.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script in this session; all numbers are from that run.
- Composed: ideas:INVENTORY/newsvendor/order-at-the-critical-fractile-not-the-mean, sandbox-kernel-inventory/E1
- Sandbox: sandboxes/2026-10-12__newsvendor-fractile-breaks-with-salvage-and-fixed-cost.py
- Prediction: Fractile equals brute force with no salvage or fixed cost; salvage 4 shifts the optimum above 19; fixed cost 15 flips the optimum to zero.
- Observed: RESULT: PASS fractile exact w/o salvage/fixed cost (S1); salvage shifts CR to (p-c)/(p-s) (S2); S2 brute 22 vs kernel 19; S3 optimum 0.
- Scenarios: 1) no salvage, means 2/50/20; 2) salvage 4 at mean 20; 3) BREAK: fixed order cost 15 at mean 2; 4) mean stocking at CR 0.95, means 2 and 50
- Link: brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh

## E1 — newsvendor critical fractile vs order the mean
- Date: 2026-10-12
- Project: local/sandbox-kernel-inventory
- Tags: [inventory][newsvendor][sandbox]
- What: Seeded the INVENTORY domain with a newsvendor test: on exact Poisson demand, compared the
  critical-fractile order quantity (generalized inverse of the CDF at CR=(p-c)/p) against a
  brute-force argmax of expected profit, the rounded normal approximation mu+z*sqrt(mu), and the
  common shortcut of stocking the mean demand.
- Why built: The inventory domain had no records. The critical fractile is the textbook answer, but
  practitioners often stock the mean or use a normal approximation on small counts, and nobody had
  measured how much each shortcut costs in expected profit.
- Design: Isolated. Stdlib-only deterministic script, Poisson pmf summed far into the tail, expected
  profit p*E[min(q,D)]-c*q evaluated for every q; four scenarios varying mean demand (2, 3, 50) and
  critical ratio (0.3, 0.5, 0.9, 0.95).
- Got right: The generalized-inverse quantile (smallest q with F(q) >= CR) equalled the brute-force
  argmax in 4/4 scenarios, and the rounded normal approximation stayed within 0.154% of optimal
  profit even at mean demand 2, missing the optimum by one unit only there.
- Where/why it failed: Stocking the mean is the costly shortcut: 3.12% loss at mu=50 CR=0.3,
  3.52% at mu=50 CR=0.9, and 21.35% at mu=2 CR=0.95, where it ordered 2 instead of 5. My prediction
  of about 1% loss at mu=50 CR=0.3 was too low because a low-margin item has a small profit base.
- Fix: Compute q from the critical ratio every time, using the discrete CDF when available and
  mu+z*sigma otherwise; never default the order to mean demand unless CR is close to 0.5.
- Why this fix: The fractile is exact and costs one CDF walk; the normal approximation is the cheap
  fallback and its one-unit rounding error is nearly free because profit is flat at the optimum,
  whereas the mean ignores the cost asymmetry that drives the whole answer.
- Rule of thumb: Order at the critical fractile (smallest q with F(q) >= (p-c)/p); even a rounded
  normal approximation lost at most 0.15% at mean demand 2, but stocking the mean lost 3% at
  mean 50 and 21% at mean 2 with CR 0.95.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry, which computes
  exact expected profit on Poisson demand for four scenarios. The profit function and the
  critical-fractile formula were checked against the Wikipedia Newsvendor model article. Poisson
  demand and a zero salvage value are modelling assumptions of the sandbox.
- Composed: N/A
- Sandbox: sandboxes/2026-10-12__newsvendor-critical-fractile-vs-order-the-mean.py
- Prediction: S1 mu=50 CR=0.3 opt 46, normal loss <0.1%, mean loss ~1%; S2 mu=50 CR=0.9 opt 59,
  mean loss ~4%; S3 mu=2 CR=0.95 opt 5, normal q 4 with ~0.15% loss, mean loss ~22%; S4 mu=3
  CR=0.5 all ~0; fractile==brute 4/4, normal within 1% 4/4.
- Observed: RESULT: PASS fractile==brute 4/4; normal-approx within 1% 4/4; order-the-mean >5% loss
  in ['S3-break']. Optima 46, 59, 5, 3; normal loss 0, 0, 0.154%, 0; mean loss 3.12%, 3.52%,
  21.35%, 0. Only miss: S1 mean loss 3.12% vs predicted ~1%.
- Scenarios: 1) mu=50 CR=0.30 low margin; 2) mu=50 CR=0.90 high margin; 3) mu=2 CR=0.95 small
  count, extreme ratio (built to BREAK both the normal approximation and order-the-mean);
  4) mu=3 CR=0.50 symmetric control
- Link: session; brain train newdomain 5 loops; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-inventory.md#E2 · compatible · sandboxes/2026-10-12__newsvendor-fractile-breaks-with-salvage-and-fixed-cost.py · observed RESULT: PASS fractile exact w/o salvage/fixed cost (S1); salvage shifts CR to (p-c)/(p-s) (S2); S2 brute 22 vs kernel 19; S3 optimum 0. · brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh
