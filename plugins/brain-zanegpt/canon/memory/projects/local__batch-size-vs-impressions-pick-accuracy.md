# local/batch-size-vs-impressions-pick-accuracy — lessons

Project: local/batch-size-vs-impressions-pick-accuracy. Newest first.

---

## E1 — bigger ad batch needs more impressions to pick the same winner
- Date: 2026-10-16
- Project: local/batch-size-vs-impressions-pick-accuracy
- Tags: [game-ads][comedy][statistics][sandbox]
- What: Ranking fake-ad variants on retained installs per impression, the best variant was picked 54% of the time with 6 variants at 300 impressions each, but 40% with 12 and 35% with 16, and a 16-variant batch only reached the 6-variant accuracy at 3000 impressions each (67% against 54%).
- Why built: Loop-2 train pick, chosen by hand because the picker returned a loop-1 target: it joins the vary-the-comic-engine kernel (more engines allow bigger batches), the fake-ad kernel source check and the batch-ceiling trope cap (ceilings of 6, 12 and 16), to see what the bigger batch costs when its variants are then ranked on IPM times D1.
- Design: Seeded simulation, 400 trials per cell. Each variant has a true install rate from 4% to 12% and a true D1 retention from 25% to 45%; observed score is retained installs per impression from Bernoulli draws; batch sizes 6, 12, 16 and impressions per variant 300, 1000, 3000. Reports the share of trials where the true best is picked and the mean regret.
- Got right: Pick accuracy rose with impressions at every batch size (6 variants: 54%, 65%, 78%), and regret stayed small, under 0.6 percentage points of retained installs per impression, so a wrong pick usually lost little.
- Where/why it failed: I expected the 16-variant batch to need about 3 times the impressions to match the 6-variant batch; the sweep showed 1000 was not enough (47% against 54%) and it matched only at 3000, a factor of 10, and a batch at the ceiling does not pay for itself when impressions are fixed.
- Fix: When a batch is sized up to the trope-cap ceiling, raise the impressions per variant in proportion (about 10 times at 16 variants versus 6) or rank in two rounds, dropping the bottom half after the first.
- Why this fix: The best variant competes against more noisy rivals as the batch grows, so the chance that one of them beats it by luck rises while the gap between the top two shrinks.
- Rule of thumb: A 16-variant ad batch picked the true best 35% of the time at 300 impressions each against 54% for 6 variants, and needed 3000 impressions each to match, so do not grow the batch to the ceiling without growing the test budget.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the 6, 12 and 16 batch sizes come from the named lessons, and the rate ranges are my own assumptions, not measured ad data.
- Composed: ideas:COMEDY-CRAFT/vary-the-comic-engine-not-the-topic, fake-ad-kernel-source-check/E1, batch-ceiling-trope-cap/E1
- Picked-by: new-half
- Distinct from: rank-ipm-times-d1-needs-fidelity-retention-link/E1 (that lesson shows the pick flips with sample size in a 3-variant toy; this one varies the batch size from 6 to 16 and measures the budget needed to hold accuracy).
- Sandbox: sandboxes/2026-10-16__bigger-ad-batch-needs-more-impressions-to-pick-the-same-winner.py
- Prediction: Hidden assumption: a larger batch costs a proportional, modest budget increase. Expected the 16-variant batch to match 6-variant accuracy at about 1000 impressions; it would be wrong if 1000 was not enough.
- Observed: RESULT: PASS at 300 impressions best picked k6 0.54 k12 0.40 k16 0.35; k16 at 3000 0.67; k16 matches k6@300 first at n=3000; regret k16@300 0.0051 vs k6@300 0.0036 (the 1000-impression expectation was refuted)
- Scenarios: 1) 6 variants at three budgets; 2) 12 variants; 3) 16 variants at ceiling, built to break the same-budget assumption.
- Link: scheduled brain train auto loop 2 pass 1 (kernel, hand-picked); session_01GYKQrKfm5FQsrnyu59GmiS

