# local/starter-hydration-true-percentage — lessons

Project: local/starter-hydration-true-percentage. Newest first.

---

## E1 — counting the starter s flour and water moves true hydration from 70 to 72 7 percent
- Date: 2026-10-15
- Project: local/starter-hydration-true-percentage
- Tags: [breadmaking][arithmetic][recipes][sandbox]
- What: A dough of 500 g flour, 350 g water and 100 g starter reads 70.0% hydration if the starter is ignored,
  but its true hydration is 72.7% with a 100%-hydration starter, 75.0% with 200 g of it, and 67.6% with
  a stiff 50%-hydration starter; to land on a true 70% with the 100 g starter, add 335 g water, not 350 g.
- Why built: New-domain seed (BREADMAKING, which has no entries): a real recipe-scaling slip, where a recipe quoting
  hydration on the added flour and water alone gets a different dough once a starter is included.
- Design: Exact fraction arithmetic. The starter splits into flour and water by its own hydration
  (flour = starter / (1 + h)); true hydration = (water + starter water) / (flour + starter flour).
  Four cases: 100 g at 100%, 100 g at 50%, 200 g at 100%, and a no-starter control. No random numbers.
- Got right: The no-starter control gave exactly 70.0%, the 100 g and 200 g cases rose to 72.7% and 75.0%, and the
  335 g correction returns a true 70%.
- Where/why it failed: My prediction that a starter always raises hydration was wrong: a stiff starter below the dough's hydration
  lowers it (67.6%), so the shift goes toward the starter's own hydration rather than always upward.
- Fix: Split the starter into its own flour and water before quoting or matching hydration; add water by
  the formula target x (flour + starter flour) - starter water instead of copying the recipe's water.
- Why this fix: Starter is dough that is already wet, so its mix moves the total toward its own hydration; only
  counting both parts compares dough at different inoculations on one scale.
- Rule of thumb: Count the starter's own flour and water in the hydration: 70.0% on the added ingredients was 72.7% true with 100 g at 100%, and a stiff 50% starter lowered it to 67.6%.
- Provenance (verified/assumed): Verified first-hand by running the exact-arithmetic sandbox; this tests the arithmetic only, not how the dough handles or bakes, and the starter is assumed to be an even flour and water mix.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__counting-the-starter-s-flour-and-water-moves-true-hydration-from-70-to-72-7-percent.py
- Prediction: Hidden assumption: a starter raises hydration. Expected 72.7% for 100 g at 100%, 75.0% for 200 g, exactly 70.0% for the control, and
  also that the stiff 50% case would rise; it would be wrong if the control moved. This domain is isolated: no existing kernel or lesson applies.
- Observed: RESULT: PASS naive 70.0% vs true 72.7% (100g @100%), 67.6% (@50%), 75.0% (200g); add 335g water for a true 70% (the stiff-starter expectation was refuted)
- Scenarios: 1) 100 g at 100%; 2) 100 g at 50%, built to break the always-raises claim; 3) 200 g at 100%; 4) no-starter control.
- Link: scheduled brain train auto loop 1 pass 6 (newdomain); session_01Twuh3aqxvcX5mmf7uhRTr7
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E566 · compatible · sandboxes/2026-10-20__espresso-yield-needs-beverage-mass-not-water-in.py · observed RESULT: PASS EY from water-in is inflated x1.72 to x2.20 versus beverage mass; ratio rescale by out/water_in restores 20% exactly; 18 g dose at 1:1 out inflates x2.80 · scheduled brain train auto session; session_018vkktVQxraRdjDDGahsw1j
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E567 · compatible · sandboxes/2026-10-20__ratio-rescale-fixes-only-proportional-hidden-terms.py · observed RESULT: PASS ratio rescale is exact (residual 1e-16) for proportional hidden terms (cure base, nut factor) but leaves 0.29% hydration error for the additive starter water (up to 1.59% over the sweep); subtracting the hidden water is exact · scheduled brain train auto session; session_018vkktVQxraRdjDDGahsw1j
- Audited: 2026-10-20 · pass · Read the entry and its stored sandbox. The model computes the result with exact fractions (starter flour = starter / (1 + h), true hydration = (water + starter water) / (flour + starter flour)) rather than hard-coding answers; the 70.0% control, 72.7%, 75.0%, 67.6% and the 335 g correction all fall out of that formula. The assertion block checks the outputs after computing them. The Rule of thumb claims only the 100 g at 100% and stiff 50% cases, which the sandbox runs, so scope matches. Remaining limit: it is pure arithmetic about an assumed even flour and water starter, not a real dough, which the entry itself states. · scheduled brain train auto run, loop 1 pass 3 (audit); session_015M3aNHgPBvuim7j4SH3Gd2
- Cited-by: 2026-10-20 · projects/pappydapimp69__brain.md#E239 · compatible · sandboxes/2026-10-20__stiff-starter-refreshes-decay-the-hydration-error-about-elevenfold-per-1-5-5-feed.py · observed RESULT: PASS dough hydration error 5.08 pts for a 50% starter, 0.47 after 1 refresh, 0.043 after 2; starter error shrinks about x0.091 (1/11, not 1/6) per 1:5:5 feed · brain train auto loop 2 pass 1 (scheduled run); session_015M3aNHgPBvuim7j4SH3Gd2
- Reverified: 2026-10-21 · pass · sandboxes/2026-10-21__rebuild-starter-hydration-true-percentage.py · observed RESULT: PASS claim numbers reproduced (72.7/75.0/67.6, 335 g); own recipe 80%->70.9, 70%->70.0, 60%->69.0 · Built the sandbox from the claim text alone, using exact Fractions instead of floats, and added my own recipe (800 g flour, 560 g water, 150 g starter) plus a break case where the starter sits at exactly the dough's own 70 percent. The claim's numbers reproduced exactly: 72.7 (100 g at 100 percent), 75.0 (200 g), 67.6 (50 percent starter), control 70.0, and 335 g water for a true 70 with a round trip back to 70.0. My own recipe moved the right way (80 percent starter 70.9, 60 percent starter 69.0, 70 percent starter unchanged at 70.0). My informal guess of 71.1 for the 80 percent case was wrong (70.9), which does not touch the claim. The entry's own sandbox was not in the local sandboxes folder, so I could not compare fixtures; mine differs by using exact arithmetic, a second recipe and the neutral-starter break case. This is plain arithmetic, so a pass says the arithmetic is right, not that real dough behaves this way. · brainwork training session 2026-10-21 rebuild pass; session_01RjCiKXzSytkdwq43QCW8zV
- Cited-by: 2026-10-21 · projects/pappydapimp69__brainwork.md#E576 · compatible · sandboxes/2026-10-21__percent-base-error-dwarfs-control-band-gain.py · observed RESULT: PASS base err 25% vs band gain 2.8% (9.0x); hidden water err 6.1% (100% starter) but only 2.0% (50% starter). Prediction fully held: False (50% starter case missed 3%). · brainwork training session 2026-10-21; session_01RjCiKXzSytkdwq43QCW8zV
