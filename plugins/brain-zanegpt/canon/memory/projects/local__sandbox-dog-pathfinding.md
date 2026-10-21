# local/sandbox-dog-pathfinding — lessons

Project: local/sandbox-dog-pathfinding. Newest first.

---

## E1 — pathfinding smoothing needs obstacle line of sight
- Date: 2026-07-13
- Project: local/sandbox-dog-pathfinding
- Tags: [algorithm][pathfinding][gamedev][testing]
- What: `brain query` on `pappydapimp69/dog`'s obstacle-avoidance gap (no
  NPC movement checks the game's own `obstacles` array — catcher, Rex, and
  wandering NPCs all walk straight through trees/hydrants/the doghouse)
  surfaced a real training target: build real A* pathfinding, verified
  against sandbox-14's already-recorded pitfalls (non-admissible heuristic
  fails silently; a replanner must not reject the agent's own cell) before
  applying it to the game. A 5-pass sandbox re-confirmed both prior
  pitfalls hold on Dog's real obstacle layout/radii, and surfaced one NEW
  finding neither prior pass covered: path SMOOTHING (string-pulling a
  zigzagging raw grid path into a few waypoints, needed so movement doesn't
  look robotic) is a separate hazard from pathfinding itself — a
  smoothing pass that checks "is this straight line walkable" against grid
  cells instead of against the real obstacle geometry can cut a corner
  directly through an obstacle the grid search correctly routed around.
- Why built: A* is only half of "move around obstacles convincingly" — the
  raw grid path is correct (never enters an obstacle) but zigzags between
  cell centers at every diagonal step, which reads as robotic/twitchy for
  a real character. Simplifying it to a few waypoints (string-pulling) is
  necessary, and it was built as its own pass specifically because nothing
  about A* itself guarantees the SIMPLIFIED path inherits A*'s own
  correctness.
- Design: `astar.mjs` (grid A*, octile heuristic, own-cell exemption,
  no-corner-cutting-through-diagonal-gaps) sized to Dog's real world
  (WORLD=80 half-extent, obstacle radii matching `world.js`'s actual
  trees r=1.4/hydrants r=0.8/doghouse r=3, `blocked()`'s own +0.6 padding).
  `pass3_smoothing.mjs` built two string-pull implementations against a
  layout specifically shaped so a shortcut WOULD cut a corner (a single
  large obstacle straddling the direct line between two path points): a
  "naive" version that only walks the existing path's own points, and an
  "obstacle-aware" version using true circle-vs-segment intersection
  against the actual obstacle list at each candidate shortcut.
- Got right: The underlying A* path itself was correct in every pass — 0
  obstacle violations across a full 600-tick simulated chase in the final
  integration check (`pass5_integration_shape.mjs`). The gap is entirely
  in what happens AFTER a correct path is found, not in the search itself.
- Where/why it failed: A raw A* path's own waypoints are all mutually
  reachable in the sense that consecutive grid cells are guaranteed
  adjacent-and-open — but a SIMPLIFIED path's job is to connect
  NON-consecutive waypoints with straight lines, and "these were both on
  a valid A* path" says nothing about whether the straight line BETWEEN
  them is clear, since the path bent around the obstacle specifically to
  avoid the direct line. The naive string-pull collapsed a 21-point path
  down to 2 points (start, goal) and the resulting line passed directly
  through the test obstacle (`clear: false`) — a full-scale reproduction
  of exactly the corner-cutting failure this pass set out to check for.
- Fix: String-pull with a real circle-vs-line-segment intersection test
  against the actual obstacle list (not the grid) at every candidate
  shortcut, extending the shortcut only as far as line-of-sight actually
  holds. Confirmed: 3 waypoints (vs. 21 raw, vs. 2 naive-and-wrong),
  routes around the obstacle (`clear: true`), and the full world-space
  integration check confirms 0 obstacle violations across 600 ticks when
  an agent steers toward the smoothed path's waypoints exactly as the real
  game's `stepXZ` would.
- Why this fix: A* and string-pulling solve different problems (least-cost
  discrete path vs. fewest-waypoints continuous path) and correctness
  doesn't transfer between them for free — the smoothing pass needs its
  own obstacle-awareness because it's allowed to ask questions (can two
  arbitrary path points see each other?) that A* itself never had to ask
  (A* only ever moves between grid-adjacent cells, so it can lean entirely
  on the grid; string-pulling explicitly does NOT move cell-by-cell, so
  leaning on the grid instead of real geometry is the exact gap that lets
  a corner get cut).
- Rule of thumb: When adding a path-simplification/string-pulling pass on
  top of a verified-correct grid search, treat it as its OWN hazard to
  test, not an automatic consequence of the search being correct — a
  smoothing pass's line-of-sight check must test against the real
  obstacle geometry (circle/polygon-vs-segment), never against grid-cell
  walkability alone, because the whole point of smoothing is to connect
  points the grid path deliberately did NOT connect directly.
- Provenance (verified/assumed): Verified first-hand — `astar.mjs`,
  `pass1_baseline.mjs` through `pass5_integration_shape.mjs` all run and
  confirmed deterministic (byte-identical output across two independent
  process invocations for every pass). Pass 2 re-confirmed sandbox-14's
  own-cell-exemption fix on Dog's real obstacle radii (with exemption:
  survives a continuously-adversarial dynamic obstacle and shows zero
  frozen ticks under the realistic transient case; without it: permanent
  freeze from the moment the hazard appears). Pass 3's corner-cut
  reproduction and fix confirmed directly via `pathClearOfObstacles`
  circle-vs-segment checks, not visual inspection. Pass 4 confirmed
  worst-case two-concurrent-agent A* cost (~4.4ms) is ~27% of one 16.6ms
  frame even fully unamortized, and negligible (~0.29ms/frame) at the
  planned ~0.35s replan cadence. Pass 5's `createPather` integration
  interface confirmed 0 obstacle violations over a 600-tick world-space
  chase simulation using only the steer-target output, matching exactly
  how the real game's `stepXZ` consumes a target position.
- Link: session (dog-game-continue-oc3xqh); sandbox
  `sandbox-dog-pathfinding/{astar,pass1_baseline,pass2_dynamic_replan,
  pass3_smoothing,pass4_performance,pass5_integration_shape}.mjs`; source
  entries local__sandbox-astar-replan (non-admissible heuristic, own-cell
  exemption, re-confirmed not re-derived from scratch).
- Composed: local__sandbox-astar-replan/E1, local__sandbox-astar-replan/E2
- Cited-by: 2026-07-18 · projects/local__sandbox-path-smoothing-validation.md#E1 · compatible · no sandbox · this session; `brain train group` dog+test seam; sandbox scratchpad `smoothing-validation/engine.mjs` (run twice, outputs diffed byte-identical)
- Cited-by: 2026-07-13 · projects/pappydapimp69__dog.md#E34 · compatible · no sandbox · session (dog-game-continue-oc3xqh); Pappydapimp69/Dog `pathfind.js` (`nearestOpenCell`, the cell-square-vs-circle `buildGrid` loop), `game.js` (`updateCatcher`); source entry local__sandbox-dog-pathfinding.
- Cited-by: 2026-10-09 · projects/local__sandbox-grid-validator-sampling.md#E1 · compatible · sandboxes/2026-10-09__grid-validator-shares-planners-sampling-blind-spot.py · observed RESULT: PASS centre-grid blind=95/400 G=0 false-green=120; aabb step<=cell C=0; aabb step3.0 C=19 step6.0 C=380 (G=0); goal-inside naive=400 fix=0; original predictions P1-P5=01101 (P1,P4 missed). Misses: blind count was 95, not 86 plus or… · brain train auto pass 2 (edge: sandbox-path-smoothing-validation + dog); sandbox 2026-10-09__grid-validator-shares-planners-sampling-blind-spot.py; session_01YFLLRpDsfZpRstb2KT2MQy
- Audited: 2026-10-14 · modeled · I read the entry in full, but the sandbox scripts it cites (astar.mjs and pass1 to pass5) are not stored in canon, so I could not confirm the code computes its results. The reasoning is internally sound: a smoothing pass that tests walkability on the grid can cut a corner the search deliberately routed around, and the entry reports a 21 to 2 waypoint collapse with `clear: false` against a layout built to trigger it. That layout was hand-built to provoke the failure, so the test shows the failure is possible, not how often it occurs. The claim concerns the Dog game's real obstacles and its `stepXZ` movement, and the 600-tick integration check used a hand-written model of that step rather than the game itself. The rule of thumb (test line of sight against real geometry, not grid cells) is general geometry and would likely survive a rebuild, but as stored this is a modeled result and not an audited pass. · brain train auto pass 3, session_01CwpncTDkwf6YoSaQyXUsNe
