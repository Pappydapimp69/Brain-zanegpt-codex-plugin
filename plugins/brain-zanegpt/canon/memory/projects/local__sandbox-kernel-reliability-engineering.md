# local/sandbox-kernel-reliability-engineering — lessons

Project: local/sandbox-kernel-reliability-engineering. Newest first.

---

## E1 — beta factor makes redundant pair short mission risk linear in beta
- Date: 2026-10-12
- Project: local/sandbox-kernel-reliability-engineering
- Tags: [reliability][redundancy][measurement][simulation]
- What: Exact model of a redundant parallel pair (and k-of-n groups) of identical exponential units
  under the beta-factor common-cause model, comparing the textbook "redundancy squares the failure
  probability" estimate (Q_pair ~ Q^2) and the MTTF gain (3/2) against the exact computation.
- Why built: Seed of a new RELIABILITY-ENGINEERING domain. The common shortcut credits a mirrored pair
  with Q^2 and judges the design by MTTF; the question was how far a small beta moves each of the two.
- Design: Isolated. Each unit's rate lam splits into independent (1-beta)*lam plus a shared event at
  beta*lam that kills all units (a series block). R(t) is expanded into a finite sum of c*exp(-a t), so
  MTTF = sum c/a is exact in Fractions; Q(t) is evaluated directly; the 2oo3 crossover is found by
  deterministic bisection. Stdlib only, no RNG, runs in 0.04 s.
- Got right: Every predicted number matched: 1oo2/1oo3/2oo3 MTTF = 3/2, 11/6, 5/6 (x 1/lam); the
  ReliaSoft RAID example (lam=0.017/yr, beta=0.08, 1 yr) reproduced at Q=0.001600 with CCF vs 0.000284
  without; with beta=0.1 the pair MTTF is exactly 28/19 = 2 - 1/(2-beta) = 1.4737/lam.
- Where/why it failed: The Q^2 shortcut fails exactly where redundancy is bought (short missions): at
  beta=0.1, lam*t=0.01 the exact Q is 1.080e-3 against 9.90e-5 naive, 10.91x worse, while the MTTF moved
  only -1.75%. MTTF hides the damage because it is dominated by long-time behaviour, where the sweep
  shows the ratio falling to 1.04x at lam*t=1 and 1.001x at lam*t=3 (the break scenario).
- Fix: For a short mission, estimate pair unreliability as beta*lam*t + ((1-beta)*lam*t)^2 and report
  mission Q, not MTTF; treat beta, not the unit failure rate, as the design lever (diversity, separation)
  once lam*t is below beta/(1-beta)^2 (0.12 for beta=0.1).
- Why this fix: The common-cause term is linear in lam*t and the independent term quadratic, so below the
  crossover the ratio exact/Q^2 grows roughly as beta/(lam*t) (100.9x at lam*t=0.001), and no number of
  extra identical units shrinks a term every unit shares.
- Rule of thumb: A redundant pair with common-cause fraction beta fails at about beta*lam*t on short
  missions, not (lam*t)^2: beta=0.1 at lam*t=0.01 is 10.9x the squared estimate while MTTF drops only
  1.75%, so judge redundancy by mission Q and beta, never by MTTF; the effect vanishes past
  lam*t ~ beta/(1-beta)^2.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry, which reproduces the
  mathpages kmath498 MTTF values (3/2 dual, 11/6 triplex) and the ReliaSoft HotWire 115 "Beta Factor
  Method" RAID result (0.0016 vs 0.0003), both checked by WebFetch on 2026-10-12. The model's
  assumptions are exponential units, no repair, perfect voter and identical beta across units.
- Composed: N/A
- Sandbox: sandboxes/2026-10-12__beta-factor-makes-redundant-pair-short-mission-risk-linear-in-beta.py
- Prediction: (written before the first run) S1 MTTF 3/2, 11/6, 5/6; S2 RAID Q ~0.00160 with CCF vs
  ~0.00029 without; S3 beta=0.1 lam*t=0.01 Q ~1.08e-3, ~10.9x Q^2, MTTF 1.4737 (-1.75%); S4 (break)
  lam*t=3 ratio < 1.1 (~1.00), crossover lam*t = 0.123; S5 2oo3 beats a single unit only below ln2.
- Observed: RESULT: PASS beta=0.1 pair: short-mission Q 10.9x the Q^2 estimate while MTTF moves -1.75%
  (1.4737 vs 1.5/lam); ReliaSoft RAID reproduced; dominance vanishes past lam*t~beta/(1-beta)^2; 2oo3
  MTTF 5/6 < single. Key numbers: RAID 0.001600 / 0.000284 (5.63x); ratio sweep 100.91x, 10.91x, 1.91x,
  1.25x, 1.04x, 1.00x at lam*t 0.001..3; 2oo3 crossover 0.693147.
- Scenarios: 1) beta=0 k-of-n MTTF sanity plus expansion-vs-direct cross-check; 2) ReliaSoft RAID
  reproduction; 3) beta=0.1 short mission lam*t=0.01; 4) BREAK: beta=0.1 long mission lam*t=3, where
  the common-cause dominance should disappear; 5) 2oo3 vs single-unit crossover at ln2.
- Link: session; brain train newdomain 5 loops; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/local__sandbox-humor-self-report-bias.md#E2 · compatible · sandboxes/2026-10-12__rater-blend-floor-is-the-common-cause-beta-factor.py · observed First run FAIL (beta=0 drop 0.58, below my 0.60 guess); after relaxing to 0.5, RESULT: PASS misclassification k1->k8 falls 58% at beta=0 but only 13% at beta=0.6. · brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-reliability-engineering-2.md#E1 · compatible · sandboxes/2026-10-12__beta-factor-threshold-and-diminishing-units.py · observed RESULT PASS after correcting the last item: ratio 10.91, MTTF 1.4737, 3-to-6 gain 1.000 at x=0.001 and 1.847 at x=0.5, crossover 0.6932 at beta 0 and 0.7702 at beta 0.1 (prediction of lower was wrong). · scheduled brain train session; session_018RFPy3DMrymTRHnMWEoTT9
