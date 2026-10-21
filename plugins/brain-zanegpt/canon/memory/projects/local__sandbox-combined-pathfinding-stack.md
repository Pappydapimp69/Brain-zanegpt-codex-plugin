# local/sandbox-combined-pathfinding-stack — lessons

Project: local/sandbox-combined-pathfinding-stack. Newest first.

---

## E1 — pathfinding stack needs end to end not pairwise
- Date: 2026-07-13
- Project: local/sandbox-combined-pathfinding-stack
- Tags: [algorithm][gamedev][testing]
- What: The pathfinding subsystems (distance metric, diagonal/octile cost, A* heuristic, pathmetrics) are each verified PAIRWISE, but a fresh end-to-end integration check on one map — a SECOND, independent angle on the same edges — confirms the whole stack is mutually consistent: the octile distance field equals A*'s g-cost at every reached cell, the octile heuristic is admissible against the true field, and true travel diverges from Manhattan. Pairwise agreement does not by itself prove the triple agrees; the integrated run does.
- Why built: To raise independence on the single-source pathfinding edges by re-verifying them together from an integration angle, and to record that integration coverage is a distinct check from pairwise coverage.
- Design: Deterministic 9×9 grid with two offset walls; run octile 8-connected Dijkstra (distance field), diagonal A* with an octile heuristic (corner-cut forbidden), and compare field vs A* g-cost, heuristic vs true remaining cost, and octile vs Manhattan.
- Got right: All three checks passed simultaneously: field == A* cost (agree), octile heuristic admissible everywhere, octile travel 25.66 vs Manhattan 16 (diverges). The stack is consistent as an integrated whole, independently of the pairwise entries.
- Where/why it failed: N/A here — the integration held; the value is the independent corroboration plus the meta-lesson that a stack of individually-correct pathfinding parts can still disagree in combination (a heuristic admissible for 4-connected movement is inadmissible once diagonals are added), which only an end-to-end check catches.
- Fix: For a composed pathfinding stack, add an end-to-end invariant test on a real map — distance field == search g-cost, heuristic admissible against the field, metric matches the move model — rather than trusting N pairwise tests to imply the whole.
- Why this fix: Pairwise tests fix each seam in isolation; a shared object (one grid with one move model) can violate a cross-cutting invariant that no single pair observes, so the whole must be asserted together.
- Rule of thumb: A pathfinding stack whose parts (distance metric, diagonal cost, heuristic) are each verified pairwise still needs an END-TO-END check on one map — assert the distance field, A* g-cost, and heuristic admissibility all agree at once; pairwise agreement doesn't guarantee the triple is mutually consistent.
- Provenance (verified/assumed): Verified first-hand — deterministic integration sandbox this session (field==A* cost agree; octile heuristic admissible; travel 25.66 vs Manhattan 16). Built and observed.
- Link: this session's sandbox (sbP.py); source entries sandbox-distance#E1, sandbox-pathfinding-diagonal#E1, sandbox-pathfinding-astar-heuristic#E1, sandbox-combined-pathmetrics#E2.
- Composed: sandbox-distance/E1, sandbox-pathfinding-diagonal/E1, sandbox-pathfinding-astar-heuristic/E1, sandbox-combined-pathmetrics/E2

