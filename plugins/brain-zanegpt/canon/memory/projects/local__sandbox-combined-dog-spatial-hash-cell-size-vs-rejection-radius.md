# local/sandbox-combined-dog-spatial-hash-cell-size-vs-rejection-radius — lessons

Project: local/sandbox-combined-dog-spatial-hash-cell-size-vs-rejection-radius. Newest first.

---

## E1 — sandbox combined dog spatial hash cell size vs rejection radius
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-spatial-hash-cell-size-vs-rejection-radius
- Tags: [algorithm][gamedev][testing][performance]
- What: A deterministic sandbox (fixed point set, no RNG) applying dog#E19's radius-aware scatter rejection through a dog#E13-style uniform spatial hash, with the hash's cell size left at the old flat minDist, checked against brute force.
- Why built: dog#E13 requires a uniform spatial hash to scan the 3x3 cell block with cell size >= radius, or cross-boundary neighbours are silently dropped. dog#E19 requires rejecting on `minDist + otherPoint.radius` rather than a flat minDist once seeded points carry differing collision radii. Both are recorded as independent fixes; this tests whether adopting E19 invalidates E13's precondition.
- Design: Five points with radii from 0.5 to 3.0 and a flat MIN_DIST of 2.0. Overlaps are computed by brute force with the radius-aware threshold, then by the spatial hash twice — once with cells sized to MIN_DIST (the pre-E19 sizing) and once sized to MIN_DIST plus the largest radius.
- Got right: Comparing against brute force over the same radius-aware predicate, so any discrepancy is attributable purely to the hash's spatial coverage rather than to a difference in the overlap rule being tested.
- Where/why it failed: With cells sized to MIN_DIST the hash finds only (0,1) while brute force finds four overlaps — (1,4), (2,4) and (3,4) are silently missed. The radius-aware threshold can exceed the 3x3 block's reach whenever a neighbour's radius is larger than the cell, so E19's wider query is asking a question the grid's cell size no longer covers. Resizing cells to MIN_DIST + max radius (5.0) recovers all four with zero missed.
- Fix: Whenever a spatial query's effective radius is widened — which is exactly what dog#E19's `minDist + otherPoint.radius` does — re-derive the hash's cell size from the new maximum query radius in the same change, and keep a brute-force cross-check on a fixture containing at least one point whose radius exceeds the cell size.
- Why this fix: dog#E13's guarantee is conditional on cell size >= the query radius, and E19 raises that radius without touching the grid. The result is not a partial miss but a systematic one biased toward exactly the large-radius points E19 was introduced to protect, so the fix silently defeats itself in its own target case while the pairwise-overlap verification E19 prescribes passes if it runs through the same hash.
- Rule of thumb: dog#E19's radius-aware rejection widens the spatial query and therefore invalidates dog#E13's cell-size precondition — sandbox-confirmed a hash sized to the old flat minDist missed 3 of 4 real overlaps, all involving the large-radius points E19 exists to protect; resize cells to minDist + max radius in the same change.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b1/l3.py) and confirmed brute force finds [(0,1),(1,4),(2,4),(3,4)] while the minDist-sized hash finds only [(0,1)], and that resizing cells to 5.0 recovers all four with none missed. dog#E13 and dog#E19 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E13, pappydapimp69__dog/E19
- Link: session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E198 · compatible · sandboxes/2026-10-13__spatial-hash-fixes-missed-pairs-but-not-order-dependent-epsilon-dedupe.py · observed RESULT: PASS brute=4 small-cell=1 eps-cell=4 survivors 3 vs 2 by insertion order. · scheduled brain train session, loop 1 pass 2; session_01DiPNzPzfsHcE8oDezvZY3n
