# local/sandbox-combined-replan-gameloop — lessons

Project: local/sandbox-combined-replan-gameloop. Newest first.

---

## E1 — compose amortized replan with deterministic loop
- Date: 2026-07-13
- Project: local/sandbox-combined-replan-gameloop
- Tags: [algorithm][determinism][state]
- What: Composing a variable-cost A* replan (astar-replan/E1: the replan's cost is its node-expansion count, and it varies) with a deterministic fixed-timestep loop (game-loop/E2: the loop must produce the same tick COUNT everywhere) exposes a constraint neither states alone: when the replan is AMORTIZED across ticks, the per-tick budget must be measured in WORK UNITS (node expansions), never in wall-clock milliseconds. A wall-time budget completes a machine-dependent number of expansions per tick, so the replan finishes on a different TICK on a fast vs slow machine — silently breaking the loop's tick-count determinism.
- Why built: To turn two separately-verified lessons into the cross-system rule that governs running a pathfinder inside a deterministic loop, and to check the composition is real rather than a tag coincidence — the co-verification edge the graph lacked between these systems.
- Design: A deterministic sandbox (25×25 grid, a wall forcing a 313-expansion A*; no RNG and no real timing — "machine speed" is an explicit ms-per-expansion parameter). The same replan is amortized under two budgeting policies (wall-ms vs fixed work-units) across two machines (1ms vs 3ms per expansion); the completion TICK is compared.
- Got right: The composition reproduced exactly as reasoned. MS-budget finish tick: fast=11, slow=32 (machine-dependent — determinism broken). WORK-budget finish tick: fast=11, slow=11 (identical). The tick-count invariant of game-loop/E2 holds if and only if the amortization budget is in work units, not time.
- Where/why it failed: The natural "give the replanner N milliseconds per frame" amortization silently makes the agent's arrival tick machine-dependent — invisible on any single machine, but it diverges across machines and across replays, exactly where game-loop/E2 promised identical tick counts. Nothing errors; the two runs just desync.
- Fix: Budget amortized variable-cost work (pathfinding, flow fields, incremental rebuilds) inside a deterministic loop in INTEGER WORK UNITS per tick (expansions/iterations), never in wall-clock time. Verify by running the same replan under two different per-expansion costs and asserting an equal finish tick.
- Why this fix: Tick determinism is a property of WORK per tick, not TIME per tick; any wall-clock gate reintroduces machine speed into the deterministic state — precisely the entropy game-loop/E2's integer time source exists to exclude.
- Rule of thumb: When you amortize a variable-cost computation (A* replan, flow-field, incremental rebuild) across a deterministic fixed-timestep loop, meter the per-tick budget in WORK UNITS (node expansions/iterations), not milliseconds — a wall-clock budget makes the completion tick machine-dependent and silently breaks the loop's same-tick-count determinism. Verify with two different per-unit costs and assert an equal finish tick.
- Provenance (verified/assumed): Verified first-hand — reproduced in a deterministic sandbox this session (A* over a 25×25 grid, 313 expansions; ms-budget → finish tick 11 vs 32 across two machine speeds; work-budget → 11 vs 11). Built and observed, not only reasoned; the two source entries were each verified when first filed.
- Link: this session's sandbox build (sandbox_replan_gameloop.py); source entries sandbox-astar-replan#E1 and sandbox-combined-game-loop#E2.
- Composed: sandbox-astar-replan/E1, sandbox-combined-game-loop/E2

