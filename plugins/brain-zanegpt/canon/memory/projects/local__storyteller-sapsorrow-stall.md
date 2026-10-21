# local/storyteller-sapsorrow-stall — lessons

Project: local/storyteller-sapsorrow-stall. Newest first.

---

## E1 — sapsorrow stall buys time only while demands outgrow capacity
- Date: 2026-10-17
- Project: local/storyteller-sapsorrow-stall
- Tags: [narrative][negotiation][simulation][sandbox]
- What: Modelled Sapsorrow's stall (gowns as pale as the moon, as sparkling as the stars, as golden as the sun, all
  provided by the king) as a run of demands whose cost grows by d each time against a maker whose capacity grows by g.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had the idle-game wall (cost growth over production
  growth) and walk-away power, but nothing on when a stall made of ever bigger demands buys time and when it only raises the price.
- Design: Stdlib, no randomness. Demand k costs 10*d^k units, the king's rate on it is 1*g^k units a day, so it takes
  10*(d/g)^k days; her escape needs 40 days; an optional ceiling refuses any single demand above it and ends the stall;
  the order of the demands can be reversed; one scenario averages over 24 equally likely ceilings the asker cannot see.
- Got right: Demands outrunning capacity (d=3, g=1.5) bought 70 days and the stall worked; matched growth (d=g=2) bought
  30, short of 40; capacity outrunning (d=1.5, g=3) capped at 20 days however many demands, while 10 demands ran the price to 1133.
  Over an unseen ceiling from 5 to 120, ascending averaged 37.1 days against 33.4 for largest-first, as predicted before that run.
- Where/why it failed: The BREAK reversed the same three demands against the mobilising king and bought 114.4 days, not 70,
  so escalating is not what buys the time; cost over capacity is. d>g is not enough on its own: under a ceiling of 25 the stall
  stopped at 10 days. A first edit adding the ceiling scenario broke the checks list with a bad string replace; fixed and rerun.
- Fix: Before stalling with demands, compare how fast each demand grows with how fast the other side can scale up, add up the
  days against the time the escape needs, and pick the order by what is known of his ceiling: largest first when he has none in
  range, smallest first when it is unknown, so the cheap demands bank their days before one is refused.
- Why this fix: Time bought per demand is its cost over his current capacity, so a side that mobilises faster than the demands
  grow turns each new ask into fewer days, and the series converges to t0/(1-d/g) while the bill keeps climbing; a refusal
  ends the stall, so an opener over his ceiling banks nothing.
- Rule of thumb: Escalating demands buy growing time only while each ask grows faster than his capacity and stays under his
  ceiling; when he scales faster they just raise his price, and escalating order beats largest-first only when his ceiling is unknown.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode's three gowns and the king providing them checked
  against Wikipedia's Storyteller article, and the parallel demands against Wikipedia's Allerleirauh and Donkeyskin pages cited in the kernel.
- Composed: ideas:GAME-DESIGN/idle-math/exponential-cost-over-linear-production-makes-the-wall, ideas:NEGOTIATION/batna/walk-away-power
- Sandbox: sandboxes/2026-10-17__sapsorrow-stall-buys-time-only-while-demands-outgrow-capacity.py
- Prediction: d=3,g=1.5 70 days works, price 130; d=g=2 30 days short of 40, price 70; d=1.5,g=3 17.5 days, 10 demands 19.98 days
  (cap 20) at price 1133; ceiling 60 refuses demand 3 after 30 days; BREAK descending 114.4 days > 70; static king 130 either order;
  added before reruns: descending against ceiling 60 refused at once (0 days); d>g under ceiling 25 stops at 10 days; unseen
  ceiling 5..120 ascending about 37.1 days vs descending about 33.4.
- Observed: RESULT: PASS d>g buys 70 days, d=g 30 (short of 40), d<g caps at 20 days while price climbs to 1133; ceiling refuses
  demand 3; BREAK: descending order buys 114.4 days vs 70, so the time comes from cost over capacity, not from escalating, unless a
  ceiling is near (descending is refused at once, 0 days vs 30); d>g under a ceiling of 25 still stops at 10 days; over an unknown
  ceiling escalating averages 37.1 days vs 33.4 largest-first
- Scenarios: 1) tale-like matched growth d=g=2; 2) demands outrun d=3 g=1.5; 3) capacity outruns d=1.5 g=3, 3 and 10 demands;
  4) ceiling of 60; 5) BREAK: same demands in descending order; 6) static king, both orders; 7) descending against the ceiling;
  8) d>g under a ceiling of 25; 9) unseen ceiling averaged over 5..120, both orders
- ZaneGPT verdict: weak — the "grows faster than capacity" half is a restatement of the formula (10*(d/g)^k), and the "escalating beats largest-first under an unknown ceiling" half rests on a 37.1 vs 33.4 gap from one hand-picked ceiling distribution that nothing here shows is robust.
- Hidden assumption: The king's response is fixed and mechanical: he always complies, never replans, and never changes his price, so "days bought" depends only on cost over capacity, with the order of demands mattering only through a ceiling.
- Would prove it wrong: A run where the king's capacity responds to the demands, for example by pre-building after seeing the pattern or by drawing on stock already made. Escalation would then buy nothing even with d>g and a known ceiling. Another refutation is a ceiling that scales with g or d, which would make "stays under his ceiling" circular. Descending beating ascending at every unseen ceiling would also refute the order claim, and the simulation partly gives this: 114.4 vs 70 days with no ceiling.
- Break scenario: d=3, g=1.5, with a ceiling the king raises 20% each time he is refused or pressed (adaptive), or one demand priced below its own predecessor. The 24-ceiling average has only one prior and one spacing (5..120). Run it again with ceilings clustered low, say 5..30. Escalating then stalls at about 10 days while largest-first is refused at once, so the claim "escalating beats largest-first when the ceiling is unknown" flips with the prior, not with the mechanism. Skewing the same range high gives the opposite result.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 0af1527d074c
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

