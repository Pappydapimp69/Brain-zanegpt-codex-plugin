# local/storyteller-sapsorrow — lessons

Project: local/storyteller-sapsorrow. Newest first.

---

## E1 — sapsorrow a test keyed to the last holder picks her kin
- Date: 2026-10-17
- Project: local/storyteller-sapsorrow
- Tags: [narrative][worldbuilding][simulation][sandbox]
- What: Modelled Sapsorrow's ring law as a selection test keyed to the previous holder: the ring fits within one
  unit of the dead queen's finger size, and daughters' sizes regress partway toward the kingdom mean, so the
  run measures how much more likely a daughter is to fit than a stranger, and who gets picked from a crowd.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had nothing on why a law that copies the last
  holder ends up choosing the one person the ruler cannot accept.
- Design: Stdlib, deterministic closed-form normal fits. Sizes ~ Normal(50, 4), tolerance 1, 1000 strangers and
  3 daughters, heritability 0.5. Runs: typical queen, 2 sd out, 3 sd out, BREAK with no inheritance, a law
  barring the household, then a looser ring, a 2 percent caste of strangers near her size (BREAK2),
  stronger inheritance, and a crowd test comparing random trying order with daughters trying first.
- Got right: Kin enrichment rose 1.15 (typical queen) to 4.27 (2 sd) to 21.98 (3 sd), held at 19.01 with a ring
  twice as loose and rose to 83.88 with heritability 0.8; with no inheritance it was exactly 1.00 and the
  exclusion clause took the daughters' share to 0. At 2 sd, daughters trying first spring the trap 0.316 of
  the time against 0.0126 in random order (25x).
- Where/why it failed: The first 3 sd guess was about 10 and the run gave 22, so the pull grows faster than guessed.
  A 2 percent caste of strangers clustered near her size cut the 3 sd enrichment from 21.98 to 3.30, so the
  pull depends on her being unusual in the whole pool, not just against the average. In random order daughters
  were at most 6 percent of fitters at heritability 0.5 but 20 percent at 0.8, so the crowd claim weakens as
  inheritance gets stronger.
- Fix: Key the test to a trait of the last holder that nobody else in the pool shares, and let the kin try it
  first or keep the pool small, because favouring kin per person does not make them win a crowd.
- Why this fix: Enrichment explains why the ring fits the daughter better than chance, but only the order of trying
  makes the trap spring on the ruler before any stranger is found, and a cluster of look-alikes erases it.
- Rule of thumb: A test copied from the last holder favours her nearest kin, more so the rarer her trait is in the
  pool, yet still seldom picks them from a crowd; to trap a ruler with his own law, have the kin try first.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against
  Wikipedia's Storyteller article and the source-tale pages cited in the kernel. Sizes and heritability are toy values.
- Composed: ideas:STATISTICS/regression-to-the-mean/galtons-1886-height-data, ideas:RPG/quest-design/existence-gating-solves-when-not-which
- Sandbox: sandboxes/2026-10-17__sapsorrow-a-test-keyed-to-the-last-holder-picks-her-kin.py
- Prediction: Round 1: enrichment about 1.1-1.2 typical, about 4 at 2 sd, about 10 at 3 sd, 1.0 with no
  inheritance, 0 share under exclusion. Round 2 (written before rerun): looser ring 5-20, caste below 5,
  h=0.8 above the 3 sd value, daughters-first about 0.32 against about 0.013 in random order.
- Observed: RESULT: PASS kin enrichment 1.15 -> 4.27 -> 21.98; no inheritance 1.00; exclusion share 0; looser
  ring 19.01; 2% caste 3.30; h=0.8 83.88; daughters-first 0.316 vs random order 0.0126 (3 sd magnitude was
  double the first guess).
- Scenarios: 1) typical queen; 2) 2 sd; 3) 3 sd; 4) BREAK: no inheritance; 5) law bars the household; 6) looser ring; 7) BREAK2: caste near her size; 8) crowd order test; 9) heritability 0.8
- ZaneGPT verdict: weak — the direction is plausible and the PASS is real, but the rule's "rarer means more" and "have the kin try first" parts are shown only inside one parametric model that you wrote and then fit, and the 3 sd miss by 2x shows the closed form is not yet understood.
- Hidden assumption: Fit depends only on a heritable, continuous finger size with fixed Normal(50, 4) variance, and the daughters' trait regresses toward the mean at a known rate. The rule assumes the enrichment is a general property of "tests copied from the last holder". But the three run-to-run numbers only show the math of a narrow-tolerance Gaussian: a ±1 window on sd 4 captures about 20% of the density near the mean, so the enrichment is set by the tolerance-to-sd ratio and h, not by "rarity".
- Would prove it wrong: A sweep that holds the queen's z-score fixed and varies only tolerance (or the pool's sd). If enrichment at 3 sd swings by an order of magnitude (it did: 21.98 vs 19.01 for a looser ring, and 83.88 at h=0.8), then "more so the rarer the trait" is really "more so the tighter the window and the stronger the inheritance". A flat enrichment at a different kingdom sd, or one that falls as the ring loosens at 3 sd, would refute the rarity claim.
- Break scenario: Make the trait non-heritable but shared by environment, e.g. the queen's household all wore rings and their fingers swelled to one size, and a non-kin guild shares the same swelling. Then kin enrichment drops toward 1 while the test still "copies the queen", and the "daughters-first traps a ruler" move fails: they would fit no better than the guild, and the 0.316 figure becomes a share of whoever tries first, not of kin.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest ddfa8fd9f51e
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

