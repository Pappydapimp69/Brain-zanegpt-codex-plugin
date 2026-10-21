# local/disagreement-targeting-does-not-help-flat-score-landscape — lessons

Project: local/disagreement-targeting-does-not-help-flat-score-landscape. Newest first.

---

## E1 — disagreement gap directs extra impressions
- Date: 2026-10-17
- Project: local/disagreement-targeting-does-not-help-flat-score-landscape
- Tags: [game-ads][testing][model][sandbox]
- What: A deterministic 300-trial simulation of 8 ad variants with a 40000-impression budget, comparing uniform extra spend against spending the extra half on the union of the top 3 by IPM and the top 3 by IPM times D1 (the disagreement set). With conflicting metrics targeting scored 0.230 correct winners against 0.247 uniform (gain -0.017); with aligned metrics it scored 0.693 against 0.647 (+0.047). The idea that a ranking disagreement tells you where to spend impressions was refuted.
- Why built: The tension-as-information-gap kernel says an open disagreement marks where information is missing, and the IPM times D1 lesson says the two rankings differ only when retention opposes conversion. I wanted to see whether the disagreement set is a better place to spend extra impressions than a uniform spend.
- Design: True install rate 0.030 + 0.004 i; D1 either 0.40 - 0.03 i (conflict) or flat 0.30 (aligned); normal-approximation binomial draws from a fixed-seed linear congruential generator; first stage 1/8 budget split evenly, second stage half the budget either even or on the union of the two top-3 sets; pick by retained installs per impression. Scenarios: conflict uniform, conflict targeted, aligned uniform, aligned targeted (aligned is the control, conflict is the claim).
- Got right: The simulation was deterministic and the aligned control moved the expected way: with one clear winner the targeted spend gains 4.7 points because the union is small and the winner is in it.
- Where/why it failed: The gain I predicted for the conflict case (at least 5 points) did not appear and was slightly negative. In the conflict setup the score curve is nearly flat: variants 2, 3 and 4 differ by about 1 percent (0.01292, 0.01302, 0.01288), so no impression budget this size separates them, and the targeted spend only shifts impressions from the other five variants which adds nothing to a three-way tie.
- Fix: Do not use the IPM versus IPM times D1 disagreement as a spending rule; first check how far apart the top scores are relative to their standard error and only then decide whether more impressions can resolve the tie or whether a variant should be recut instead.
- Why this fix: The failing case had a near-tie in the true score, where extra data cannot help, whereas the aligned case with one clear winner is where targeting helped, so the score gap is the quantity that decides, not the existence of a disagreement.
- Rule of thumb: A disagreement between IPM and IPM times D1 rankings is not a signal to spend more impressions on the union of their top variants: targeting lost 1.7 points when the true scores were within about 1 percent and gained 4.7 points only when the winner was clear, so measure the top-score gap first.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the rates, the D1 slope and the normal approximation are assumed toy values and no real ad data was used.
- Composed: ideas:SYSTEM/tension-as-information-gap, rank-ipm-times-d1-needs-fidelity-retention-link/E1, film
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__disagreement-gap-directs-extra-impressions.py
- Prediction: Targeting the union of the two top-3 sets gains at least 5 points correct-winner rate under conflicting metrics and at most 2 points under aligned metrics. Assumption: the true winner is inside the union and its score is separable from the runner-up at this budget; a near-tie would prove it wrong.
- Observed: RESULT: FAIL targeting gain conflict -0.017 aligned +0.047 (uniform 0.247/0.647)
- Scenarios: 1) conflict metrics, uniform spend; 2) conflict metrics, targeted spend (the claim); 3) aligned metrics, uniform spend; 4) aligned metrics, targeted spend (control; BREAK of the claim that targeting only helps under conflict)
- Link: session_01FKz3vbJ5KozVVes2fUyYJ8

