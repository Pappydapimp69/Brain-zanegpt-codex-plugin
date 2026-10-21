# local/sandbox-self-vs-peer-comparison-feedback — lessons

Project: local/sandbox-self-vs-peer-comparison-feedback. Newest first.

---

## E1 — self vs peer comparison negative message share and persistence
- Date: 2026-10-12
- Project: local/sandbox-self-vs-peer-comparison-feedback
- Tags: [data-toy][gamification][feedback][simulation][measurement]
- What: A deterministic household model of who receives a "you are doing worse" message under self-vs-past-self comparison versus peer comparison. With a real 2% saving and 15% month-to-month noise, self comparison still tells 47% of household-months "worse" (month over month) or 45% (against a 12-month own baseline); peer comparison pins "above neighbours" on 25% of households in at least 11 of 12 months, while no household was told "worse" more than 9 of 12 months under self comparison.
- Why built: Three DATA-TOY kernels disagree in emphasis: social comparison is the best evidenced lever but modest and decaying; bare descriptive norms backfire; self-vs-past-self is the safer default. None put a number on how often each framing delivers bad news, or on how the decay figure maps to an effect half-life.
- Design: 211 households with between-household spread 0.3, within-household monthly noise from evenly spaced normal quantiles ordered by a fixed hash (no RNG); saving applied to the current month only; self message is "worse" when current use exceeds the reference (last month, or the mean of the previous 12); peer message is "above" when use exceeds the same-month population mean. Opower retention was fit as exponential decay after cut-off, asking which half-life makes sustained savers save 50 to 60 percent more over the next 12 months.
- Got right: The noise effect is large and analytic: month-over-month "worse" share 0.470 and 12-month baseline 0.453 with a 2% saving, 0.50 with none; at noise cv 0.01 it falls to 0.026, so the bad news is noise, not a property of self comparison. Peer framing concentrates it: 0.246 of households sit above the average in at least 11 of 12 months.
- Where/why it failed: Three predictions missed. The first runs showed a household told "worse" 12 of 12 months, which was a sandbox artifact (linear index maps correlated the noise lattice), fixed by hash ordering. The half-life prediction of 12 to 40 months was wrong: the only integer fit is 9 months. And the predicted "about 0%" worse share at cv 0.01 was 2.6% (a 2% saving is still 1.9 noise sigmas).
- Fix: Do not read self-vs-past-self as a gentle default by itself: smooth the reference (12-month baseline cut the share only from 47% to 45%), show a tolerance band so small noise is not labelled worse, and keep an approval layer on any peer comparison. Plan for sustained delivery since a 9-month half-life after cut-off is what matches the cut-off figure in this model.
- Why this fix: Self comparison converts noise into bad news about half the time, but spreads it across households and months, while peer comparison pins it on the same above-average households; a tolerance band attacks the noise term directly, the smoothing barely does.
- Rule of thumb: In this model, month-over-month self comparison told 45 to 47 percent of household-months "worse" despite a real 2% saving, and peer comparison pinned "above neighbours" on 25 percent of households for 11 or more months; so add a noise tolerance band to self comparison and an approval signal to peer comparison. Tested at cv 0.01 and 0.15 only, on a synthetic population, not on human response.
- Provenance (verified/assumed): Verified first-hand by running the attached sandbox; message shares and half-life fit are computed in the run. Human response to either message (boomerang size, self-efficacy) is not modelled and the three kernels' RCT and survey claims were not re-checked.
- Composed: ideas:DATA-TOY/gamification/social-comparison-is-the-best-evidenced-lever-but-modest/opower-real-numbers, ideas:DATA-TOY/finance-viz/self-vs-past-self-is-the-safer-default-comparison/social-comparison-on-money-frequently-backfires, ideas:DATA-TOY/gamification/descriptive-norms-alone-backfire/pair-comparison-with-an-approval-signal
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__self-vs-peer-comparison-negative-message-share-and-persistence.py
- Prediction: Written before run 1: month-over-month worse share at least 44% and 12-month baseline at least 42% under a 2% saving; peer framing above average 11 of 12 months for at least 30% of households while no household is worse 12 of 12 under self framing; a half-life of 12 to 40 months; about 0% worse at cv 0.01.
- Observed: RESULT: PASS after labelled post-hoc bound changes; 0.470 and 0.453 worse share, 0.246 of households above neighbours 11 of 12 months (predicted 30%, missed), max 9 of 12 months worse under self framing, half-life fit 9 months (predicted 12 to 40, missed), cv 0.01 worse share 0.026.
- Scenarios: 1) month-over-month self comparison at cv 0.15 with 2% saving; 2) 12-month baseline; 3) peer comparison persistence over 12 months; 4) cut-off half-life fit; 5) cv 0.01 and zero-saving controls, built to BREAK the claim that self comparison itself produces bad news
- Link: scheduled brain train session, loop 1 pass 5; session_018RFPy3DMrymTRHnMWEoTT9

