# local/caution-turn-break-even-n-plus-one-and-question-budget-hazard — lessons

Project: local/caution-turn-break-even-n-plus-one-and-question-budget-hazard. Newest first.

---

## E1 — caution turn break even n plus one and question budget hazard
- Date: 2026-10-11
- Project: local/caution-turn-break-even-n-plus-one-and-question-budget-hazard
- Tags: [game-design][turn-based][model][testing]
- What: An exact-arithmetic model (no RNG) of a 20-turn journey with per-turn hazard h, testing the kernel that a caution costing N extra exposed turns needs at least N+1 protected turns to break even, then crossing it with the question-budget kernel by treating each question to a suspect as one hazard-exposed turn that raises deduction accuracy.
- Why built: The N-plus-one kernel was applied by no memory entry. It claims a structural, hazard-independent floor, so the sandbox looks for where the floor stops holding.
- Design: Caution survival gain = survival over N extra turns times survival with protected turns scaled by a multiplier m, divided by baseline survival. Constant hazards 3, 6 and 12 percent; m=0 and m=0.5; a back-loaded hazard rising 0.01 to 0.238; protection of the last M turns; and a detective with 5 suspects, recall accuracy 0.3, accuracy 0.3+0.7q/5 for q questions and 1.0 at q of 5 or more.
- Got right: With perfect protection the first strictly profitable M was N+1 at every N from 1 to 5 and every constant hazard, and for half protection M over N was 1.94 to 1.98 (about 2N), as the kernel says.
- Where/why it failed: The N+1 floor is not structural once hazard is not constant: with a back-loaded hazard the first profitable M was 2 at N=2 and 3 at N=4 (floor would be 3 and 5), and protecting only the last M turns paid off at M=1 for both N. My question-budget prediction also missed: with 5 suspects the best question count stayed 5 up to 14 percent hazard and fell to 4, 2, 1, 0 at 16, 20, 30, 40 percent, so hazard shrinks the optimal budget only past a threshold (the last question lifts accuracy from 0.86 to 1.0, a ratio of 1.16, and stops paying once 1/(1-h) exceeds it).
- Fix: Quote the N+1 rule with its condition, a roughly constant hazard over the journey, and where hazard is back-loaded compute the exact break-even from the hazard profile; treat a question or detour as paid for by the hazard-weighted turns it protects, not a fixed N+1.
- Why this fix: The break-even is the ratio of survival terms, so it depends on the hazard of the turns spent versus the turns protected; N+1 appears only when those hazards are equal.
- Rule of thumb: N+1 protected turns to repay N caution turns (about 2N at half protection, identical at 3, 6 and 12 percent hazard) holds only for a flat hazard; with a back-loaded hazard it fell to N-1 at N=4 and to M=1 when the protected turns are the last ones, and a 5-suspect question budget stays fully spent until hazard passes about 14 percent.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; all numbers are exact arithmetic. The back-loaded hazard profile and detective accuracy curve are my own choices, not measurements of any game.
- Composed: ideas:GAME-DESIGN/turn-based-ai/caution-costs-turns-that-are-themselves-exposed/n-plus-one-break-even-rule, ideas:GAME-DESIGN/deduction/question-budget
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__caution-turn-break-even-n-plus-one-and-question-budget-hazard.py
- Prediction: Floor N+1 for all constant hazards, about 2N at half protection, floor broken below N for back-loaded hazard, and best question count under 5 at 12 percent hazard (the last two partly missed on the first run: M=N at N=2 and best q stayed 5 at 12 percent).
- Observed: RESULT: PASS P1 floor N+1 at all h,N=True; P2 M*/N in [1.94,1.98]; P3 back-loaded first profitable M={2: 2, 4: 3} (<=N); P4 best q by h={0.0: 5, 0.03: 5, 0.12: 5} then at higher h={0.1: 5, 0.14: 5, 0.16: 4, 0.2: 2, 0.3: 1, 0.4: 0}; late-protection first profitable M={2: 1, 4: 1}
- Scenarios: 1) constant hazard 3, 6, 12 percent with perfect protection; 2) half protection; 3) back-loaded hazard and last-turn protection, built to BREAK the claim that the floor is structural; 4) question-budget detective across hazards 0 to 40 percent
- Link: scheduled brain train loop 2 pass 5 gap; session_015bpfiyHog3CaYStqh5GY3K
- Audited: 2026-10-11 · pass · Read the entry and reran its stored sandbox (PASS, same numbers). The model computes survival products rather than hard-coding results, and its criteria cover the stated scope: N+1 floor at 3, 6 and 12 percent hazard for N=1..5, M*/N of 1.94-1.98 at half protection, and a back-loaded profile that breaks the floor (M=2 at N=2, M=3 at N=4). Caveats the Rule of thumb should carry: the N+1 floor at perfect protection is close to an algebraic identity of the flat-hazard product, so P1 confirms the arithmetic more than it discovers anything; the "N-1" and "M=1" figures hold only for the one assumed hazard profile 0.01+0.012*i with the detour priced at turn-0 hazard; and the question-budget threshold near 14 percent depends entirely on the assumed accuracy curve (linear lift, full accuracy only at q>=S) and a 10-turn base, so it is not a general figure. The claim is abstract arithmetic, not about a real system, so modeled does not apply. · scheduled brain train loop 1 pass 3 audit; session_012sVtwcAGDa7irV2RPYCWfu
