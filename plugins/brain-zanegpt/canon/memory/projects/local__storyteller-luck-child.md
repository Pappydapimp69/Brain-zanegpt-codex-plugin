# local/storyteller-luck-child — lessons

Project: local/storyteller-luck-child. Newest first.

---

## E1 — luck child backfire attacks feed the hero
- Date: 2026-10-17
- Project: local/storyteller-luck-child
- Tags: [narrative][antagonist][simulation][sandbox]
- What: Modelled The Luck Child's backfire chain, where each of the king's moves against the boy becomes the boy's
  next step, as a hero with no moves of his own whose position grows only when an attack is converted into it.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had causally chained villain escalation and
  habituation, but nothing on a story where the antagonist's failed attacks are the hero's whole progression.
- Design: Stdlib loop of up to 6 king attacks; force = the king's motive given the hero's position; backfire adds the
  force to the hero, plain failure adds nothing; audience response = force x 0.5 per earlier attack as strong or
  stronger. Kings: motive grows with threat (1 + P), flat motive (1), a BREAK king deterred by strength, plus
  half conversion, a flat strong king (force 4) and a sublinear motive (1 + 0.1P).
- Got right: Threat-driven backfire ran forces 1, 2, 4, 8 and hit the goal on attack 4 with response 15.00; plain failure
  left the hero at 0 with response 1.97; flat-motive backfire reached only 6 of 10 in six attacks, response 1.97.
- Where/why it failed: Backfire alone did not escalate: with a flat motive the hero crept up and the response decayed exactly as
  with plain failure, and the BREAK king who backs off once the hero is strong stopped after one attack of 3,
  stalling the hero at 3 for good. A flat strong king (force 4) also reached the goal, on attack 3, but with
  response 7.00, so growth buys the escalation, not the arrival; the habituation rule counts any rise as new,
  so a sublinear king's tiny rises (1.0 to 1.61) dodge it, a known gap in the toy.
- Fix: Tie the antagonist's motive to the hero's gains (fear of a prophecy, then greed) so each conversion raises
  the next attack's force, and convert the whole force of each attack into the hero's next asset.
- Why this fix: The doubling comes from the loop, attack feeds hero and hero feeds motive; break either link and the
  attacks repeat at one size, which the audience habituates to and the hero barely moves on.
- Rule of thumb: When a passive hero rises only through the villain's failed attacks, make the villain's drive grow
  with each gain; a one-size villain flattens the escalation even when strong enough to deliver the goal, and a
  deterred one stalls the hero.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode and tale details checked against
  Wikipedia's Storyteller article and the Grimm tale text cited in the kernel. Model parameters are toy values.
- Composed: ideas:narrative-design/arc-structure/power-creep-accounting, ideas:ORAL-STORYTELLING/controlled-escalation/habituation
- Sandbox: sandboxes/2026-10-17__luck-child-backfire-attacks-feed-the-hero.py
- Prediction: Threat-driven backfire: forces 1, 2, 4, 8, goal on attack 4 (P = 15), response 15; plain failure: P = 0,
  response under 2; flat-motive backfire: P = 6, goal missed, response under 2; deterred king: one attack of 3,
  stall at 3. Added after run 1: half conversion still reaches the goal (attack 6, response above 15); flat
  strong king reaches it on attack 3 with response 7; sublinear motive misses (P under 8).
- Observed: RESULT: PASS threat-driven backfire reaches the goal in 4 attacks (forces 1,2,4,8, response 15.00); plain
  failure stays at 0 (response 1.97); flat-motive backfire only P=6 in 6 (response 1.97); deterred king stalls
  the hero at P=3; flat strong king also reaches the goal (attack 3) but response 7.00; half conversion still
  escalates (goal attack 6, response 20.78); sublinear motive misses (P=7.72)
- Scenarios: 1) backfire, motive grows with threat; 2) plain failure, same king; 3) backfire, flat motive; 4) BREAK:
  backfire with a king deterred by the hero's strength; 5) half conversion; 6) flat strong king; 7) sublinear motive
- ZaneGPT verdict: weak — the sim shows only that a self-reinforcing motive compounds, which is true by construction (force = 1+P is a doubling recurrence), and the strong-flat control undercuts the "must grow" wording; the real finding is "needs enough total force, ideally escalating," which has not been separated from simple magnitude.
- Hidden assumption: Escalation is the goal, and "reaches P=15 in ≤6 attacks" measures a good story. The rule also assumes the villain's drive can be tuned per-gain at all, when the run shows flat strong king (force 4) hits the goal on attack 3, faster than the "correct" growing king (attack 4), so growth isn't what delivers the goal; magnitude is.
- Would prove it wrong: A flat-motive king with force set so the sum over 6 attacks reaches 15 (e.g. flat 2.5) hitting the goal, or any growing-motive king failing at a plausible base force. The strong-king result already shows "a one-size villain flattens the escalation even when strong enough to deliver the goal" only means the response curve is flatter (7.00 vs 15). That is a claim about audience response, not about reaching the goal, and the rule conflates the two.
- Break scenario: Growth with decay: motive = (1 + P) but the king's attacks have a cap, or the hero's position is lost on each plain failure by a fraction (negative drift), so the king can't be both "driven by gain" and win. Also try a growing king whose base is 0.3 (motive 0.3·(1+P)): the P=0 start never compounds past ~0.3 per attack, and the rule predicts escalation that the arithmetic denies. Same for the sublinear case, which already missed (P=7.72) and shows the rule is knife-edge on the exponent, not robust.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest aeec9162f9f2
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

