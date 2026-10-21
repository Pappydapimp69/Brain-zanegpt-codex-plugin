# local/sandbox-combined-undo-replan — lessons

Project: local/sandbox-combined-undo-replan. Newest first.

---

## E1 — compose undo with a state reading replanner
- Date: 2026-07-13
- Project: local/sandbox-combined-undo-replan
- Tags: [algorithm][state][process]
- What: Composing an UNDO/REDO history with a REPLANNER that recomputes from live world state (an A* that re-reads the agent's current cell + the occupancy set every call) yields a constraint neither source lesson states alone: the undo snapshot must restore the ENTIRE state the replanner reads, not just the visible position. astar-replan/E2 establishes the replanner trusts its own current cell UNCONDITIONALLY; undo-redo/E3 establishes every history entry must be a deep, fully-independent snapshot. Together, a partial undo that restores position but not the occupancy set leaves the replanner confidently planning against a stale world — no error, just a silently wrong (or absent) path.
- Why built: To turn two separately-verified lessons into the cross-system rule that governs building both together, and to check whether the composition is real rather than a tag coincidence — the co-verification edge the graph lacked between these systems.
- Design: A deterministic sandbox (7×7 grid, a wall down column x=3 with a single gap at (3,0), no RNG): A* replans from the agent's CURRENT cell against the CURRENT occupancy set; an undo either deep-snapshots {pos, occ} (full) or {pos} only (partial). Sequence: snapshot → step forward and close the gap (occ grows) → undo → replan, comparing against the pre-action baseline.
- Got right: The two lessons compose exactly as reasoned, confirmed by running it: FULL undo restores {pos, occ} and the replan reproduces the correct 7-cell baseline path; the PARTIAL undo restores pos=(0,0) but leaves the gap closed, so the replanner — trusting its restored position but reading stale occupancy — returns NO PATH, throwing nothing. The bug is invisible to the replanner precisely because E2 removed its right to distrust current state.
- Where/why it failed: The predicted failure reproduced first-hand: an undo that snapshots the obvious visible state (position) but omits a field the replanner reads (occupancy / path cache) makes the replanner plan against a world that no longer matches, and because E2 makes it trust unconditionally there is no validation step to catch the mismatch.
- Fix: Before adding undo to any component that recomputes from live state, enumerate EVERY field that recompute reads and prove the undo snapshot captures all of them (deep-copied, per E3). Treat a "trusts current state unconditionally" replanner as an amplifier: any gap in the undo snapshot becomes a silent correctness bug, not a visible glitch. Verify by round-tripping an undo and re-running the recompute, not by checking the snapshot's shape.
- Why this fix: You cannot rely on the replanner to notice a stale world (E2 removed that check by design), so the only place to enforce consistency is the undo snapshot's completeness (E3) — as the sandbox shows, a position-only undo passes a shape check yet produces a wrong result.
- Rule of thumb: When you make a state-recomputing system (pathfinder/replanner, layout solver, physics resolver) undoable, the undo snapshot must cover the FULL closure of state that recompute reads — position AND occupancy AND caches AND rng cursor — because a component that trusts current state unconditionally converts any missing snapshot field into a silent wrong result; verify by undo-then-recompute, not by snapshot shape.
- Provenance (verified/assumed): Verified first-hand — reproduced in a deterministic sandbox this session (A* replanner + undo over a 7×7 single-gap grid): full undo replans the correct baseline path; a partial (position-only) undo makes the replanner return no path with no error. The composition was built and observed, not only reasoned; the two source entries were each verified when first filed.
- Link: this session's sandbox build (sandbox_undo_replan.py); source entries sandbox-astar-replan#E2 and sandbox-undo-redo#E3.
- Composed: sandbox-astar-replan/E2, sandbox-undo-redo/E3

