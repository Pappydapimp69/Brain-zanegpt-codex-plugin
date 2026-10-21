# local/kit-rotation-with-finite-grid — lessons

Project: local/kit-rotation-with-finite-grid. Newest first.

---

## E1 — finite trope grid adds only 0 02 similarity so three rotated kit assets still hold
- Date: 2026-10-15
- Project: local/kit-rotation-with-finite-grid
- Tags: [game-ads][comedy][ai-video][sandbox]
- What: Refuted: the finite 6-by-5 trope/axis grid does not make 3 rotated kit assets insufficient. In a 17-slot similarity model a 30-video batch with 3 of 10 kit assets rotated and trope and axis drawn from the grid scored 0.460 mean pair similarity, under the 0.5 line, versus 0.442 with fresh values; 4 rotated gave 0.410 and 6 gave 0.312.
- Why built: Train kernel pick: the kit lesson (rotate 3+ assets), the slot-machine cell-budget lesson (30 cells, tropes repeat by video 7) and the kit kernel were never run together; I expected the grid's forced repeats to push a 30-video batch back over 0.5 and demand more kit rotation.
- Design: Kit slots 10 (rotated ones drawn from a pool of 6), five fresh slots (name, joke, script, voiceover, layout), plus trope (6 values) and axis (5 values) taken from a seeded 30-cell rotation; mean pair similarity averaged over 20 seeds. Same equal-weight slots and 0.5 line as the kit lesson (both assumptions).
- Got right: Kit assets dominate the score: the grid adds only about 0.016 to 0.02 over fresh trope and axis values (0.442 to 0.458 at 8 videos), so the kit rotation advice stands unchanged.
- Where/why it failed: My prediction failed: I expected over 0.5 at 30 videos with 3 rotated assets and got 0.460. Only two of 17 slots are drawn from the grid and a repeated trope matches in 1 slot of 17 (axis repeats are rarer), so a finite grid cannot move the mean much. Equal slot weighting is the weak point: if a platform weights trope or joke engine more heavily, the grid would matter more; that was not tested.
- Fix: Keep the kit rule at 3 or more rotated assets and treat the cell grid as a separate, smaller budget (rotate cells without replacement) rather than adding kit rotation for it.
- Why this fix: Similarity is an average over slots, so sameness in two slots costs about two slots' worth; the 10 kit slots are what drive the batch score, and rotating them is cheaper than shrinking the grid's repeats.
- Rule of thumb: Under equal slot weights a finite trope/axis grid adds only about 0.02 pair similarity (30 videos, 3 rotated kit assets 0.460, fresh 0.442), so the kit rotation count, not the grid, sets whether a batch looks templated.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below (5 scenarios, 20 seeds each, deterministic). The slot weights, the 0.5 line and the idea that repeated tropes count as identical slots are assumptions; no platform data.
- Composed: ideas:COMEDY/fake-mobile-ad/reusable-fake-ad-grammar-kit, fake-ad-kernel-source-check/E1, slot-machine-cell-budget/E1
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__finite-trope-grid-adds-only-0-02-similarity-so-three-rotated-kit-assets-still-hold.py
- Prediction: Written before running; hidden assumption: repeated trope and axis values count as identical slots and are enough to matter. Expected 8-video grid batch near the fresh batch and the 30-video batch with 3 rotated above 0.5, 4 rotated below 0.5. Would be wrong if the 30-video batch stayed under 0.5 with 3 rotated; it did.
- Observed: RESULT: FAIL 30-video batch with 3 rotated kit assets 0.460 (>0.5), 4 rotated 0.410, 6 rotated 0.312; fresh-trope 8-video 0.442, grid 8-video 0.458 (the FAIL is the refuted expectation: 0.460 is under 0.5)
- Scenarios: 1) 8 videos with fresh trope and axis; 2) 8 videos with the finite grid; 3) BREAK: 30 videos, 3 rotated, grid; 4) 30 videos, 4 rotated; 5) 30 videos, 6 rotated
- Link: scheduled brain train auto loop 2 pass 1 (kernel); session_01DsRJQWba5msMYZQ3BqZXpp

