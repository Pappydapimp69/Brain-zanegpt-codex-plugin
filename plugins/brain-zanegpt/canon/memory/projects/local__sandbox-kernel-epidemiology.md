# local/sandbox-kernel-epidemiology — lessons

Project: local/sandbox-kernel-epidemiology. Newest first.

---

## E2 — sir final size overshoot shrinks under heterogeneous susceptibility
- Date: 2026-10-12
- Project: local/sandbox-kernel-epidemiology
- Tags: [epidemiology][sir][sandbox]
- What: Re-verified the SIR final-size kernel (z=0.797 at R0=2, peak at cumulative infection 1-1/R0) with an RK4 cross-check, then broke it with heterogeneous susceptibility.
- Why built: The kernel had no memory entry building against it and its homogeneous-mixing assumption was never stressed.
- Design: Bisection root of z-1+exp(-R0 z) against an RK4 SIR run from I0=1e-6; then a two-group model (susceptibility 1.8 and 0.2 at equal weight, force scaled so R0 stays 2) and a mild split (1.1 and 0.9).
- Got right: Homogeneous results matched: R0=2 gave z=0.797 and RK4 0.797 with cumulative infection 0.500 at the I peak, R0=1.1 gave 0.176 and peak 0.091 against HIT 0.091.
- Where/why it failed: With strong susceptibility spread at the same R0 the final size was 0.208 (not 0.797) and cumulative infection at the peak 0.111 (not 0.500); the mild split gave 0.787 and 0.491.
- Fix: Quote the homogeneous-mixing final size and herd threshold only with a stated homogeneity assumption, and give a sensitivity range when susceptibility is known to vary.
- Why this fix: High-susceptibility people are infected first, so the effective susceptible pool depletes faster than the homogeneous 1-1/R0 count assumes; the mild split moved the answer by 0.01 and the strong one by 0.59, so the caveat only matters when spread is large.
- Rule of thumb: The z-1+exp(-R0 z) final size and 1-1/R0 peak match RK4 to 1e-3 only for homogeneous mixing; with susceptibility spread of 1.8 versus 0.2 at the same R0 the final size fell from 0.797 to 0.208, so state the assumption before quoting burden.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script in this session; all numbers are from that run.
- Composed: ideas:EPIDEMIOLOGY/sir/final-size-root-beside-herd-threshold, sandbox-kernel-epidemiology/E1, brainwork/E62
- Sandbox: sandboxes/2026-10-12__sir-final-size-overshoot-shrinks-under-heterogeneous-susceptibility.py
- Prediction: Homogeneous z matches RK4 within 1e-3 with peak cumulative infection at HIT; strong heterogeneity at the same R0 gives final size under 0.70 and peak cumulative below 0.45.
- Observed: RESULT: PASS homogeneous final size 0.797 matches RK4 to 1e-3 but strong heterogeneity at the same R0 gives 0.208 (peak cum 0.111 vs HIT 0.5); mild gives 0.787
- Scenarios: 1) homogeneous R0=2; 2) homogeneous R0=1.1; 3) BREAK: strong two-group susceptibility 1.8/0.2; 4) mild 1.1/0.9
- Link: brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh

## E1 — sir epidemic ends past herd threshold overshoot peaks near r0 2
- Date: 2026-10-12
- Project: local/sandbox-kernel-epidemiology
- Tags: [epidemiology][sir]
- What: Tested the common reading that an SIR epidemic burns out once the herd-immunity
  threshold HIT = 1 - 1/R0 is immune. HIT is where prevalence PEAKS (S = 1/R0); the
  epidemic keeps infecting past it, and the final attack rate z solves z = 1 - exp(-R0 z).
- Why built: Seeding the EPIDEMIOLOGY domain from a cited source (Wikipedia, Herd immunity:
  p_c = 1 - 1/R0 and "the cumulative proportion of individuals who get infected ... can
  exceed the HIT", the excess being the overshoot; Wikipedia, Compartmental models in
  epidemiology: final size s_inf = s0 exp(-R0 (r_inf - r0))).
- Design: Isolated. Stdlib python: bisection solves the final-size root to 1e-15; an RK4
  integration of normalized SIR (gamma=1, i0=1e-6, dt=0.01) checks the root and records
  cumulative infection at the prevalence peak; a sweep of R0 over 1.01..10 finds the
  largest overshoot.
- Got right: The final-size root and the ODE agree to 1e-4 at every R0 tried, and the
  cumulative infected fraction at the I-peak equals 1 - 1/R0 to 1e-3. That identity is
  why the threshold is a peak marker, not an end marker.
- Where/why it failed: Treating HIT as the final burden understates it badly. At R0=2 the
  HIT is 0.50 but 0.797 get infected. Near threshold (R0=1.1) the epidemic infects 1.94x
  the HIT. Even at R0=10 it overshoots by 0.10 absolute (z=0.99995 vs 0.90).
- Fix: Compute the final size from z = 1 - exp(-R0 z) (bisection or Lambert W). Report
  overshoot z - (1 - 1/R0) beside the HIT, never the HIT alone as the cost of
  letting an outbreak run.
- Why this fix: The final-size relation is exact for homogeneous-mixing SIR and needs one
  scalar root; the ODE confirms it, so no simulation is needed to get the burden.
- Rule of thumb: An unmitigated SIR epidemic does not stop at the herd threshold 1-1/R0; that
  is where prevalence peaks. Final size solves z = 1-exp(-R0 z): R0=2 gives 0.797 vs 0.5,
  and the overshoot peaks at about 0.30 near R0=2.15.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry, and the
  formulas were checked against the two cited Wikipedia pages on 2026-10-12. Assumptions:
  homogeneous mixing, a closed population, SIR with permanent immunity and a tiny seed.
- Composed: N/A
- Sandbox: sandboxes/2026-10-12__sir-epidemic-ends-past-herd-threshold-overshoot-peaks-near-r0-2.py
- Prediction: Written before the first run. R0=2 gives HIT 0.500 and z~0.797 (overshoot ~0.297).
  R0=1.5 gives z~0.583 and R0=3 gives z~0.940. Max overshoot ~0.30 at R0 in [2.0, 2.5].
  RK4 cumulative at the I-peak equals HIT within 1e-3, and the ODE final equals the root
  within 1e-3. At R0=1.1, z/HIT is about 1.9.
- Observed: RESULT: PASS SIR ends past HIT: R0=2 z=0.797 vs HIT 0.5; overshoot max 0.298 at
  R0=2.15; cum@peak==HIT; R0=1.1 z/HIT~1.9 (R0=1.5 z=0.5828; R0=3 z=0.9405; R0=10
  z=0.999955, overshoot 0.1000; R0=1.1 z=0.1761 vs HIT 0.0909, ratio 1.937).
- Scenarios: 1) R0=1.5, 2, 3: root vs RK4, cumulative at peak vs HIT; 2) R0 sweep 1.01..10
  for maximum overshoot; 3) BREAK: extremes R0=1.1 (ratio z/HIT near 2) and R0=10
  (ratio near 1) to see if "ends at HIT" is ever close. It holds only in ratio at high R0.
- Link: session; brain train newdomain 5 loops; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-epidemiology.md#E2 · compatible · sandboxes/2026-10-12__sir-final-size-overshoot-shrinks-under-heterogeneous-susceptibility.py · observed RESULT: PASS homogeneous final size 0.797 matches RK4 to 1e-3 but strong heterogeneity at the same R0 gives 0.208 (peak cum 0.111 vs HIT 0.5); mild gives 0.787 · brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh
