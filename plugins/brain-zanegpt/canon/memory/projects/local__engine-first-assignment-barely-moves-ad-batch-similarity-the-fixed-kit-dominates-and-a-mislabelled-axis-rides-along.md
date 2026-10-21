# local/engine-first-assignment-barely-moves-ad-batch-similarity-the-fixed-kit-dominates-and-a-mislabelled-axis-rides-along — lessons

Project: local/engine-first-assignment-barely-moves-ad-batch-similarity-the-fixed-kit-dominates-and-a-mislabelled-axis-rides-along. Newest first.

---

## E1 — engine first assignment barely moves ad batch similarity the fixed kit dominates and a mislabelled axis rides along
- Date: 2026-10-19
- Project: local/engine-first-assignment-barely-moves-ad-batch-similarity-the-fixed-kit-dominates-and-a-mislabelled-axis-rides-along
- Tags: [ads][batching][simulation][method]
- What: A deterministic model of a 10-video fake-ad batch with 16 feature slots (10 reusable kit assets, one comic-engine slot, 5 fresh slots) comparing engine-first round-robin assignment with topic-first random engines, with and without rotating 3 kit assets.
- Why built: Engine-first assignment caps repeated engines in a batch, and a fixed ad kit keeps a batch above half identical even with new jokes; I wanted to know whether fixing the engine repeats helps the similarity the platform would flag. The source-check lesson says to fact-check labels, so the run also counted how often a batch carries the mislabelled axis cell.
- Design: Pair similarity is the share of identical slots, batch score is the mean over all 45 pairs of 10 videos. Engine-first gives engine i mod 8, topic-first draws engines from 8 with a fixed seed over 300 batches. Kit rotation draws 3 assets from a pool of 6 variants. The mislabelled-axis probability is 1 - C(24,10)/C(30,10) for 6 flagged cells of 30.
- Got right: With a fixed kit the score was 0.6278 engine-first against 0.6331 topic-first, matching the closed form (10 + P(same engine))/16, and rotating 3 kit assets cut it to 0.4569 and 0.4622, under the 0.5 flag line.
- Where/why it failed: The engine assignment method moved the batch similarity by only 0.0053, so the engine-first lesson does not help with similarity: the fixed kit sets the score. The 0.5 flag line is an assumption carried from the kit lesson, not a platform figure, and the mislabelled axis is still in a 10-cell batch with probability 0.935 whichever assignment is used.
- Fix: Spend the variety budget on rotating kit assets (3 or more per video) rather than on engine assignment, and strip or correct the mislabelled axis label from the cells before a batch is drawn.
- Why this fix: The engine is one slot of sixteen so equalising it can change the mean by at most about 1/16 of the same-engine rate, whereas each rotated kit asset removes a whole fixed slot from the score.
- Rule of thumb: In a 16-slot ad batch the engine-first versus topic-first choice changed the mean pair similarity by 0.0053 while rotating 3 kit assets changed it by 0.17, so fix the kit before the engine mix and correct a mislabelled axis label before drawing cells.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, PASS with deterministic output; the slot structure and the 0.5 flag line are modeling assumptions from the earlier kit lesson, and no real platform similarity score was measured.
- Composed: engine-first-idea-batches/E1, fake-ad-kit-template-similarity/E1, fake-ad-kernel-source-check/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the 0.17 vs 0.0053 gap is nearly a restatement of how many slots the model gave each factor, and the axis-label clause (0.935) is plain combinatorics that was never tested against the ad-similarity claim.
- Hidden assumption: Pair similarity is a valid proxy for how repetitive the batch looks to viewers, so every slot counts equally and the engine slot (1 of 16) is no more visible than a single kit asset. The 0.17 vs 0.0053 gap therefore comes from the slot arithmetic (3 rotated slots vs 1 engine slot), not from anything about ads. The rule also assumes the 6-variant pool and the 3-asset choice are representative.
- Would prove it wrong: A viewer or detector test where the engine (comic style) is weighted far above kit assets, so that engine-first batches read as less repetitive than topic-first ones regardless of slot count. Or the same model with the engine slot weighted 3x or more and a rotated-kit effect that falls below the engine effect.
- Break scenario: Rerun with engine variety as the only varied dimension (engine slot weighted by visibility, say 5 slots' worth) against rotating 1 kit asset, and with a pool of 2 variants instead of 6. If the ordering flips, or kit rotation gains less than 0.05, "fix the kit before the engine mix" is an artifact of the slot count and pool size. Also check that the 8-engine round-robin with 10 videos (engines 0 and 1 repeat) isn't the only reason engine-first and topic-first sit so close.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest 1e709c211303
- Sandbox: sandboxes/2026-10-19__engine-first-assignment-barely-moves-ad-batch-similarity-the-fixed-kit-dominates-and-a-mislabelled-axis-rides-along.py
- Prediction: Fixed kit: engine-first 0.6278, topic-first within 0.01 of it; rotating 3 kit assets lowers the score by more than 0.10 to at most 0.5; the mislabelled-axis cell appears in a 10-cell batch with probability 0.935.
- Observed: RESULT: PASS fixed kit: engine-first 0.6278 vs topic-first 0.6331 (diff 0.0053); +3 kit rotated 0.4569/0.4622; P(mislabelled-axis cell in 10-cell batch)=0.935
- Scenarios: 1) engine-first with fixed kit; 2) topic-first random engines with fixed kit; 3) BREAK: rotate 3 kit assets under both assignments; 4) mislabelled-axis cell probability in a 10-cell batch
- Link: scheduled brain train auto, loop 2 pass 2; session_01W1FCx5tpnHusaTASoCMosY
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E548 · compatible · sandboxes/2026-10-20__ad-batch-ceiling-similarity-and-mislabelled-axis.py · observed RESULT: PASS sizes [6, 12, 16, 16]; one lost axis keeps sizes {1: 6, 2: 12, 3: 16, 6: 16}; 2 axes gives {1: 6, 2: 12, 3: 12, 6: 12}; sim R3-R1=0.0073 vs kit rotation 0.188 · scheduled brain train run, 2026-10-20; session_01AxvhKMfKUmYVr8Ree8rqE7
