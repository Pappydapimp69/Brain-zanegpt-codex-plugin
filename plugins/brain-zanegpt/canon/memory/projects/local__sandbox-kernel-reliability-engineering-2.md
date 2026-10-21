# local/sandbox-kernel-reliability-engineering-2 — lessons

Project: local/sandbox-kernel-reliability-engineering-2. Newest first.

---

## E1 — beta factor ln2 crossover holds only at beta zero
- Date: 2026-10-12
- Project: local/sandbox-kernel-reliability-engineering-2
- Tags: [reliability][redundancy][measurement][sandbox]
- What: Sandbox re-run of the beta-factor mission-Q kernel: the pair ratio (10.9x), the shared-term threshold beta/(1-beta)^2, the diminishing return of extra units below it, and the 2-of-3 voting crossover with one unit.
- Why built: The kernel had one memory entry built against it; its 2-of-3 clause (beats one unit only while lam*t < ln 2) was stated without a common-cause term, so it needed a boundary test.
- Design: Closed-form k-of-n reliability with common-cause factor exp(-beta*lam*t) times a binomial over survivors at rate (1-beta)*lam; midpoint-integrated MTTF; sweeps of x=lam*t at beta 0, 0.02, 0.1, 0.3; a 1-of-3 versus 1-of-6 comparison; a rater-blend variance analogue (beta + (1-beta)/k).
- Got right: Pair ratio 10.91x and MTTF 1.4737/lam match the kernel; the threshold x* = beta/(1-beta)^2 is exactly where shared and independent terms are equal (0.1235 at beta 0.1); going from 3 to 6 units gains 0.1% at x=0.01 but 85% at x=0.5; 2-of-3 MTTF is 0.8333.
- Where/why it failed: My prediction that the 2-of-3 crossover with a single unit would move DOWN from ln 2 once beta>0 was wrong: at beta 0.1 it moves UP to 0.770 (ln 2 = 0.693). The kernel's ln 2 holds only at beta = 0, since the single unit's independent share shrinks too.
- Fix: State the 2-of-3 break-even as a function of beta (0.693 at beta 0, 0.770 at beta 0.1) and quote ln 2 only for fully independent units.
- Why this fix: The sandbox gives the exact crossover for the stated beta, so a design review uses the right number instead of a beta-free constant.
- Rule of thumb: Below x = beta/(1-beta)^2 extra identical units buy under 1%; cut beta by diversity instead. Quote the 2-of-3 ln 2 break-even only at beta 0; at beta 0.1 it was 0.770. The rater-blend analogue showed the same cap: variance cut 87.5% at beta 0 but 35% at beta 0.6 with 8 raters.
- Provenance (verified/assumed): Verified first-hand by running the attached sandbox; the model is closed-form and idealised (identical units, one common-cause mode), not field failure data.
- Composed: ideas:RELIABILITY-ENGINEERING/redundancy/beta-factor-mission-q-check/mttf-hides-common-cause, sandbox-kernel-reliability-engineering/E1, sandbox-humor-self-report-bias/E2
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__beta-factor-threshold-and-diminishing-units.py
- Prediction: Written before running: pair ratio 10.9 and MTTF 1.4737; 3-to-6 unit gain under 1% below the threshold; 2-of-3 crossover at ln 2 for beta 0 and lower than ln 2 at beta 0.1.
- Observed: RESULT PASS after correcting the last item: ratio 10.91, MTTF 1.4737, 3-to-6 gain 1.000 at x=0.001 and 1.847 at x=0.5, crossover 0.6932 at beta 0 and 0.7702 at beta 0.1 (prediction of lower was wrong).
- Scenarios: 1) pair at beta 0.1; 2) threshold at three betas; 3) 1-of-3 vs 1-of-6 across x (built to BREAK the no-gain claim above threshold); 4) 2-of-3 at beta 0; 5) 2-of-3 at beta 0.1 (built to break ln 2); 6) rater analogue at beta 0 and 0.6
- Link: scheduled brain train session; session_018RFPy3DMrymTRHnMWEoTT9
- Cited-by: 2026-10-13 · projects/pappydapimp69__brain.md#E164 · compatible · sandboxes/2026-10-13__hamming-double-error-miscorrection.py · observed RESULT: PASS Hamming7 miscorrects 21/21 doubles per codeword (perfect code), SECDED detects 28/28 doubles but triples still miscorrect 896/896; sphere cover 128=128 exactly once; silent-wrong rate at p=.01 2.03e-03 vs 5.33e-05. · brain train auto session 2026-10-13; session_01SVMqRFxH6Uuecz64bYuF9E
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E443 · compatible · sandboxes/2026-10-18__second-check-needs-unlike-modulus.py · observed RESULT: PASS unlike checks joint/product 0.38, dependent pair 4.76; transpositions missed by sum 100% and weighted 0% · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
