# local/storyteller-term-cure — lessons

Project: local/storyteller-term-cure. Newest first.

---

## E1 — term cure early costs more short leaves a mark
- Date: 2026-10-17
- Project: local/storyteller-term-cure
- Tags: [narrative][game-design][curse][sandbox]
- What: Modelled the two term-limited curses in The StoryTeller: Hans My Hedgehog's spell broken three days
  early (a search penalty follows) and The Three Ravens' last shirt short one sleeve (one brother keeps
  a wing), as freedom-time arithmetic and as partial versus all-or-nothing credit.
- Why built: Brain train on elements of Jim Henson's The StoryTeller beyond The Luck Child; canon had no kernel
  for how a curse with a term should punish acting early or finishing short.
- Design: Part 1: the spell lifts at day T; acting at T-3 fails and adds a penalty P, freedom at T-3+P, swept
  over P = 1, 2, 3, 30, 300. Part 2: six shirts, the last at 0.95; partial credit restores each whole
  shirt and counts the missing parts as visible marks; all-or-nothing restores nobody unless all six are
  whole.
- Got right: With penalties of 30 or 300 days, acting three days early lost (free at 127 and 397 against 100);
  one missing sleeve restored 5 of 6 brothers and left exactly 1 wing under partial credit, matching
  the Grimm text.
- Where/why it failed: The rule only teaches patience when the penalty is bigger than the days saved: penalties of 1, 2 and 3
  days made acting early pay or tie; and all-or-nothing credit turned the same missing sleeve into 0
  of 6 restored with no mark left.
- Fix: Price early action above the time it saves, and give a term cure partial credit per part with the
  shortfall left visible, so finishing short changes the ending instead of erasing it.
- Why this fix: The penalty is what makes waiting the right play, and partial credit is what turns a near miss into
  a lasting, visible token the ending can rest on.
- Rule of thumb: Give a cure with a term two failure modes: acting early must cost more than it saves, and finishing
  short should leave a visible remainder per missing part rather than voiding the whole cure.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller article and the source-tale pages cited in the kernel. Model parameters are toy values.
- Composed: ideas:SONGWRITING/endings/decisive-choice-leaves-a-token
- Sandbox: sandboxes/2026-10-17__term-cure-early-costs-more-short-leaves-a-mark.py
- Prediction: Early action loses only when the penalty exceeds the 3 days saved; one missing sleeve gives 5 of 6
  restored plus 1 wing under partial credit and 0 under all-or-nothing.
- Observed: RESULT: PASS penalties 1-3 make acting early pay or tie, 30 and 300 lose (free at 127, 397 vs 100);
  partial credit 5 of 6 restored and 1 wing, all-or-nothing 0.
- Scenarios: 1) penalty 30; 2) penalty 300; 3) partial credit; 4) all-or-nothing; 5) BREAK: penalties 1-3 days
- ZaneGPT verdict: weak — the rule is arithmetic restated, since both predictions follow from the model's definitions and the PASS only confirms that, while the sweep skips P between 3 and 30, treats the penalty as certain, and leaves partial credit's perverse incentive untested.
- Hidden assumption: The model's numbers are the argument. "Early action loses only above 3 days" is true by construction (T-3+P vs T), and "5 of 6 vs 0" is just the two credit rules as the model defines them. Nothing here tests whether the penalty is real, known to the actor, or independent of how early they act, and the 0.95 shirt is assumed to count as "missing" while still earning its "whole" restoration.
- Would prove it wrong: A variant where the penalty scales with earliness or is unknown in advance, or where partial credit adds an incentive to ship a deliberately short cure. If either flips the early-vs-wait ordering or makes the short cure the preferred one, the rule is wrong. A threshold other than 3 days would do the same.
- Break scenario: P = 3.5 or P = 0 with a stochastic penalty (30% chance of 300, otherwise 1). The sweep never samples between 3 and 30, and it never prices risk. The expected cost of acting early is 90.7 days against 3 saved, so the rule's "must cost more than it saves" can't be applied without knowing the distribution. Add a cure that is 5 of 6 shirts on purpose: partial credit makes it free to skimp, with no incentive to finish.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 50f4654f5ff3
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

