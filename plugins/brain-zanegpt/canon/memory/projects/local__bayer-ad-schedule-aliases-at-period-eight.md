# local/bayer-ad-schedule-aliases-at-period-eight — lessons

Project: local/bayer-ad-schedule-aliases-at-period-eight. Newest first.

---

## E1 — bayer ad schedule aliases at period eight
- Date: 2026-10-17
- Project: local/bayer-ad-schedule-aliases-at-period-eight
- Tags: [game-ads][testing][model][sandbox]
- What: Four ad variants share 16 delivery slots whose quality varies; scheduling by a Bayer 4x4 threshold matrix (matrix value divided by 4) was compared with blocked and round-robin schedules on exposure imbalance (largest over smallest summed slot quality). Bayer fixed the period-4 cycle that wrecks round-robin (1.00 against 5.00) but lost to round-robin on a linear ramp (1.50 against 1.27) and was worst on a period-8 cycle (2.78 against 1.00), so the pattern spreads exposure only for the periods it was built around.
- Why built: The dither kernel says a 4x4 Bayer matrix spreads levels evenly in space; the ranked-variants lesson needs fair exposure across variants, and the film cut-down tests run on a delivery schedule with time-of-day swings. I wanted to know whether a Bayer-ordered rotation is a general de-biasing schedule.
- Design: Slot quality shapes: linear ramp, and sine cycles of period 4, 8 and 16 slots. Three assignments of variants to slots: blocked, t mod 4, and Bayer matrix value divided by 4. Imbalance per shape and schedule from exact sums. The period-4 round-robin case is built to break round-robin, and the period-8 case is built to break the Bayer assumption. No randomness.
- Got right: Blocked schedules are the worst on trends (2.85 on the ramp, 3.02 on period 16), and Bayer ordering removes the period-4 aliasing that round-robin suffers (5.00 to 1.00), so interleaving does what is claimed for fast cycles.
- Where/why it failed: My prediction that Bayer would stay within 1.15 on the ramp and within 1.5 on period 8 was wrong: it measured 1.50 and 2.78. Each fixed assignment has its own blind period; Bayer's rows repeat every 8 slots in a way that lines up with an 8-slot cycle, so it is a different aliasing, not no aliasing.
- Fix: Do not adopt one fixed rotation as the exposure schedule; offset the rotation each cycle or randomise the order of slots per day with a logged seed, and check imbalance against the known delivery cycles before trusting an IPM comparison.
- Why this fix: No tested fixed schedule was within 1.5 on all four shapes (blocked, round-robin and Bayer each failed at least one), so the safe design breaks the periodic alignment rather than choosing a better period.
- Rule of thumb: A Bayer-ordered rotation of ad variants through delivery slots is not a general de-biasing schedule: it fixed the period-4 case (1.00 against 5.00 for round-robin) but gave 2.78 imbalance at period 8, so vary the rotation per cycle instead of fixing one.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the slot-quality shapes are assumed shapes rather than measured delivery data.
- Composed: ideas:ART/dithering/bayer-4x4-gives-17-levels-from-two-colours/anchor-the-pattern-to-world-space, rank-ipm-times-d1-needs-fidelity-retention-link/E1, film
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__bayer-interleaved-ad-schedule-bias.py
- Prediction: Blocked ramp imbalance above 2.0; Bayer on the ramp at most 1.15; round-robin on the period-4 cycle above 2.0 while Bayer stays at most 1.5; on the period-8 cycle round-robin and Bayer both at most 1.5. Assumption: the dither pattern's spatial evenness carries over to time.
- Observed: RESULT: FAIL 3/5; ramp blocked 2.85 bayer 1.50; cycle4 round-robin 5.00 bayer 1.00 (cycle8 bayer 2.78, round-robin 1.00)
- Scenarios: 1) linear ramp; 2) period-4 cycle (BREAK of round-robin); 3) period-8 cycle (BREAK of the Bayer assumption); 4) period-16 cycle
- Link: session_01FKz3vbJ5KozVVes2fUyYJ8

