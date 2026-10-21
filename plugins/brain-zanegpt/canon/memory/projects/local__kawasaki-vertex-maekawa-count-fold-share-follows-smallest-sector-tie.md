# local/kawasaki-vertex-maekawa-count-fold-share-follows-smallest-sector-tie — lessons

Project: local/kawasaki-vertex-maekawa-count-fold-share-follows-smallest-sector-tie. Newest first.

---

## E1 — kawasaki vertex maekawa count fold share follows smallest sector tie
- Date: 2026-10-18
- Project: local/kawasaki-vertex-maekawa-count-fold-share-follows-smallest-sector-tie
- Tags: [origami][geometry][sandbox][testing]
- What: On every Kawasaki-valid degree-4 vertex on a 15 degree grid, the share of count-satisfying mountain and valley assignments that fold flat is fixed by ties at the smallest sector: 8 of 8 when all sectors are equal, 6 of 8 when the smallest sector is tied, 4 of 8 when it is unique; degree 6 ranges from 8 to 30 of 30.
- Why built: Train pick joining the Kawasaki angle rule (closure equals the reflection identity) with the Maekawa lesson that the count is necessary but not sufficient, to turn the three hand-picked fold shares in the second into a rule over the whole grid.
- Design: Enumerate every ordered sector composition of 360 into 4 and 6 parts in multiples of 15 degrees; Kawasaki by the alternating sums; fold decided by an independent crimp reduction that removes a local-minimum sector whose two creases differ and merges its neighbours, searched exhaustively over ties; all 2^n assignments per vertex.
- Got right: Fold shares were exactly 8/8, 6/8 and 4/8 for equal, tied-minimum and unique-minimum degree-4 vertices, no non-Kawasaki vertex folded under any assignment, every Kawasaki vertex folded under some assignment, and no folding assignment broke the count.
- Where/why it failed: Nothing in the prediction failed, but the degree-6 shares (8, 12, 16, 18, 20, 24 and 30 of 30) were only observed, not predicted, and the crimp reduction is a single-vertex model with no paper thickness or whole-pattern interaction.
- Fix: For a vertex that passes the Kawasaki test, count the folding assignments with a crimp or smallest-sector search instead of assuming the count-satisfying ones fold; for degree 4 expect 4, 6 or 8 of 8 by the smallest-sector tie.
- Why this fix: The count and the angle rule remove the impossible assignments; what remains fails only at the smallest-sector crease pair, so tie structure decides the share and the search is cheap.
- Rule of thumb: A Kawasaki-valid degree-4 vertex folds in 4, 6 or 8 of its 8 count-satisfying assignments according to a unique, tied or fully equal smallest sector, so Maekawa plus Kawasaki still needs a smallest-sector or crimp check.
- Provenance (verified/assumed): Verified first-hand by running the sandbox over every degree-4 and degree-6 pattern on the 15 degree grid with an independent crimp checker; whole crease patterns and degrees above 6 were not run.
- Composed: 2026-10-13__origami-single-vertex-kawasaki-equals-reflection-composition-identity/E1, origami-vertex-maekawa-count-is-necessary-not-sufficient-to-fold-flat/E1
- Picked-by: current-half
- ZaneGPT verdict: holds — I hand-derived the degree-4 counts and they match (odd crease on the unique minimum's boundary gives 2 of 4 positions, so 4/8; tied adjacent minima give 3 of 4, so 6/8; equal sectors give 8/8), but the rule is the known Kawasaki–Justin crimp condition and the PASS is confirmatory, not independent evidence.
- Hidden assumption: The crimp reduction is a faithful oracle for "folds flat". Both it and the prediction come from the same Kawasaki–Justin theory, so a shared misconception, or a bug in how ties or merged-sector creases are handled, would pass unnoticed. It also assumes single-vertex flat-foldability is the real question, and that a 15° grid with every rotation and reflection counted separately is representative of arbitrary angles.
- Would prove it wrong: A brute-force layer-ordering check that doesn't use the crimp rule (enumerate stackings of the four sectors, test for self-intersection) finding a fold on a degree-4 count-satisfying assignment the crimp rule rejected, or rejecting one it accepted. For example, a unique-smallest vertex with the odd crease not adjacent to the smallest sector that does fold, or a tied-smallest vertex with fewer or more than 6 of 8 folding.
- Break scenario: Run that independent stacking-order check on the off-grid, near-degenerate degree-4 vertices (1°, 1°, 179°, 179° and 30°, 30°, 150°, 150°), plus the unique-minimum case 30°, 60°, 150°, 120°. For the 30°, 30°, 150°, 150° vertex, take the odd crease at the boundary between the two tied minima, and then at the crease between the two large sectors. The first should fold and the second should not.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest af1ff3fee820
- Sandbox: sandboxes/2026-10-18__kawasaki-vertex-maekawa-count-fold-share-follows-smallest-sector-tie.py
- Prediction: Written into the script header before the first run: degree-4 fold share of count-satisfying assignments is 8/8 for equal sectors, 6/8 for a tied smallest sector and 4/8 for a unique one, with zero folds on non-Kawasaki vertices.
- Observed: RESULT: PASS deg4 shares equal 8/8, tied-min 6/8, unique-min 4/8; deg6 shares 8,12,16,18,20,24,30 of 30; non-Kawasaki folds 0; count-breaking folds 0
- Scenarios: 1) degree-4 equal sectors; 2) degree-4 tied smallest sector; 3) degree-4 unique smallest sector; 4) BREAK: all non-Kawasaki degree-4 and 6 patterns, built to show some assignment folding without closure; 5) degree 6 full grid
- Link: scheduled brain train auto loop 1 pass 2; session_01U1GJP4ePDFrmU7psLn9wKR

