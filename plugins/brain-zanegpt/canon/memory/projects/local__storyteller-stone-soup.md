# local/storyteller-stone-soup — lessons

Project: local/storyteller-stone-soup. Newest first.

---

## E1 — story short stone soup small toppings fill a pot no one gives whole
- Date: 2026-10-17
- Project: local/storyteller-stone-soup
- Tags: [narrative][persuasion][simulation][sandbox]
- What: Modelled the stone soup trick from A Story Short (a stone in a cauldron of water, the cook adding ingredients to improve
  it) as a run of asks where each yes depends on how far along the pot looks, against a single full request and equal shares.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had endowed progress (a pre-stamped card) and the goal gradient,
  but nothing on getting a whole thing out of people by framing every ask as a small topping to something already underway.
- Design: Stdlib, no randomness. Pot worth 12; an ask for an item of cost c gets a yes iff c <= base + k*p, where p is (seed +
  real units given)/12; the stone is a seed perceived as 2 and worth 0; refused items are skipped; one pass in a fixed order.
  Main constants base 0.8, k 4; reruns at 0.4 + 4p and 1.5 + 2p test how much the result rests on those numbers.
- Got right: Stone plus cheap toppings first filled 12/12 with 6 yeses; with no stone, a single ask for the whole 12, or six
  equal asks of 2 with nothing underway, the pot got 0; the same toppings dearest first got only the two 1-unit items, 2/12.
  Under all three threshold settings the stone never did worse than no stone and cheapest-first never worse than dearest-first.
- Where/why it failed: The full pot is a property of the constants, not of the trick: at 0.4 + 4p the pot stopped at 2/12 and
  at 1.5 + 2p at 6/12 (2/12 without the stone). A ladder gap (a 4 right after two 1s) stalled at 2/12, seeing through the stone
  after 3 yeses stalled at 6/12, and the BREAK meat worth 6, above the top willingness of 4.8, was never given (pot 6/12).
- Fix: Start with a visible seed that makes the thing look underway, ask for the cheapest additions first, and check that every
  step of the ladder is affordable at the progress the steps before it reach; split or source any big-ticket item another way.
- Why this fix: Each yes raises the apparent progress that sets the next person's willingness, so cheap early yeses compound
  only while the next item fits inside the willingness they have built; one step too dear stops every ask after it.
- Rule of thumb: Frame each ask as a small topping to something already cooking and order them cheapest first; it fills the
  pot only if each next item is affordable at the progress already shown, and no piece is above one giver's top willingness.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode's stone, cauldron and the cook adding ingredients
  and later demanding the boiling checked against Wikipedia's Storyteller article, the fable against Wikipedia's Stone Soup page.
- Composed: ideas:UX/step-navigation/goal-gradient-progress-indicator, ideas:REINFORCEMENT/progress-design/effort-accelerates-as-remaining-distance-to-a-fixed-goal-shrinks
- Sandbox: sandboxes/2026-10-17__story-short-stone-soup-small-toppings-fill-a-pot-no-one-gives-whole.py
- Prediction: Stone + cheap toppings 12/12 with 6 yeses; no stone 0/12; one full ask 0/12; six equal asks of 2 with nothing
  underway 0/12; dearest first 2/12; stone seen through after 3 yeses 6/12; BREAK meat worth 6 refused, pot 6/12; added before
  rerun: ladder gap 2/12; 0.4+4p stone 2, no stone 0, dear-first 2; 1.5+2p stone 6, no stone 2, dear-first 2.
- Observed: RESULT: PASS stone + cheap toppings fills 12/12 where no stone, a full ask or 6 equal asks get 0; dear-first gets 2/12;
  seeing through the stone after 3 yeses stalls at 6/12; BREAK: a 6-unit meat above top willingness 4.8 is never given, pot stops at
  6/12; a ladder gap (a 4 after two 1s) stalls at 2/12; under 0.4+4p and 1.5+2p the pot reaches only 2/12 and 6/12, the stone and
  cheapest-first never worse but the full pot depends on every step being affordable
- Scenarios: 1) tale: stone, cheap toppings first; 2) no stone; 3) one full request, and six equal asks with nothing underway;
  4) dearest toppings first; 5) stone seen through after 3 yeses; 6) BREAK: meat worth half the pot; 7) ladder gap;
  8) threshold 0.4 + 4p, three orderings; 9) threshold 1.5 + 2p, three orderings
- ZaneGPT verdict: weak — the 12/12 result follows from tuning (the reruns give 2/12 and 6/12), so the data supports only "ordering helps when willingness rises with progress and every step is affordable", not the general rule of thumb.
- Hidden assumption: Each giver's willingness is a deterministic, monotone function of visible progress alone (c <= base + k*p), so the stone's perceived 2 units is credited as real progress and cheap-first steps always clear the threshold. The sim hard-codes the very mechanism the rule claims to discover, and a real giver's yes can also depend on the asker, on fairness, or on suspicion of the frame.
- Would prove it wrong: A run where the threshold is not increasing in p, for example a flat cap or one that falls as the pot fills (fatigue or "why am I the only one giving"), and cheap-first with a stone still stalls below 12/12 while a different order or a single full ask does as well or better. Or a rerun with the stone's perceived value at 0 or 1, where the pot still fails. The reruns already show 2/12 and 6/12 under shifted constants, so "fills the pot" is a property of the chosen numbers, not of the rule.
- Break scenario: Keep base 0.8, k 4, but make each giver single-use with an individual cap of 1.5 and a threshold that drops by 0.3 per prior yes seen (donor fatigue). Cheap-first then has to buy twelve units from givers who each give at most 1.5, with willingness shrinking as the pot fills, so it stalls well under 12/12, and a mix of big asks early (before fatigue) beats it.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest dd67c04cf1c8
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

