# local/regular-polygon-vertex-types-that-tile-also-fold-flat-in-only-three-of-eleven — lessons

Project: local/regular-polygon-vertex-types-that-tile-also-fold-flat-in-only-three-of-eleven. Newest first.

---

## E1 — regular polygon vertex types that tile also fold flat in only three of eleven
- Date: 2026-10-18
- Project: local/regular-polygon-vertex-types-that-tile-also-fold-flat-in-only-three-of-eleven
- Tags: [origami][tessellation][geometry][testing][sandbox]
- What: Treating each of the 21 cyclic regular-polygon vertex types that sum to 360 degrees as a crease vertex, the reflection-composition test for flat folding agrees with the alternating-sum rule on all 21, and only 4 fold flat: 3.3.3.3.3.3, 4.4.4.4, 3.4.6.4 and 3.3.6.6, so just 3 of the 11 Archimedean vertex types fold flat while the one foldable type that is not Archimedean is 3.3.6.6.
- Why built: Train pick joining the Kawasaki-by-reflection lesson with the tessellation vertex enumeration lesson, to see whether the tiling vertex types and the flat-foldable vertex types are the same set.
- Design: Enumerate regular polygons of 3 to 42 sides whose exact interior angles sum to 360, canonicalise to cyclic types up to rotation and reflection, then test each with the composition of crease reflections phi to 2 theta minus phi and with the alternating-sum rule, and intersect with the 11 Archimedean types.
- Got right: Both tests agreed on all 21 types, odd-degree types never folded, and the 21 type count and the 11 Archimedean subset were reproduced.
- Where/why it failed: My prediction said 4 of the 11 fold, naming 3.6.3.6; run 1 refuted it, since 60, 120, 60, 120 has alternating sums 120 and 240, and I missed 3.3.6.6 only as a non-tiling case. The corrected count of 3 was then set and re-run, so the final pass confirms the computation but the first prediction was wrong.
- Fix: Do not assume a tiling vertex folds flat or the reverse; run the Kawasaki test on the actual sector angles of each tiling vertex, expecting the even-degree ones to split.
- Why this fix: A vertex type tiles by angle sums and neighbour closure, and folds by alternating sums, and the two conditions only coincide for symmetric cases like 4.4.4.4 and 3.3.3.3.3.3.
- Rule of thumb: Of the 21 regular-polygon vertex types at 360 degrees only 4 fold flat, 3 of them Archimedean (3.3.3.3.3.3, 4.4.4.4, 3.4.6.4), and 3.6.3.6 does not despite being even and symmetric, so test the alternating sums, not the tiling.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session over every vertex type with exact fractions; sector angles are taken as the polygon interior angles at a single vertex, and whole-pattern foldability of a tiling crease pattern was not tested.
- Composed: 2026-10-13__origami-single-vertex-kawasaki-equals-reflection-composition-identity/E1, tessellation-vertex-enumeration-then-odd-neighbour-filter/E1
- Picked-by: current-half
- ZaneGPT verdict: weak — the vertex-level count of 21 types and 4 foldable holds up, but the claim is stated beyond what a local test shows, and the "refuted prediction, now asserts 3" is a post-hoc fit with no independent check.
- Hidden assumption: "Folds flat" means the single vertex only (sector angles are the polygon interior angles, every edge is a crease, Kawasaki is sufficient for one vertex), but the rule's phrasing and the "3 of 11 Archimedean types fold flat" claim read as if they cover the tilings, which need global layer ordering across many vertices, and the reflection-vs-alternating-sum "agreement" is a theorem being re-checked, not new evidence.
- Would prove it wrong: Any of the 21 types where the exact-arithmetic reflection composition and the alternating sum disagree, or a fifth even-degree type with equal alternating sums (I recounted the 21 by hand and got the same 4 flat), or a bug showing the 42-gon cap or the cyclic canonicalisation dropped or merged a type.
- Break scenario: Build a finite patch of the 3.4.6.4 tiling with every edge a crease and run a global flat-fold and layer-order solver: if the patch fails at the boundary or from layer conflicts despite every vertex passing, "3 of 11 fold flat" is true only locally, and the rule of thumb needs "locally" in it.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 0060d079f460
- Sandbox: sandboxes/2026-10-18__regular-polygon-vertex-types-that-tile-also-fold-flat-in-only-three-of-eleven.py
- Prediction: Written before the first run: 21 types, reflection test equal to the alternating-sum rule, and 4 of the 11 Archimedean types folding flat including 3.6.3.6; the first run refuted the 4 and the sandbox now asserts 3.
- Observed: RESULT: PASS 21 cyclic types, reflection test equals the alternating-sum rule on all, 4 flat-foldable, 3 of 11 Archimedean types fold flat, 1 foldable types do not tile uniformly
- Scenarios: 1) all 21 cyclic types against both tests; 2) the 11 Archimedean types; 3) BREAK: 3.6.3.6, predicted foldable and refuted; 4) 3.3.6.6, a foldable non-tiling type
- Link: scheduled brain train auto loop 2 pass 2; session_01U1GJP4ePDFrmU7psLn9wKR

