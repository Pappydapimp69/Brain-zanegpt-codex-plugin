# local/storyteller-trapped-death — lessons

Project: local/storyteller-trapped-death. Newest first.

---

## E1 — trapping a necessary sink breaks the world
- Date: 2026-10-17
- Project: local/storyteller-trapped-death
- Tags: [narrative][economy][simulation][sandbox]
- What: Modelled The Soldier and Death as a faucet and sink: a village of all ages gains 10 people a year,
  everyone ages, Death takes everyone at 80, and from year 40 Death is tied in the sack for 20 years.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had the faucet/sink coverage kernel for economies
  but nothing on what capturing a necessary force should do to a story's world.
- Design: Stdlib yearly loop from an existing village (ten at each age 0-79), births 10 a year, death at 80
  unless trapped; coverage = deaths per year over births; waiting = people past 80 who cannot die;
  control with no trap and a BREAK run where nobody ages.
- Got right: Untrapped coverage held at 1.00 with nobody waiting; with Death in the sack coverage fell to 0.00 and
  200 people were left waiting by year 59, all cleared within two years of release.
- Where/why it failed: The first run started from an empty village, so nobody reached 80 during the trap and the effect read
  as zero; and the BREAK run with no aging left 0 waiting, so the cost depends entirely on decline
  continuing while the sink is gone.
- Fix: Start from a populated world, keep inflow and decline running while the sink is trapped, and let the
  backlog grow each turn, so releasing the force is forced by what piles up rather than by a rule.
- Why this fix: A trapped sink only reads as a mistake if the audience watches the backlog build, and an empty or
  ageless world hides it completely.
- Rule of thumb: If the hero traps a force that also clears something away, keep the inflow and decline running and
  show the backlog grow; without ongoing decline, trapping it costs nothing.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller article and the source-tale pages cited in the kernel. Model parameters are toy values.
- Composed: ideas:ECONOMY/core/faucets-and-sinks-target-95-to-105-percent-coverage
- Sandbox: sandboxes/2026-10-17__trapping-a-necessary-sink-breaks-the-world.py
- Prediction: With Death trapped, coverage drops to 0 and the number waiting grows every year of the trap; with no
  aging the trap leaves nobody waiting.
- Observed: RESULT: PASS coverage 1.00 to 0.00, 200 waiting by year 59, cleared on release; no-aging trap leaves
  0 waiting (first run from an empty village showed 0, fixed by seeding all ages).
- Scenarios: 1) no trap; 2) trapped years 40-60 then released; 3) BREAK: trapped with no aging
- ZaneGPT verdict: weak — the "no aging means no backlog" control is real and informative, but the main prediction restates the model's own definition of waiting, so PASS shows the arithmetic works, not that the rule generalizes.
- Hidden assumption: The rule assumes the backlog is caused by the inflow-and-decline structure, but in this model "waiting" is defined as people past 80 who cannot die. That makes the backlog nearly tautological: with births constant and the trap on, 10 per year pile up by construction. The prediction can't fail unless the code is buggy, and the one failure already seen (the empty-village run) was a seeding bug, not a test of the rule.
- Would prove it wrong: A run with ongoing aging and a trap where waiting stays flat or shrinks. For example, if births fall to 0 during the trap, or if the waiting count includes people who would have died anyway, the backlog would stop tracking "inflow minus decline." Another refutation is a trapped run in which waiting doesn't equal trap years × 10 (here, 200 by year 59 is exactly 20 × 10, so it only confirms the arithmetic).
- Break scenario: Make the clearing force partial or mortal-dependent. Death takes only a fraction of the age-80 cohort each year (say 50%), or the trap holds only some people while others still die. Then run the rule's two conditions (inflow on, decline on) against that. If waiting grows in proportion to the blocked share, the rule survives in a weaker form. If waiting grows even when the trapped force's share of total decline is small, or doesn't grow because other causes of death absorb it, the rule's "clears something away" framing is too coarse.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest e25f5ce59661
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

