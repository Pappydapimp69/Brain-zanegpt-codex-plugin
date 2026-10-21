# local/sandbox-rankpull-forcelayout — lessons

Project: local/sandbox-rankpull-forcelayout. Newest first.

---

## E1 — rankpull gives drift protection not nan protection
- Date: 2026-07-13
- Project: local/sandbox-rankpull-forcelayout
- Tags: [algorithm][graph][state][testing]
- What: `brain analyze` surfaced sandbox-graph-viz#E3 (force-directed layout:
  coincident nodes give `d=0` → `Infinity × 0-unit-vector` → NaN that
  poisons every position in one step; disconnected components drift apart
  with nothing to balance the repulsion, since nothing anchors them) as a
  single-source edge worth re-verifying from a new angle. Composed:
  local__sandbox-graph-viz#E3 (force-directed layout's coincident-node NaN
  and disconnected-component drift failure modes) with a category
  rank-pull mechanic (a per-node force toward a fixed angular sector,
  verified first-hand today in a real constellation visualization, built
  to organize nodes into readable per-category "arms" rather than relying
  on emergent spacing). The interaction claim: does a rank-pull force —
  built for a completely different reason (semantic clustering) — also
  give graph-viz#E3's drift protection for free, and does it help with
  graph-viz#E3's OTHER failure mode (coincident-node NaN) too, or is that
  orthogonal?
- Why built: graph-viz#E3's own fix for disconnected-component drift is a
  generic weak centering/gravity force pulling every node toward a shared
  origin. A rank-pull force (pulling each node toward ITS OWN category's
  assigned angular sector, not a shared origin) looks superficially
  similar — both are "an extra force added to the simulation" — but
  nothing had confirmed whether rank-pull actually delivers the same
  structural guarantee, or merely happens to look stable in the one
  layout it was built for.
- Design: `engine.mjs` — a deterministic (zero RNG, zero wall-clock, fixed
  dt=0.02, fixed step count) force-directed simulation matching
  graph-viz#E3's exact shape (all-pairs `k/d²` repulsion, spring edges,
  damped Euler integration, no soft-core distance clamp). Two disconnected
  components (no edge between them), four scenarios: with/without
  rank-pull crossed with with/without a coincident-node pair seeded at
  `d=0`. A supplementary sandbox (`engine2.mjs`) reruns the drift case from
  two DIFFERENT starting configurations to test whether rank-pull's final
  layout is genuinely initial-condition-invariant (determined by the
  assigned sector) or just "looks less drifty" for one particular start.
- Got right: Without rank-pull, the two disconnected components settle at
  a separation entirely determined by their starting positions — bbox
  48.828 from one starting configuration, 35.591 from a different one (a
  ~37% difference for the identical rule set) — confirming graph-viz#E3's
  point that nothing anchors a disconnected component's position; wherever
  it drifts to is an accident of initial placement, not a designed
  outcome. With rank-pull, the same two starting configurations converge
  to 42.289 and 42.294 — within 0.01% of each other, i.e. effectively
  initial-condition-invariant, because each component is now pulled toward
  its OWN category's fixed sector rather than left to whatever the
  repulsion/spring balance happens to settle on.
- Where/why it failed: Rank-pull's protection is real but not complete.
  With the coincident-node pair (`d=0`) present, BOTH the no-rank-pull and
  the with-rank-pull runs hit NaN identically (`nanHit: true` in both) —
  rank-pull is a per-node force added on top of the same unguarded `k/d²`
  repulsion term, and does nothing to prevent the `Infinity × 0-unit-vector
  = NaN` computation graph-viz#E3 describes; it has no mechanism that
  touches the local, pairwise distance-zero case at all. The two failure
  modes are structurally independent: one is about what happens to an
  UNDER-constrained system with no anchor (rank-pull fixes this, same as
  generic centering, because both add a restoring force), the other is
  about a local division-by-zero in the repulsion term itself (rank-pull
  cannot touch this, because it never appears in that term).
- Fix: Rank-pull can safely REPLACE a generic centering/gravity force where
  both are being considered for disconnected-component drift (confirmed
  equivalent-or-better here, and additionally gives a semantically
  meaningful rather than arbitrary final layout) — but it must not be
  mistaken for a substitute for graph-viz#E3's OTHER fix, the soft-core
  minimum-distance clamp on the repulsion term. Both fixes are still
  independently required in any layout that has both hazards (which is
  most real layouts: disconnected subgraphs AND possible coincident seed
  positions).
- Why this fix: The two graph-viz#E3 failure modes live in different parts
  of the force calculation — the drift fix works by adding a force that
  wasn't there before (any restoring force toward a stable point works,
  generic or per-category); the NaN fix works by clamping a term that's
  already there (the repulsion's distance divisor) before it can reach
  zero. Adding a new force elsewhere in the sum can never retroactively
  guard a division that happens earlier in the same sum's other term.
- Rule of thumb: When a layout adds a NEW force for an unrelated purpose
  (semantic clustering, category grouping, narrative ordering) and it
  happens to also look like it fixes a known layout hazard (drift), verify
  which SPECIFIC failure mode(s) it actually addresses before crediting it
  with the whole class of "force-directed layout hardening" — a force that
  restores position (drift, missing-anchor problems) and a guard that
  clamps a divisor (coincident-point NaN problems) are different repairs
  for different terms in the simulation, and adding one is not evidence
  the other is now unnecessary. Verify by testing the specific hazard the
  new force was NOT designed for, not just the one it was.
- Provenance (verified/assumed): Verified first-hand — `engine.mjs` run
  twice as independent process invocations, output byte-identical
  (deterministic); confirmed rank-pull eliminates initial-condition-
  dependence in the drift case (48.828/35.591 without → 42.289/42.294
  with, via `engine2.mjs`, also reproducible across two independent runs);
  confirmed rank-pull does NOT prevent the coincident-node NaN case
  (`nanHit: true` identically with and without rank-pull present).
- Link: session (dog-game-continue-oc3xqh); sandbox
  `sandbox-rankpull-forcelayout/engine.mjs`, `engine2.mjs`; source entry
  local__sandbox-graph-viz#E3; the rank-pull mechanic itself verified
  first-hand today in a real constellation-visualization artifact
  (category-arm clustering + a label-overlap-avoidance fix), not yet filed
  as its own memory entry.
- Composed: local__sandbox-graph-viz/E3
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E206 · compatible · sandboxes/2026-10-13__rankpull-layout-inherits-toposort-tiebreak-instability.py · observed RESULT: FAIL rank-pull layout over 720 declaration orders: declared tie-break 2 layouts (max move 0.91), lexicographic 1, tie-free chain 1. Mechanism held, numeric thresholds missed. · scheduled brain train session, 2026-10-13; session_01KgwUVJ8YiFpBjfevwrK7fS
