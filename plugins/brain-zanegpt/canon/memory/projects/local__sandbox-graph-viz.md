# local/sandbox-graph-viz — lessons

Project: local/sandbox-graph-viz. Newest first.

---

## E4 — sandbox graph terminal iterate not the answer
- Date: 2026-07-11
- Project: local/sandbox-graph-viz
- Tags: [algorithm][determinism][testing]
- What: An iterative process's FINAL state is not automatically its result,
  and two distinct bugs come from trusting terminal iteration bookkeeping
  instead of the real objective. (1) A convergence detector keyed on
  per-step DISPLACEMENT false-positives two ways: a cooling schedule shrinks
  the step directly, so it declares "settled" while true energy is orders of
  magnitude above rest; and a numeric blow-up to NaN makes `NaN > max`
  false, so the running max stays 0 and the detector latches "settled" on a
  diverged garbage layout. (2) An iterative IMPROVER (a barycenter
  crossing-reduction sweep) is not monotone — it can oscillate period-2 or
  end on an ordering strictly worse than one it already visited — so
  returning the LAST iterate is wrong.
- Why built: To validate the convergence/quality loops in two visual-graph
  systems — a force-directed layout that iterates to equilibrium, and a
  hierarchical layout that sweeps to minimize edge crossings.
- Design: Force layout: iterate until "settled," measured per-step max
  velocity/displacement. Crossing reduction: sweep down/up applying the
  barycenter heuristic, return the resulting order. Both were probed across
  many seeds/graphs.
- Got right: The underlying physics and the barycenter heuristic themselves
  worked; the bugs were entirely in the STOP decision and the RESULT
  selection wrapped around them.
- Where/why it failed: Displacement/step-size is a proxy that shrinks for
  reasons unrelated to equilibrium (annealing shrinks it deliberately; NaN
  makes the max-tracker read 0), so a stop-condition built on it fires on
  non-equilibrium and even on divergence. And an iterative improver's last
  pass isn't its best: across 400 test graphs, 41 ended worse than their
  own best-seen ordering, and many oscillated between two orderings forever.
- Fix: (1) Gate convergence on the TRUE residual (remaining force/energy),
  with an explicit `Number.isFinite` guard so a NaN can never read as
  "small/settled." (2) Snapshot the best-by-objective state across all
  iterations and return THAT, never the last iterate; detect a period-2
  cycle to stop early.
- Why this fix: The question is "has the real objective reached its target"
  and "which iterate is actually best" — both must be answered against the
  measured objective, not against loop bookkeeping (step size, iteration
  count) that correlates with it only when nothing has gone wrong. The
  finite-guard closes the specific hole where NaN silently reads as
  converged.
- Rule of thumb: Do not trust the terminal state of an iterative
  solver/optimizer/physics loop. Gate the stopping condition on the true
  residual/objective, finite-guarded so a NaN can't masquerade as "small";
  and when the process isn't monotone, keep and return the best-by-objective
  iterate, not the last one (and detect a period-2 cycle to stop). A proxy
  like per-step displacement shrinks under annealing and under divergence
  alike, so it can report "done" in exactly the cases it shouldn't.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: a displacement-based detector reported "settled" at
  a NaN'd layout (max velocity read 0 after blow-up) and at an
  aggressively-cooled layout whose energy was ~10^25× the resting floor; a
  barycenter sweep left 41 of 400 graphs worse than their best-seen
  ordering and oscillated period-2 on 122 of 400. Residual-gating and
  keep-best fixes resolved both.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-graph-force
  (`engine.js` settle-detector) and sb-graph-routing (`graph.js` sweep).
  Kernel filed in ideas `idea-repository.md`
  (SYSTEM/algorithm/the-terminal-iterate-is-not-the-answer).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E2 · compatible · no sandbox · `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E8 · compatible · no sandbox · `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-08-10 · projects/pappydapimp69__august-10.md#E4 · compatible · no sandbox · August-10 gossip/community.py

## E3 — sandbox graph force layout nan and drift
- Date: 2026-07-11
- Project: local/sandbox-graph-viz
- Tags: [algorithm][graph][state]
- What: A textbook force-directed layout (all-pairs `k/d²` repulsion + Hooke
  spring edges + Euler integration) has three failure modes that each turn
  "converges to a readable diagram" into "NaN / flies apart / explodes," and
  each has a standard cheap fix. (1) Coincident nodes: two nodes at the same
  point give `d=0`, `repulsion/d² = Infinity`, and `Infinity × 0-unit-vector
  = NaN` that poisons every position in one step. (2) Disconnected
  components: with no edge between two components, nothing balances the
  repulsion pushing them apart, so the bounding box drifts unbounded forever
  and the layout never settles. (3) Integration stability is governed by
  timestep × the stiffest force gradient (the springs) and by damping — NOT
  by the loud repulsion parameter, which self-limits.
- Why built: To harden the auto-layout used to arrange a visual node graph,
  by simulating physics-based positioning and stressing its edge cases.
- Design: Seeded initial positions, all-pairs repulsion, spring attraction
  along edges, semi-implicit Euler with damping/cooling; measured energy,
  overlaps, bounding-box drift, and iterations-to-settle across coincident,
  disconnected, and high-timestep cases.
- Got right: The basic force model converged cleanly on a connected graph
  with distinct start positions; the three failures are specific edge cases
  a happy-path test never touches.
- Where/why it failed: (1) An inverse-power repulsion has a singularity at
  zero distance, and coincident nodes are inevitable in practice (duplicate
  imports, symmetric spawns, drag-to-same-point). (2) Repulsion between two
  disconnected components has no attractive counter-force, so the drift is
  structural, not numeric — more iterations never help. (3) Testers reach
  for the repulsion knob to explain instability, but repulsion self-limits
  (`k/d²` just spreads nodes; stable to 1e6 in the sim) while the timestep
  alone crossed oscillation→NaN at dt≈2→3, and raising damping toward 1
  destabilized at fixed dt.
- Fix: (1) Clamp with a soft-core minimum distance so `d` can't be 0. (2)
  Add a weak centering/gravity force (`−g·position`) so every component is
  bounded (real graphs are frequently disconnected). (3) Tune the timestep
  against the stiff spring gradient, and use velocity damping as the energy
  sink that buys a larger dt — don't chase the repulsion magnitude.
- Why this fix: Each fix addresses the actual mechanism — the singularity
  (soft-core floor), the missing counter-force (gravity), and the real
  stability limit (dt vs the stiffest gradient). These are exactly the
  measures production layout engines (d3-force, ForceAtlas, Graphviz neato)
  all carry, for the same reasons.
- Rule of thumb: When building a force-directed / physics layout: floor the
  distance in any inverse-power repulsion (coincident nodes → Inf×0 → NaN
  that poisons everything in one step); add a weak centering/gravity force
  so disconnected components can't drift unbounded (structural, not fixable
  by more iterations); and tune the timestep against the STIFFEST force
  gradient (springs), not the loud repulsion parameter, using damping to buy
  a larger dt. All three are edge cases a connected-graph happy-path test
  will never surface.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: minDist=0 produced all-NaN positions in one step;
  two disconnected triangles grew the bounding box 122→314 over 8000 iters
  and never settled, while a gravity term (g≥0.01) bounded and settled it;
  a springK sweep dropped the stable-timestep threshold from 4 to 1 as
  stiffness rose 0.02→2, while a repulsion sweep to 1e6 stayed stable.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-graph-force
  `engine.js` (repulsion `d²`, disconnected drift, dt/damping). Kernel filed
  in ideas `idea-repository.md`
  (SYSTEM/graph-layout/force-directed-production-hardening).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E1 · compatible · no sandbox · Sandbox: `sandbox-garden-camera-live-extents.js`; related artifact: `brain-garden-viz.html`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E4 · compatible · no sandbox · Sandbox: `sandbox-garden-group-rank-pull.js`; related artifact: `brain-garden-viz.html`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E5 · compatible · no sandbox · `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E6 · compatible · no sandbox · `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E7 · compatible · no sandbox · `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E4 · compatible · no sandbox · session (query brain for "train seams, combination, 3 environments, 5 loops, until satisfied" — loop 3/5), sandbox script loop3_graphviz.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-rankpull-forcelayout.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); sandbox `sandbox-rankpull-forcelayout/engine.mjs`, `engine2.mjs`; source entry local__sandbox-graph-viz#E3; the rank-pull mechanic itself verified first-hand today in a real constellation-visualization artifact (category-arm clustering + a label-overlap-avoidance fix), not yet filed as its own memory entry.
- Audited: 2026-10-13 · modeled · The entry has no stored sandbox, so I rebuilt a two-node version of its third claim (stability set by timestep against the stiff spring, not by repulsion) with inverse-square repulsion, a Hooke spring and semi-implicit Euler. It computes rather than assumes: repulsion from 1 to 1e6 stayed stable at dt 0.5, the timestep went stable at 1, oscillating at 2 and blowing up at 3, a spring constant of 2 turned dt 1 oscillating, and damping of 1.0 at dt 2 was far worse than 0.5. That matches the entry's dt 2 to 3 threshold and its spring-stiffness claim. But the Rule of thumb is about production layout engines and a multi-node graph with disconnected components and coincident nodes, and the evidence is a hand-written model; the NaN and drift claims were not re-run here, so the verdict is modeled, not pass. · scheduled brain train session, loop 2 pass 3 audit; session_01UeKMwUeVxtmySB3P82SSXJ

## E2 — sandbox graph delete cascade referential integrity
- Date: 2026-07-11
- Project: local/sandbox-graph-viz
- Tags: [state][graph]
- What: In a node-graph editor, deleting a node from the node collection
  WITHOUT removing its incident edges leaves dangling edges pointing at a
  now-missing node id. The next consumer that dereferences one — an
  evaluator reading `edge.to.inputs` — crashes on the missing node
  (`TypeError: cannot read properties of undefined`). Edges are references,
  and the delete broke referential integrity.
- Why built: A visual node-connection editor where nodes are connected by
  edges and the graph is evaluated; delete is a basic editing operation.
- Design: Nodes stored by id; edges stored as `{from, to}` id pairs; an
  evaluator walks edges to resolve each input's driver. Delete initially
  just removed the node from the id→node map.
- Got right: The evaluator and the connection model were correct for a
  consistent graph; the bug was solely that delete left the graph
  inconsistent (edges referencing a gone node).
- Where/why it failed: An edge is a REFERENCE to two nodes. Removing a node
  without removing the edges that reference it leaves the graph in a state
  no consumer expects — and because the crash happens later, at eval time,
  in a different code path, it reads like an evaluator bug rather than a
  delete bug.
- Fix: Make delete CASCADE to every incident edge atomically —
  `edges = edges.filter(e => e.from !== id && e.to !== id)` in the same
  operation that removes the node — restoring referential integrity. Keep a
  light eval-time missing-node guard only as defense-in-depth for
  corrupted/deserialized graphs, not as the primary mechanism.
- Why this fix: Referential integrity is an invariant of the graph, so it
  must be maintained by the mutation that could break it (delete), not
  patched at every read site. Cascading on delete keeps every consumer able
  to assume a consistent graph; pushing null-checks onto every reader is
  strictly worse (one missed check reintroduces the crash).
- Rule of thumb: In any graph / entity-with-relationships store, a delete
  must cascade to every incident edge/reference as part of the same
  operation — edges are references, and removing a referenced entity without
  cleaning its references leaves dangling pointers that crash a later,
  unrelated-looking consumer. Fix referential integrity at the mutation, not
  by defensive null-checks at every read (keep those only as
  defense-in-depth for externally-loaded/corrupted data).
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: deleting a mid-chain node left two dangling edges
  and the evaluator threw `TypeError: cannot read properties of undefined
  (reading 'inputs')`; making delete filter incident edges left zero
  phantoms and the downstream node fell back to its default input.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-graph-connect
  (`graph_v1.js` node-only delete, `graph_v2.js` `deleteNode` cascade).
  Kernel filed in ideas `idea-repository.md`
  (SYSTEM/graph/node-deletion-must-cascade-to-incident-edges).

## E1 — sandbox graph dag precondition before traversal
- Date: 2026-07-11
- Project: local/sandbox-graph-viz
- Tags: [algorithm][graph][state]
- What: Any traversal that assumes a DAG — recursive pull-evaluation of a
  node/dataflow graph, longest-path layer ranking for hierarchical drawing,
  dependency resolution — fails hard on a cycle: unbounded recursion /
  stack overflow, or a relaxation loop whose ranks ratchet upward forever
  and never terminate. Discovering the cycle when it blows up is too late;
  acyclicity must be established BEFORE the traversal.
- Why built: To find where visual node-graph systems break — building a
  node-connection editor (evaluates a dataflow graph) and a hierarchical
  layout (ranks nodes by dependency depth), both of which assume a DAG.
- Design: Two deterministic sandboxes — one evaluating a node graph by
  recursing from a sink into its inputs, one assigning layers by
  longest-path relaxation — deliberately fed cycles and self-loops.
- Got right: The DAG-case logic (topological evaluation, layer ranking) was
  correct; the failure was purely the absence of an acyclicity precondition
  in front of it.
- Where/why it failed: A recursive evaluator with no visited-set follows a
  back-edge forever (stack overflow on a clean 2-node cycle); longest-path
  relaxation on a cycle keeps finding a longer path each pass, so ranks grow
  every iteration and never converge (a cycle's layers grew +3 per
  iteration until a guard tripped). Self-loops are a distinct sub-case: an
  edge from a node to itself diverges the same way, and "reversing" it as a
  feedback arc is a no-op (the reversed edge is still the same self-loop).
- Fix: Establish acyclicity before traversing, with the remediation matched
  to who OWNS the graph. If the system authors it (an editor), reject the
  offending edge at connect-time: before adding `from→to`, DFS from `to`
  over outgoing edges and refuse if `from` is reachable (catches direct and
  multi-hop cycles). If the system only renders a given graph (a layout
  engine), accept it and DAG-ify by reversing a feedback-arc set for the
  algorithm, restoring direction when drawing. Self-loops must be FILTERED
  OUT and drawn as a decoration, never reversed.
- Why this fix: The traversal's precondition is "this is a DAG"; enforcing
  or establishing that up front is the only place the guarantee can be made.
  Connect-time rejection keeps an authored graph a DAG by construction;
  feedback-arc reversal makes a foreign graph temporarily acyclic without
  losing its real direction. Self-loops need filtering because reversal
  cannot change a self-edge.
- Rule of thumb: Before running any algorithm that assumes a DAG (recursive
  dependency eval, topological ranking, longest-path layout), enforce or
  establish acyclicity as a PRECONDITION — don't let the cycle surface as a
  stack overflow or a non-terminating loop. Reject the cycle-creating edge
  at author time if you own the graph, or reverse a feedback-arc set if you
  only render it; and treat self-loops as a separate filtered case, since
  reversing a self-edge is a no-op that still diverges.
- Provenance (verified/assumed): Verified first-hand this session and
  reproduced by an adversarial re-check: a single-driven 2-node cycle threw
  `RangeError: Maximum call stack size exceeded` in the recursive
  evaluator; longest-path ranking ratcheted a 3-cycle's layers +3/iteration
  until the guard fired, and a self-loop "reversal" left the edge unchanged
  and still diverging; connect-time DFS-reachability rejection and
  feedback-arc reversal both fixed their respective cases.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-graph-connect
  (`graph_v1.js` recursion, `graph_v2.js` `_wouldCycle`), sb-graph-routing
  (`graph.js` longest-path + `breakCycles`). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/graph/establish-acyclicity-before-a-dag-assuming-traversal).

