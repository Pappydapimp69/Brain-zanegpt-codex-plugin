# local/sandbox-gap-lag-wall-from-exponential-hold-cost — lessons

Project: local/sandbox-gap-lag-wall-from-exponential-hold-cost. Newest first.

---

## E1 — sandbox gap lag wall from exponential hold cost
- Date: 2026-10-15
- Project: local/sandbox-gap-lag-wall-from-exponential-hold-cost
- Tags: [sandbox][narrative][structure][game-design]
- What: A beat-by-beat model of withholding information (each beat opens a question that resolves LAG beats later) where holding k open questions costs growth^k attention against a fixed budget; it finds the longest withholding lag a viewer can carry.
- Why built: The information-gap kernel says engineer the order and rationing of information, the film short's therefore-chain removes gaps entirely, and the idle-math kernel says an exponential cost against linear supply makes a wall; the run asks where the rationing wall lands.
- Design: 40 beats; lag 0 is an and-then chain (open and close in one beat, payoff 1); otherwise payoff 1+lag per resolved gap; when growth^held exceeds the budget of 10 the oldest gap is forgotten. Growth swept 1.3/1.6/2.0/3.0, lags 0-8, plus a budget-40 case.
- Got right: Rationing beats the and-then chain (148 vs 40 at growth 1.6) and the cost curve sets a sharp optimum; raising the budget (a rest or reset, the prestige analogue) moved the best lag from 3 to 6.
- Where/why it failed: Past the wall the score collapses to 0, not to a gentler decline, because the forgotten gap is always the oldest, which is the next one due. My prediction that the best lag equals the affordable hold count was off by one: the opener of a gap is held at the same time as its pending questions, so best lag is affordable count minus 1.
- Fix: Set the longest withholding lag to the affordable simultaneous-question count minus one, and test one step past it; if story needs more, add a recap beat that restores the budget rather than lengthening the wait.
- Why this fix: The collapse is a cliff, so the safe choice is the lag just under it; a recap resets forgetting the way prestige resets the idle wall, so it moves the wall instead of fighting it.
- Rule of thumb: In a withholding structure treat viewer memory like an exponential cost: the best lag is the affordable open-question count minus one (7, 3, 2, 1 for growth 1.3, 1.6, 2.0, 3.0) and one beat further pays nothing, so rank gaps by due date and recap before the limit.
- Provenance (verified/assumed): Verified first-hand: the sandbox ran, the first run failed my prediction by one lag and the second printed PASS. The payoff of 1+lag and the oldest-forgotten rule are assumed model inputs, not measured audience data, so the numbers show structure only.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, ideas:GAME-DESIGN/idle-math/exponential-cost-over-linear-production-makes-the-wall, film/E3
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__sandbox-gap-lag-wall-from-exponential-hold-cost.py
- Prediction: Best lag equals the affordable hold count (4 at growth 1.6, budget 10) and lag 5 scores 0; and-then baseline stays below the optimum; budget 40 moves the best lag out.
- Observed: RESULT: PASS best gap lag is the affordable hold count minus 1 ([7, 3, 2, 1]), one lag past it collapses to [0, 0, 0, 0], and-then baseline 40, bigger budget moves best lag 3 to 6
- Scenarios: 1) growth 1.3; 2) growth 1.6; 3) growth 2.0; 4) growth 3.0; 5) and-then chain lag 0 baseline; 6) BREAK: lag one past the wall; 7) budget 40 wall pushed back
- Link: brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2

