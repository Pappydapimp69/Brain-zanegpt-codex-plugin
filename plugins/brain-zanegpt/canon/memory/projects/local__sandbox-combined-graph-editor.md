# local/sandbox-combined-graph-editor — lessons

Project: local/sandbox-combined-graph-editor. Newest first.

---

## E2 — combined testing finds interaction seam bugs
- Date: 2026-07-11
- Project: local/sandbox-combined-graph-editor
- Tags: [testing][process][architecture]
- What: Composing several independently-verified rules/components into one
  system surfaces a class of bug that unit-verifying each in isolation
  structurally cannot find: interaction-seam bugs, where each rule is
  correct alone but their combination needs a "when stacked with X, also do
  Y" fix. Of 11 kernels each previously verified in its own sandbox, three
  needed such a fix once combined, and two of the failures shared a single
  root cause — none of it visible in the isolated tests that passed.
- Why built: A deliberate combined/integration ("stress-test") sandbox
  whose GOAL was to check whether canon knowledge that was each verified
  separately still holds together — not to discover new isolated bugs.
- Design: One node-graph editor implementing all 11 rules at once
  (undo/redo, DAG validation, generational handles, memoized eval), then a
  battery of scenarios that specifically exercised the BOUNDARIES between
  rules rather than any rule alone.
- Got right: Each rule's isolated sandbox and its isolated verification
  were correct — the combined failures were not regressions in any rule,
  they were genuinely new facts that only exist at the seams.
- Where/why it failed: Unit verification fixes each rule's inputs to its
  own scenario, so it never sees the enlarged scope another rule imposes:
  an undo pre-image tested on scalar edits never learns it must also capture
  a delete's CASCADE set; a memo tested within one eval run never learns an
  undo must invalidate it; a deep-copy tested on plain data never learns it
  dangles a generational handle; a connect-time cycle guard tested on live
  edits never learns undo can restore an edge that closes a cycle. The
  recurring seams were: an operation's scope GROWS (capture/undo more),
  caches must invalidate on MORE transitions, and identity/mutation must be
  SINGLE-SOURCED.
- Fix: Run an explicit combined/integration pass over components that will
  share a real system, and target the tests at the interaction boundaries
  (does A's captured state include what B cascades? does B's cache see A's
  transitions? do A's copies preserve B's identity handles?), not at
  re-testing each component. Record the resulting "when combined with X,
  also do Y" caveats onto the individual rules so the composed constraint
  isn't lost.
- Why this fix: Correctness of parts does not compose to correctness of the
  whole when the parts share mutable state, ordering, caches, or identity —
  the guarantees interact. Only a test that actually stacks them exercises
  the shared preconditions; and writing the caveat back onto each rule is
  what keeps the interaction knowledge attached where the next user will
  look.
- Rule of thumb: Independently-verified components are not a verified
  system — unit-verifying each in isolation cannot find interaction-seam
  bugs, because each test fixes away the enlarged scope the others impose.
  Before trusting a stack of separately-proven rules, run a combined pass
  aimed at the BOUNDARIES (scope-growth, cache-invalidation, single-source-
  of-identity are the recurring seams), and write any "when combined with X,
  do Y" caveat back onto each rule. "Each part passed its own test" is a
  weaker guarantee than "the composition was tested."
- Provenance (verified/assumed): Verified first-hand this session — a
  combined node-graph editor stacking 11 previously-isolation-verified
  kernels; 3 required composition fixes (cascade-capture, cache-
  invalidation, deep-copy-vs-handle reconciliation) and 2 failures shared
  one root cause (allocation bypassing the history stack), all reproduced
  and then independently re-verified, none of which appeared in the passing
  isolated sandboxes.
- Link: session (dog-game-continue-oc3xqh); combined sandbox
  combined-graph-editor; the four existing kernels that gained composition
  caveats + the new single-mutation-channel kernel in ideas
  `idea-repository.md`.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E6 · compatible · no sandbox · `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E114 · compatible · sandboxes/2026-10-11__parked-alternatives-single-log-reason-recheck.py · observed RESULT: PASS cost {'none': 32.0, 'fragmented': 24.0, 'log_blind': 16.0, 'log_first_reason': 12.0, 'log_all_reasons': 13.5}; blind-skip misses 8; first-reason recheck rewalks 2; recheck crossover at check cost 0.143. The last prediction (fu… · scheduled brain train session; session_01BWCnQ783SE9ph58n6xAc6f

## E1 — combined route all mutation through one stack
- Date: 2026-07-11
- Project: local/sandbox-combined-graph-editor
- Tags: [architecture][state][testing]
- What: In a system with undo/redo (or any authority that reconstructs
  state from a command log), EVERY structural mutation must flow through
  the single history/command stack — including the ones that don't look
  like edits, most commonly ENTITY/NODE ALLOCATION (add/remove), not just
  the obvious ops (connect, set, move). A partially command-sourced model —
  edges go through undo but `addNode` doesn't, or one subsystem mutates
  state directly — silently forfeits the invariants every rule built on the
  stack assumes, and is worse than no undo because it passes every test
  until an out-of-band mutation interleaves with a pending undo.
- Why built: A combined/integration sandbox — one node-graph editor
  stacking 11 rules ("kernels") each previously verified IN ISOLATION
  (undo/redo, DAG connection validation, generational handles, memoized
  eval) — to test whether independently-correct rules still hold when
  composed.
- Design: A pool of nodes referenced by generational handles, typed
  ports/edges with connect-time cycle rejection, a memoized pull-evaluator,
  and an undo/redo history of commands; `addNode`/`removeNode` initially
  bypassed the history stack while edge ops went through it.
- Got right: Each of the 11 rules was individually correct and stayed
  correct in the combined build; the failures were purely at their
  interaction seams, not in any single rule.
- Where/why it failed: Three invariants ALL depend on state being a pure
  function of the linear history stack, and each broke when a mutation
  bypassed it. (1) Acyclicity: the connect-time cycle guard stays valid
  under undo only if no restored edge can coexist with an out-of-band edge;
  an out-of-band `connect` before an undo of a delete restored a graph with
  a cycle and the DAG evaluator stack-overflowed. (2) Identity:
  generational handles survive undo only if slot allocation is sequenced by
  the stack — a node created out-of-band reused a freed slot, so undoing
  the earlier delete either clobbered the new occupant or rolled the slot's
  generation BACKWARD, resurrecting a dead handle (ABA). (3) Cache
  coherence: a memo cache outliving one eval run returned stale outputs
  after undo unless the history layer invalidated it. The two identity/
  acyclicity failures shared exactly one root cause: allocation bypassed
  the history stack.
- Fix: Pick ONE authority for structural change and make it TOTAL — route
  node allocation through the same history stack as edges (an `AddNodeCmd`),
  so slot reuse can't interleave out-of-order with a pending delete-undo.
  With allocation on the stack, linear-LIFO undo only ever revisits states
  the connect-time guard already approved (verified over 16k+20k fuzzed
  states, zero cycles), handles keep stable slot+generation, and the eval
  cache has a single set of transitions to invalidate on.
- Why this fix: Every guarantee (acyclic reconstruction, handle identity,
  cache invalidation) is a statement about "the state is exactly what the
  command log produces." A mutation channel that skips the log makes that
  statement false, and the guarantees that rest on it become conditionally
  wrong in a way no single-rule test can surface. Totalizing the authority
  restores the precondition all three rules share.
- Rule of thumb: In any redoable/authoritative state system, route ALL
  structural mutation through the ONE history/command stack — including
  entity allocation, not just the obvious edits. Partial command-sourcing
  is worse than none: it forfeits acyclicity, reference-identity, and
  cache-coherence guarantees (each of which assumes state is a pure
  function of the linear log) and does so silently, failing only when an
  out-of-band mutation interleaves with an undo. If a subsystem must mutate
  outside the stack, it forfeits every invariant the stack guarantees for
  the state it touches — so don't, or make that boundary explicit and
  re-validate on restore.
- Provenance (verified/assumed): Verified first-hand this session by
  building the combined editor and reproducing each break, then confirmed
  by an independent adversarial re-run: an out-of-band edge before an
  undo-of-delete produced `n0→n1→n2→n0` and the evaluator overflowed; a
  node reusing a freed slot before undo clobbered the new node and left its
  handle resolving to null; a generation rolled 2→1 on restore let a dead
  handle resolve to a different node; 16k+20k fuzzed strict-LIFO states with
  allocation on the stack found zero cycles and zero identity breaks.
- Link: session (dog-game-continue-oc3xqh); combined sandbox
  combined-graph-editor (`editor.js` pool/allocation, `history.js`).
  Companion kernel filed in ideas `idea-repository.md`
  (SYSTEM/architecture/route-ALL-structural-mutation-through-the-one-history-stack).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E4 · compatible · no sandbox · session (query brain for "brain analyze groups and train in sandbox, 3 sandbox environs"), sandbox scripts engine.mjs/sweep5_salvage.mjs/sweep5b_salvage_atomic.mjs, no code change to a shipping project
