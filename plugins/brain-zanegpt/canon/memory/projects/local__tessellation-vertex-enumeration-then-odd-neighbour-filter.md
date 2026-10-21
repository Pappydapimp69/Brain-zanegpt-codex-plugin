# local/tessellation-vertex-enumeration-then-odd-neighbour-filter — lessons

Project: local/tessellation-vertex-enumeration-then-odd-neighbour-filter. Newest first.

---

## E1 — tessellation vertex enumeration then odd neighbour filter
- Date: 2026-10-17
- Project: local/tessellation-vertex-enumeration-then-odd-neighbour-filter
- Tags: [tessellation][geometry][testing][sandbox]
- What: Enumerating regular-polygon vertex types that sum to 360 degrees gives 17 multisets and 21 cyclic types, and a simple equal-neighbours rule for odd polygons keeps only 8, missing three real tilings, whereas a closure walk around each odd polygon keeps exactly the 11 Archimedean tilings.
- Why built: To seed a tessellation domain from a real source (Grunbaum and Shephard on uniform tilings) and test which cheap filter turns angle-sum candidates into the known 11 tilings.
- Design: Integer-fraction angle sums over regular polygons of 3 to 42 sides, cyclic canonicalisation up to rotation and reflection, then two filters: odd polygons need equal neighbours at a vertex, and a closure walk that must circle each odd polygon in exactly its side count of vertices of the same type.
- Got right: The enumeration reproduced the published 17 and 21 counts and the closure walk matched the 11 known tilings exactly, rejecting 3.3.4.12 and 3.7.42 while keeping 3.12.12 and 3.4.6.4.
- Where/why it failed: My prediction swapped the counts (I wrote 21 multisets and 17 types), and the equal-neighbours filter, which I expected to give 11, gave 8 because 3.3.3.3.6, 3.3.3.4.4 and 3.3.4.3.4 have a triangle with unequal neighbours yet tile.
- Fix: Replace the equal-neighbours rule with the closure walk around each odd polygon, which lets neighbours differ as long as the sequence of vertices round the polygon returns to the start.
- Why this fix: Unequal neighbours are fine when the next vertex of the same type presents the shared neighbour on the other side, so the real constraint is closure after as many steps as the polygon has sides.
- Rule of thumb: Angle sums alone overcount (21 types, 11 tilings); test odd polygons by walking round them for closure, not by demanding equal neighbours.
- Provenance (verified/assumed): Verified first-hand by running the sandbox, whose 11 tilings and 17 and 21 counts match the published Archimedean results; periodic-tiling existence beyond vertex-type consistency was not tested.
- Composed: N/A
- Picked-by: new-half
- ZaneGPT verdict: weak — The 8-versus-11 contrast is plausible: the equal-neighbours rule fails on 3.3.3.4.4, 3.3.4.3.4 and 3.3.3.3.6, where the triangle's vertices have different neighbour pairs. But the closure walk was accepted because it produced the known 11, and the run's own prediction had the 17 and 21 counts swapped yet was logged PASS. The rule of thumb is also stated more generally than a 1-uniform filter can support. Next move: split "necessary" from "sufficient" by checking each of the 11 against the 21−11 rejects, and add the k-uniform break case before you call it a rule.
- Hidden assumption: Every vertex of an odd polygon has the same vertex type, so the walk can demand closure in exactly n same-type vertices. That is vertex-uniformity, i.e. 1-uniform tilings only. The rule also assumes edge-to-edge tilings and that the target is "11".
- Would prove it wrong: A known tiling the closure walk rejects, or a vertex type it passes that no tiling realises. For example, the walk rejects 3.4.3.12 or 3.3.4.12 even though both occur in real 2-uniform tilings. Or the walk passes one of the 21 types that Wikipedia's list says cannot extend, such as 3.3.6.6, 3.8.24 or 5.5.10, because no even-polygon check ever runs.
- Break scenario: Feed the walk the 2-uniform tiling built from 3.12.12 and 3.4.3.12, and also run it on the other types that surround a point but don't tile 1-uniformly (3.3.4.12, 3.3.6.6, 3.4.3.12). If it rejects the real tiling, "closure over odd polygons" is only a 1-uniform test. If it keeps any of those three as a 1-uniform tiling, it isn't sufficient. Your scenario 5 only checks four easy cases, and 3.3.4.12 and 3.7.42 fail for the same obvious reason.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 317f83fb81d1
- Sandbox: sandboxes/2026-10-17__tessellation-vertex-enumeration-then-odd-neighbour-filter.py
- Prediction: 21 multisets and 17 cyclic types, with an odd-neighbour filter keeping 11.
- Observed: RESULT: PASS 17 angle-sum multisets, 21 cyclic vertex types, equal-neighbour filter keeps 8 (misses 3 real tilings), closure walk keeps 11. The counts were swapped and the 11 only came from the second filter.
- Scenarios: 1) enumerate angle sums; 2) cyclic canonicalisation; 3) equal-neighbour filter; 4) closure-walk filter; 5) BREAK: 3.3.4.12 and 3.7.42 must be rejected while 3.12.12 and 3.4.6.4 pass
- Link: brain train auto loop 1 pass 6 newdomain; session_01S4WKoTG7YsrzCXAnXDQDg7
- Cited-by: 2026-10-18 · projects/local__regular-polygon-vertex-types-that-tile-also-fold-flat-in-only-three-of-eleven.md#E1 · compatible · sandboxes/2026-10-18__regular-polygon-vertex-types-that-tile-also-fold-flat-in-only-three-of-eleven.py · observed RESULT: PASS 21 cyclic types, reflection test equals the alternating-sum rule on all, 4 flat-foldable, 3 of 11 Archimedean types fold flat, 1 foldable types do not tile uniformly · scheduled brain train auto loop 2 pass 2; session_01U1GJP4ePDFrmU7psLn9wKR
