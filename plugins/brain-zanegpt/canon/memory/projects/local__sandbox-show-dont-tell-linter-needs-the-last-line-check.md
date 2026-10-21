# local/sandbox-show-dont-tell-linter-needs-the-last-line-check — lessons

Project: local/sandbox-show-dont-tell-linter-needs-the-last-line-check. Newest first.

---

## E1 — show dont tell linter needs the last line check
- Date: 2026-09-30
- Project: local/sandbox-show-dont-tell-linter-needs-the-last-line-check
- Tags: [songwriting][lyrics][testing]
- What: An emotion-word versus sensory-noun ratio linter from the sense-bound-detail kernel passes every verse that shows images and then explains the meaning in its last line (3 of 3); adding a last-line check from the resist-explaining kernel got 8 of 8, but it also flags a show verse that ends on a colour word like blue.
- Why built: Compose the sense-bound-detail kernel with the resist-explaining-the-resolution kernel, to see whether the ratio linter alone can catch telling.
- Design: Eight hand-labelled verses (3 show, 2 tell, 3 show-then-explain) and a break probe added after the first run. Word lists for emotion words and sensory nouns; the ratio flag fires when emotion words outnumber sensory nouns; the last-line flag fires on an emotion word or a stating phrase (I realize, that's when I knew) in the final line.
- Got right: Ratio plus last-line check judged all 8 verses as labelled with no false flags on the 3 show verses, and blue in the blue truck mid-verse did not flip that verse.
- Where/why it failed: The ratio linter alone passed all 3 show-then-explain verses, since their images outnumber the one emotion word. The added probe showed the last-line check's limit: a show verse ending on the blue truck in the rain is falsely flagged, because the word list cannot tell a colour from a mood.
- Fix: Run both checks, and in the last-line check skip emotion words used as modifiers of a concrete noun (blue truck, cold coffee) or require a stating phrase or a first-person feeling clause.
- Why this fix: Explaining is a positional failure (the last line), which a whole-verse ratio cannot see; the remaining false flag comes from ambiguous words, which a noun-modifier test separates.
- Rule of thumb: A show-don't-tell ratio linter passes verses that show images then explain the meaning in the last line (3 of 3); add a last-line stating check (8 of 8), but skip colour words that modify a noun (the blue truck).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from its output. The verses, labels and word lists are hand-made and small.
- Composed: ideas:SONGWRITING/imagery/sense-bound-detail-beats-a-named-emotion, ideas:WRITING/short-form/resist-explaining-the-resolution
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__show-dont-tell-linter-needs-the-last-line-check.py
- Prediction: ratio alone passes both show-then-explain verses; ratio plus last line catches them with no false flags on show verses; blue truck does not flip its verse. Second run, written before it: the last-line check falsely flags a show verse ending on blue truck.
- Observed: RESULT: PASS ratio alone 5/8 and passes 3/3 image-then-explain verses; ratio + last-line check 8/8 with 0/3 false flags; blue-truck verse not flipped mid-verse, but a show verse ending on it is falsely flagged: True
- Scenarios: 1) show verses; 2) tell verses; 3) show-then-explain verses, built to break the ratio linter; 4) a show verse ending on the blue truck, built to break the last-line check.
- Link: https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__show-dont-tell-last-line-rebuild.py · observed RESULT: PASS ratio alone passes 4/4 show-then-explain; +naive last-line catches 4/4, 0/3 show FP, but 2/2 colour/temp-modifier endings falsely flagged; noun-modifier skip gives 11/11 and still flags 'i felt blue' · Rebuilt from What / Rule of thumb / Prediction only, with my own 11 verses (3 show, 2 tell, 4 show-then-explain, 2 show verses ending on a noun-modifying colour/temperature word), my own emotion and sensory lexicons (emotion set adds bitter, cold, hollow, grief, sorrow, hopeless) and my own stating phrases (adds "it means", "i understand", "i see now"). All three claims reproduce: the ratio linter alone passes every show-then-explain verse (4/4, original 3/3), ratio + naive last-line check catches 4/4 with 0/3 false flags on show verses and a mid-verse "the blue truck" does not flip its verse, and a show verse ending on "the blue truck in the rain" is falsely flagged. I pushed further than the original in two ways: (1) the original sandbox never implements the Fix (skip emotion words that modify a concrete noun) and only demonstrates the false flag; mine implements it and it reaches 11/11, clearing both "the blue truck" and "cold coffee" endings; (2) a negative probe that the fix does not over-skip: a last line "i felt blue" (predicative, not modifying a noun) is still flagged. The original fixture used 8 verses with a single blue probe added after the run and no temperature word; mine shares no verses or lines with it. Caveat unchanged: lexicons and labels are hand-made and tiny, and the noun-modifier test is a one-token lookahead that would miss "the blue old truck". · session; brain train rebuild pass round 3; session_01QGT1LfmPHPG99JEGaPhBwB
