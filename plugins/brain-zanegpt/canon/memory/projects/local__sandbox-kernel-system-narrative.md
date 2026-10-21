# local/sandbox-kernel-system-narrative — lessons

Project: local/sandbox-kernel-system-narrative. Newest first.

---

## E1 — a salience lru stage after exact fit stages never rotates
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-narrative
- Tags: [narrative][design][content][state]
- What: Applied the ideas kernel that a salience selector should rank by staged filtering (criteria, most specific, best tension fit, not recently shown, lexical tie-break) rather than one blended score. The blended score's failure reproduced with an exact threshold, and the recently-shown stage in the kernel's order turned out to be nearly inert.
- Why built: brain train gap listed the kernel as unapplied, and memory had no entry built on the selector.
- Design: 80 beats with 0 to 3 criteria over 8 boolean facts and a tension target, and 3000 seeded fact states. A blended score, criteria count x 100 minus the tension misfit x weight, against the staged selector, for weights 10, 100, 150 and 300. Then 300 selections with facts flipping every 25 steps and tension drifting, with the recently-shown (last 3) stage placed after the tension stage as in the kernel, first, or between specificity and tension fit.
- Got right: Counting repeats rather than trusting the stage's presence. The selector has an anti-repeat stage, so it looks covered.
- Where/why it failed: The blended score matched the staged selector in all 3000 states while the tension weight stayed at or below the specificity multiplier (weights 10 and 100) and picked a less specific beat in 78 states at 150 and 566 at 300. In the kernel's order, the recently-shown stage comes after the exact tension-fit stage, which almost always leaves one beat, so the selector repeated back to back 287 times in 300 picks over 6 distinct beats. Placing the stage first gave 0 repeats and 15 distinct beats but chose a less specific beat 142 times. Placing it between specificity and tension fit kept all picks most specific and gave 169 repeats over 9 distinct beats.
- Fix: Run the recently-shown filter before any stage that can narrow to one candidate by a continuous measure: between the specificity stage and tension fit keeps most-specific-wins intact. If repeats must go further, author more beats per specificity tier rather than moving the filter earlier.
- Why this fix: A filter can only rotate among the candidates still alive when it runs. After an exact best-fit stage there is almost never a second candidate, so the stage exists but does nothing.
- Rule of thumb: In a staged salience selector a not-recently-shown stage placed after an exact best-fit stage is inert (287 back-to-back repeats in 300 picks); place it between the specificity and fit stages (169 repeats, still 0 less-specific picks) rather than first (0 repeats but 142 less-specific picks); a blended score only matches staging while fit weight stays at or below the specificity multiplier (0 of 3000 wrong at 100, 78 at 150).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b03.py loop 14 in Pappydapimp69/Brain, deterministic. Observed: blended disagreements 0/0/78/566 of 3000; 287, 0 and 169 repeats with 6, 15 and 9 distinct beats and 0, 142 and 0 less-specific picks for the three placements. The beat pool is synthetic, not The Recursion's authored beats.
- Composed: ideas:SYSTEM/narrative/salience-selector-as-staged-filtering/most-specific-wins
- Link: session 2026-09-28, brain train gap batch 3 loop 14
- Sandbox: sandboxes/2026-09-28__train-gap-b03.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-play-the-legible-game.md#E1 · compatible · sandboxes/2026-10-09__legible-bots-vs-tag-reader-chain-completion.py · observed RESULT: PASS tag-bot 1.00 vs legible 0.467 (attach0.5,lru between); lru-after attach.8 0.327; naive verb guard misses 0, stripped 4. Attachment prediction was wrong (completion fell). First, easier game version gave 0.993 and was discarded. · https://claude.ai/code/session_01GfAHwy3Bruhswzp52FBWqr
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E40 · compatible · sandboxes/2026-10-09__narrative-ending-is-a-classifier-over-state-exhaustive-replay.py · observed RESULT: PASS 729 paths -> 4 endings {'dead': 268, 'holding': 97, 'drifting': 359, 'lost': 5}; handler-flag same-state conflicts 62 vs classifier 0; reorder changes ending for 49/81 multisets; staged overlap rule exact over 1331 states · scheduled brain train loop 2 pass 5; session_0177RNbpM9ouiodK1KEajhTr
