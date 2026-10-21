# local/stacked-redraw-gate-cost — lessons

Project: local/stacked-redraw-gate-cost. Newest first.

---

## E1 — stacked reject and redraw gates multiply generation cost in a fake ad batch
- Date: 2026-10-16
- Project: local/stacked-redraw-gate-cost
- Tags: [comedy][game-ads][testing][sandbox]
- What: In a 16-video fake-ad batch where each video must pass a verbatim-label gate (30% of drafts paraphrased and rejected) and a name gate (no name within one edit of an earlier name), the cost per accepted video was 1.42 draws with the label gate alone, 1.02 with the name gate alone, and 1.45 with both, equal to the product 1.45; with 2-syllable names the cost rose to 1.83.
- Why built: Loop-2 train pick, hand-chosen because the picker repeated a loop-1 target: it joins the every-video-gets-its-own-joke kernel, the fake-ad kernel source check (verbatim labels) and the invented-name check, to price what stacking the label and name gates costs, since earlier lessons only showed that each gate is needed.
- Design: Seeded script, 300 batches per setting, three-syllable names from 12 syllables unless noted; a draw is rejected when the label is paraphrased (probability 0.3) or the name is within edit distance 1 of an earlier name; counts draws divided by videos accepted.
- Got right: The two gates behaved independently: the combined cost 1.45 matched the product of the single-gate costs 1.42 and 1.02, so each gate can be sized separately, and the label gate dominates at three syllables.
- Where/why it failed: My band was wrong on one side: I expected 2-syllable names to more than double the combined cost (over 2.9), and it reached only 1.83, because with 144 names a 16-video batch still finds room; the script prints FAIL for that band only, not for the product result.
- Fix: Budget about 1/(1-p) draws per video for the label gate and treat the name gate as nearly free at three syllables; cut the paraphrase rate (a closed list in the prompt) before lengthening names.
- Why this fix: The label gate rejects a fixed share of every draw while the name gate rejects only as the batch fills, so the label rate is the cost driver until names get short.
- Rule of thumb: Stacked redraw gates multiplied: label 1.42 x name 1.02 gave 1.45 draws per video (observed 1.45) at 30% paraphrase, so price each gate alone; 2-syllable names lifted the total to 1.83.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the 30% paraphrase rate and the syllable pool are my own assumptions, not measured, and the FAIL line comes from my own band for 2-syllable names, not from the product result.
- Composed: ideas:AI-VIDEO/every-video-gets-its-own-joke-and-script, fake-ad-kernel-source-check/E1, invented-name-check-exact-match-misses-lookalikes/E1
- Picked-by: new-half
- Distinct from: brain-auto-training/E23 (that lesson shows the engine counter needs verbatim labels; this prices the label gate and name gate together in draws per video and shows they multiply).
- Sandbox: sandboxes/2026-10-16__stacked-reject-and-redraw-gates-multiply-generation-cost-in-a-fake-ad-batch.py
- Prediction: Hidden assumption: the two gates interact so the cost is worse than the product. Expected combined cost equal to the product within 15% and 2-syllable names more than doubling it; it would be wrong if the combined cost differed from the product by over 15%.
- Observed: RESULT: FAIL draws per video none 1.00 label 1.42 name 1.02 both 1.45 (product 1.45); 2-syllable both 1.83 (product held; the more-than-double band for 2-syllable names was refuted)
- Scenarios: 1) no gate; 2) label gate only; 3) name gate only; 4) both gates; 5) both with 2-syllable names, built to break the independence claim.
- Link: scheduled brain train auto loop 2 pass 5 (gap, hand-picked); session_01GYKQrKfm5FQsrnyu59GmiS

