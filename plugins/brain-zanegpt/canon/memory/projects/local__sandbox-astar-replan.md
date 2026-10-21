# local/sandbox-astar-replan — lessons

Project: local/sandbox-astar-replan. Newest first.

---

## E2 — sandbox14 replanner must not reject agents own cell
- Date: 2026-07-11
- Project: local/sandbox-astar-replan
- Tags: [algorithm][state][gamedev]
- What: A real-time A* replanner rejected planning entirely whenever the
  agent's OWN current cell was flagged blocked on the static occupancy
  grid: `if (blocked(start.x, start.y)) return { path: null, reason:
  'start-blocked' }`. When an obstacle-change schedule happened to mark the
  agent's current cell as blocked (a realistic case: another unit moves
  onto you, a hazard spawns under you, a door closes behind you), the
  replanner reported "no path" and the agent froze in place — even though
  a real route existed one step away and the agent's own presence there
  was never actually in question.
- Why built: Checking "is the start cell blocked" before running A* is a
  standard, reasonable guard for STATIC pathfinding (if you're asked to
  plan FROM an occupied cell, that's normally a caller error worth
  rejecting early) — the code carried that same guard forward unchanged
  into the dynamic-replanning version.
- Design: Built a symmetric-gap grid with a scheduled sequence of
  which-gap-is-open toggles, and had the agent replan from its live
  position on each schedule tick. Confirmed the exact trigger: a tick
  closed a gap cell at the same moment the agent's current position
  happened to be that cell.
- Got right: The static-start-blocked guard is completely correct for a
  ONE-SHOT planner that's told "plan a route starting from this cell" by
  an external caller who might genuinely hand it bad input — the bug is
  specific to reusing that same check in a REPLANNER that always plans
  from "wherever the agent physically already is right now."
- Where/why it failed: A replanner's start position isn't a caller-supplied
  hypothesis to validate — it's a fact (the agent is physically there,
  full stop). Checking it against the same static occupancy grid used to
  reject moves INTO cells conflates two different questions: "is this cell
  a legal place to move TO" (yes, occupancy-gated) and "is this cell where
  the agent already is" (not a question at all — it's ground truth,
  regardless of what the occupancy grid says). The static guard doesn't
  distinguish them because both look identical to a plain grid lookup.
- Fix: Remove the start-blocked rejection from the replanning path. Always
  treat the agent's current position as a valid g=0 planning root
  regardless of the grid's occupancy flag there; continue rejecting moves
  INTO blocked neighbor cells as before. Re-ran the exact scenario that
  triggered the bug after the fix: the agent now replans successfully
  (2 replans, reached: true) instead of freezing.
- Why this fix: It draws the boundary at the right place — occupancy data
  legitimately governs where you're allowed to GO, never whether you're
  allowed to already BE somewhere. A planner that re-derives its start from
  live agent state should never re-validate that start against the same
  data used to gate destinations.
- Rule of thumb: Any pathfinder/replanner invoked with "start from wherever
  the agent currently is" must treat that position as unconditional ground
  truth, never re-check it against the same occupancy/validity rules used
  for candidate moves — a static-pathfinder's "reject invalid start" guard
  is correct for a one-shot planner taking caller-supplied coordinates, but
  becomes a self-inflicted failure the moment the "start" is instead
  derived from where an agent already, factually, is. This specifically
  bites systems where obstacles can appear dynamically at/under an already-
  positioned agent (unit stacking, moving hazards, closing doors) — a
  failure mode a test suite that only ever starts agents from pre-verified-
  open cells will never exercise.
- Provenance (verified/assumed): Verified first-hand — reproduced the
  freeze live (console showed "no path!" and the agent halted at
  `(3,5)` with `reached: false` despite a route existing one step away);
  confirmed the fix resolves the exact scenario (2 replans, reached: true)
  without weakening the destination-occupancy checks, which continued to
  correctly reject/detect blocked-goal and no-path-exists cases in the
  same pass.
- Link: session (dog-game-continue-oc3xqh); sandbox-14-astar/astar.js,
  pass4.js (Part B, symmetric-gap oscillation test).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-movement-stack.md#E2 · compatible · no sandbox · session (query brain for "brain analyze groups and train on edges"), sandbox script sweep.mjs/sweep_fixed.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E2 · compatible · no sandbox · session (query brain for "train groups" -- merging the movement and RPG-progression emergent clusters via brain analyze seams), sandbox scripts engine.mjs/sweep2.mjs/sweep3.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E6 · compatible · no sandbox · session (query brain for "stress test mega group in a sandbox environment"), sandbox script stress.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-undo-replan.md#E1 · compatible · no sandbox · this session's sandbox build (sandbox_undo_replan.py); source entries sandbox-astar-replan#E2 and sandbox-undo-redo#E3.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-wfc-keylock.md#E3 · compatible · no sandbox · session (query brain for "brain train combinations, then train edges"), sandbox script sweep_astar.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-dog-pathfinding.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); sandbox `sandbox-dog-pathfinding/{astar,pass1_baseline,pass2_dynamic_replan, pass3_smoothing,pass4_performance,pass5_integration_shape}.mjs`; source entries local__sandbox-astar-replan (non-admissible heuristic, own-cell exemption, re-confirmed not re-derived from scratch).
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-architecture.md#E5 · compatible · sandboxes/2026-09-28__train-gap-b10.py · session 2026-09-28, brain train gap batch 10 loop 50
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-testing.md#E3 · compatible · sandboxes/2026-09-28__train-gap-b10.py · session 2026-09-28, brain train gap batch 10 loop 48
- Cited-by: 2026-07-13 · projects/local__sandbox-pathfinding-flowfield.md#E2 · compatible · no sandbox · session (query brain for "train untested seams, sandbox each test until satisfied"), sandbox script sweep.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-recursion.md#E19 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script seam.js, no code change to a shipping project
- Audited: 2026-10-13 · modeled · Read the entry; it has no stored sandbox script in sandboxes/, only a reference to astar.js and pass4.js in another session that I could not open. The mechanism is sound by inspection (a start-cell check against the occupancy grid rejects a replan when an obstacle appears under the agent), and the entry reports a live repro before and after the fix, so the result was not built in. But the Rule of thumb speaks about any pathfinder or replanner, while the evidence is one hand-written grid with one scheduled gap toggle, with no second planner or library tested and no script a reader can rerun. That is a hand-written model standing in for a general claim, so the fair verdict is modeled, not pass. · brain train auto audit session 2026-10-13; session_01HK1W7JLSbLXCV3BweWrzfF

## E1 — sandbox14 nonadmissible heuristic fails silently
- Date: 2026-07-11
- Project: local/sandbox-astar-replan
- Tags: [algorithm][testing]
- What: A*'s optimal-path guarantee depends entirely on the heuristic never
  overestimating true remaining distance (admissibility). Deliberately
  poisoning a single on-path cell's heuristic value (reporting 100 instead
  of the true 2) made the pathfinder route AROUND that cell and return a
  longer path (cost 6 vs. the true optimal 4) — with the exact same
  return shape (`{path, cost}`, no error, no warning) as a correct result.
- Why built: The poisoned-heuristic test was run specifically to check
  whether a non-admissible heuristic's effect is visible/detectable from
  the function's own output, as part of auditing tie-breaking and
  heuristic behavior.
- Design: First tried a uniform multiplicative weighting (1x-50x) on an
  admissible heuristic across a grid with only one real detour choice —
  this changed EXPANSION COUNT (33→18 nodes) but never changed the
  returned cost, because the grid didn't offer a genuine suboptimal-vs-
  optimal choice for the weighting to expose. Only a targeted, localized
  poisoned value on a single real on-path cell produced an actually-wrong
  (non-optimal) result.
- Got right: A* correctly used the heuristic as given, precisely as
  designed — the algorithm has no bug; it fully trusts its heuristic input,
  which is the correct contract. The "failure" is entirely a property of
  the input violating an assumption the algorithm depends on but cannot
  verify about itself.
- Where/why it failed: There is no cheap, general runtime check that can
  tell A* "this heuristic just lied to you" from inside the algorithm —
  admissibility is a property of the heuristic FUNCTION across its whole
  domain, not something derivable from any single query's result. A wrong-
  but-plausible path and a right path are structurally identical outputs
  (same shape, same types, both look like "a path was found"), so nothing
  short of independently knowing the true optimal cost would reveal the
  problem from the outside.
- Fix: No fix to the algorithm itself (there isn't one — trusting the
  heuristic is the correct design). The actionable fix is procedural: any
  heuristic that isn't a hand-verified-admissible textbook function
  (Manhattan/Euclidean/octile on a uniform-cost grid) — e.g. a precomputed
  distance table, a learned/approximate heuristic, or one adjusted for
  weighted terrain — needs correctness testing SEPARATE from and prior to
  trusting any path the pathfinder using it returns.
- Why this fix: Since the algorithm cannot self-detect a bad heuristic, the
  only place the guarantee can be restored is upstream, by validating the
  heuristic's admissibility directly (e.g. spot-checking `h(cell) <=
  true_remaining_cost` against known-correct distances) rather than
  inferring correctness from the pathfinder "seeming to work" on typical
  inputs.
- Rule of thumb: A*'s shortest-path guarantee is conditional on heuristic
  admissibility, and violating that condition fails SILENTLY, not loudly —
  a non-admissible heuristic doesn't crash the algorithm or produce an
  obviously-malformed result, it produces a normal-looking, wrong answer.
  Whenever a heuristic is anything other than a textbook-proven-admissible
  function on a uniform-cost domain (custom, learned, precomputed, or
  adjusted for weighted terrain), test the heuristic's admissibility
  directly and independently — never treat "the pathfinder ran without
  error and returned a plausible path" as evidence the path is actually
  optimal.
- Provenance (verified/assumed): Verified first-hand — confirmed true
  optimal cost is 4 with the correct Manhattan heuristic on the test grid;
  confirmed poisoning one on-path cell's heuristic value to 100 (vs. true
  distance 2) changed the returned path to cost 6, a real, measurable
  suboptimality, with the function reporting success either way.
- Link: session (dog-game-continue-oc3xqh); sandbox-14-astar/pass4.js
  (Part C2, poisoned-heuristic test).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-replan-gameloop.md#E1 · compatible · no sandbox · this session's sandbox build (sandbox_replan_gameloop.py); source entries sandbox-astar-replan#E1 and sandbox-combined-game-loop#E2.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-replan-save.md#E1 · compatible · no sandbox · this session's sandbox (sbR.py); source entries sandbox-astar-replan#E1, sandbox-combined-game-loop#E2, sandbox-savemigrate#E3.
- Cited-by: 2026-07-13 · projects/local__sandbox-dog-pathfinding.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); sandbox `sandbox-dog-pathfinding/{astar,pass1_baseline,pass2_dynamic_replan, pass3_smoothing,pass4_performance,pass5_integration_shape}.mjs`; source entries local__sandbox-astar-replan (non-admissible heuristic, own-cell exemption, re-confirmed not re-derived from scratch).
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E17 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 2), sandbox script dodge-oracle-sandbox.mjs (live import of real reducer/world, verbatim ported dodge-gate loop), test-coverage gap flagged, not applied
