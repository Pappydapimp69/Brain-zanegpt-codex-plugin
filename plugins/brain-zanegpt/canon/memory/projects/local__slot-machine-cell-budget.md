# local/slot-machine-cell-budget — lessons

Project: local/slot-machine-cell-budget. Newest first.

---

## E1 — the slot machine has only 30 cells and 6 tropes so a batch repeats a trope by video seven
- Date: 2026-10-15
- Project: local/slot-machine-cell-budget
- Tags: [game-ads][comedy][ai-video][sandbox]
- What: The fake-ad premise slot machine has only 30 trope-by-axis cells (6 tropes, 5 study axes), so 10 randomly drawn videos repeat a cell with exact probability 0.815 (simulated 0.818); rotating through unique cells avoids cell repeats to video 30 but still repeats a trope within 7 videos (first at video 4 in the seeded order), and 6 of the 30 cells carry a mislabelled axis.
- Why built: Train gap pick: the slot-machine kernel generates premises, the policy kernel says every video needs its own joke, and the source-check lesson found one axis label is not the study's. Nobody had counted how far the generator's finite grid can go under the own-joke rule.
- Design: Cells = 6 tropes from the kernel times its 5 axes. Exact birthday probabilities, a seeded Monte Carlo of 20,000 ten-video batches as a cross-check, a seeded rotation through all 30 cells, and a label check of the kernel axis names against the study taxonomy as quoted in the source-check lesson (popular externalization, not borrowed fame).
- Got right: Exact and simulated cell-collision rates agree (0.815 vs 0.818), so the grid is small enough that unplanned drawing breaks the own-joke rule within about ten videos; the source-check finding costs 6 of 30 cells their traceability.
- Where/why it failed: My prediction was wrong on the size: I expected a ten-video collision chance of 0.6 to 0.8 and the exact value is 0.815, so the grid is tighter than I guessed. Also the own-joke rule cannot be met by cell-uniqueness alone: pigeonhole forces a repeated trope by video 7. Whether a repeated trope with a new axis reads as templated to a platform is not tested; cells are treated as equal and the one-swap absurd slot is ignored, so the real space is larger.
- Fix: Draw premises by rotation through the grid, never at random, treat the trope as the repeat unit and add a third slot (the one absurd swap, or a format) to widen the space; quote the axis names from the study verbatim before reuse (popular externalization).
- Why this fix: Without replacement removes cell repeats entirely, the trope count (6) sets the cadence for repeats, so only a larger third slot or a trope rest period reduces trope-level sameness; verbatim labels keep every cell traceable.
- Rule of thumb: The slot machine's 30 cells run out fast: 10 random videos repeat a cell 82% of the time and any 7 videos repeat a trope, so rotate without replacement and add a third axis before relying on it for a batch.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below (exact probabilities, a simulation and a seeded rotation); the kernel's trope and axis lists were read from the kernel, and the study label from the source-check lesson, not re-fetched. Whether platforms treat repeated tropes as templated is assumed, not tested.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns, fake-ad-kernel-source-check/E1, ideas:AI-VIDEO/monetization-policy/every-video-gets-its-own-joke-and-script
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__the-slot-machine-has-only-30-cells-and-6-tropes-so-a-batch-repeats-a-trope-by-video-seven.py
- Prediction: Written before running; hidden assumption: the grid is large enough for the own-joke rule over a normal batch. Expected a ten-video cell-collision chance of 0.6 to 0.8, a rotation with no cell repeats, and a trope repeat by video 7; would be wrong if the collision chance were under 0.5. The collision band was missed (exact 0.815).
- Observed: RESULT: FAIL 10 random videos repeat a cell 0.82 (sim 0.82); rotation avoids cell repeats to 30 but repeats a trope by video 4; kernel labels traceable 80% (6/30 cells). The FAIL is only my 0.6-0.8 band; the other expectations held.
- Scenarios: 1) random draw of 10 videos, exact plus 20,000 simulated batches; 2) rotation without replacement across all 30 cells; 3) BREAK: rotation checked for trope repeats, which cell-uniqueness does not prevent; 4) label trace of the 5 kernel axis names against the study names
- Link: scheduled brain train auto loop 1 pass 5 (gap); session_01DsRJQWba5msMYZQ3BqZXpp
- Cited-by: 2026-10-15 · projects/local__kit-rotation-with-finite-grid.md#E1 · incompatible · sandboxes/2026-10-15__finite-trope-grid-adds-only-0-02-similarity-so-three-rotated-kit-assets-still-hold.py · observed RESULT: FAIL 30-video batch with 3 rotated kit assets 0.460 (>0.5), 4 rotated 0.410, 6 rotated 0.312; fresh-trope 8-video 0.442, grid 8-video 0.458 (the FAIL is the refuted expectation: 0.460 is under 0.5) · scheduled brain train auto loop 2 pass 1 (kernel); session_01DsRJQWba5msMYZQ3BqZXpp
