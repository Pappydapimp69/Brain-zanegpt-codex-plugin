# local/trope-catalog-native-axis-redundant-swap — lessons

Project: local/trope-catalog-native-axis-redundant-swap. Newest first.

---

## E1 — trope catalog native axis redundant swap
- Date: 2026-10-15
- Project: local/trope-catalog-native-axis-redundant-swap
- Tags: [game-ads][comedy][ideation][sandbox]
- What: The premise slot machine (one real trope plus one absurd swap on a mismatch axis) was run over the 20-trope catalog with the study's five axis names verbatim. If a swap must land on an axis the trope does not already use, 72 of 100 cells are legal (18 parody-safe tropes times 4 axes), 54 if each trope natively uses two axes, and any batch needing a distinct axis per idea caps at 5 ideas although 18 tropes exist.
- Why built: The slot machine says pick a trope and swap one thing; the catalog lists the tropes; the source check says labels must be verbatim. I wanted to know how much of the 20 by 5 grid is actually usable and whether a mislabelled axis changes the grid.
- Design: Each trope got one native axis by my own judgement (for example pull-the-pin is gameplay disguise, celebrity skit is popular externalization), two banned tropes (won-real-money testimonial, sexualised reveal) were excluded as unsafe to parody, and a cell is legal when the swap axis is not native. Batch size is a bipartite matching of distinct tropes to distinct axes. Scenarios: one native axis; a second native axis per trope; the old label borrowed fame in place of popular externalization (built to BREAK label matching). No randomness.
- Got right: Predictions held exactly: 18 safe tropes, 72 legal cells, max batch 5 for both native-axis settings, 54 legal cells with two native axes.
- Where/why it failed: A paraphrased axis name silently changes the grid: with the old label, the 3 tropes natively on that axis no longer matched any axis string, so legal cells inflated from 72 to 75 and the redundant swap was offered as legal. The 5-idea axis cap also means batch variety beyond 5 must come from a second dial, not from more tropes.
- Fix: Quote axis labels verbatim from the source, have the generator reject any swap axis string that is not in the verbatim list, and treat the axis count as the batch cap unless a second variation dial is added.
- Why this fix: Rejecting unknown axis strings turns a silent grid change (72 to 75) into a loud error, and naming the axis cap stops a planner from promising 10 distinct-axis ideas it can never produce.
- Rule of thumb: Before generating a fake-ad batch, count legal cells as non-native swaps only (72 of 100 here, with my own native-axis labels) and expect at most 5 distinct-axis ideas; a paraphrased axis name changed the grid by 3 cells without any error.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the native-axis assignment per trope is my own judgement and the safe/banned split follows the catalog's own notes, so the exact counts are assumed inputs.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns, ideas:GAME-ADS/tropes/twenty-trope-catalog-pick-one-name-the-genre-it-sells, fake-ad-kernel-source-check/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__trope-catalog-native-axis-redundant-swap.py
- Prediction: 18 of 20 tropes safe, 72 legal cells with one native axis each, max distinct-axis batch 5, two native axes at most 54 cells, and the old label inflating legal cells by one per native trope; wrong if legal cells were not 72. Assumption: each trope has a knowable native axis.
- Observed: RESULT: PASS safe 18/20, legal cells 72 (one native) / 54 (two native), max distinct-axis batch 5, old label 'borrowed fame' inflates legal cells by 3 (=3 tropes)
- Scenarios: 1) one native axis per trope; 2) two native axes per trope; 3) old paraphrased axis label (BREAK for label matching); 4) matching for max batch under distinct trope and axis
- Link: session_01A5ZkeepCfk7CHTSxS7qQ4k

