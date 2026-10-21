# local/sandbox-toposort — lessons

Project: local/sandbox-toposort. Newest first.

---

## E2 — report the actual cycle not the leftover
- Date: 2026-07-01
- Project: local/sandbox-toposort
- Tags: [process][harness]
- What: Detecting and reporting a dependency cycle in a task/topological ordering.
- Why built: A scheduler must fail with a useful "these depend on each other" message when the graph isn't a DAG.
- Design: Kahn's algorithm (in-degree removal) already detects a cycle for free: whatever nodes it can't place are "unschedulable", so the first instinct is to report that leftover set as the cycle.
- Got right: Kahn correctly detects THAT a cycle exists.
- Where/why it failed: The leftover set OVER-REPORTS the cycle — it contains every node stuck in the cycle AND every node merely downstream of it (that can never reach in-degree 0). Reporting it as "the cycle" is misleading: e.g. for a→b→c→a plus a→d, the leftover is {a,b,c,d}, but d is not in the cycle at all. A user chasing the "cycle" wastes time on innocent nodes.
- Fix: To report the ACTUAL cycle, run a DFS with three-color marking (white/gray/black); a back-edge to a GRAY node (one still on the current recursion stack) is the cycle, and you extract the exact path by slicing the stack from that node. Use Kahn for fast *detection*; use DFS when you need to *name the cycle* in an error.
- Why this fix: In-degree removal loses the path structure, so it can say "unschedulable" but not "which loop". DFS keeps the active path on the stack, so the back-edge gives the minimal cycle directly — the thing a human actually needs to fix it.
- Rule of thumb: Kahn's "unschedulable leftover" detects a cycle but over-reports it (includes downstream-of-cycle nodes) — for an actionable error message, extract the real cycle with a DFS that flags a back-edge to a gray (on-stack) node and slices the path off the recursion stack.
- Provenance (verified/assumed): VERIFIED first-hand — built both this session; Kahn's leftover included a downstream node, DFS returned the exact cycle (a→b→c→a, excluding d) and a self-loop.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E1 · compatible · no sandbox · session (query brain for "brain train combinations in sandbox"), sandbox scripts sweep.mjs/sweep3.mjs/sweep5.mjs, no code change to a shipping project

## E1 — comparative test needs adversarial baseline input
- Date: 2026-07-01
- Project: local/sandbox-toposort
- Tags: [harness][process]
- What: A comparative test meant to show that critical-path-priority scheduling beats naive scheduling (shorter makespan) under bounded workers.
- Why built: To prove the priority heuristic actually helps, not just theorize it.
- Design: Built a graph (a dependency chain + independent tasks) and compared makespan of "arbitrary order" vs "critical-path priority" with 2 workers.
- Got right: The heuristic and simulator were correct.
- Where/why it failed: The first run showed a TIE (both = 3, "optimal"), suggesting the heuristic didn't matter. It did — but the node list happened to place the critical-chain tasks FIRST, so the "arbitrary" (stable, insertion-order) baseline accidentally picked the good tasks too. The test wasn't adversarial to the baseline, so it couldn't reveal the difference.
- Fix: Order the inputs so the NAIVE baseline actually misbehaves — put the independent tasks first, so arbitrary order wastes workers on them and delays the chain. Then the gap appeared (arbitrary 4, critical-path 3).
- Why this fix: A comparison only demonstrates "A beats B" if the inputs are a case where B genuinely fails. If the test data lets the baseline succeed by luck (input ordering, easy case), you get a false tie and wrongly conclude the improvement is pointless. Construct the baseline's worst case.
- Rule of thumb: A comparative test (heuristic beats baseline) must use inputs adversarial to the BASELINE — where the naive approach actually fails — or a lucky input ordering yields a false tie and hides a real improvement. (Sibling of "benchmark data must exercise the cost driver.")
- Provenance (verified/assumed): VERIFIED first-hand — the false tie occurred this session and flipped to a clear 4-vs-3 gap once the input order was made adversarial to the naive baseline.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E1 · compatible · no sandbox · session (query brain for "brain train combinations in sandbox"), sandbox scripts sweep.mjs/sweep3.mjs/sweep5.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E2 · compatible · no sandbox · session (query brain for "keep training brain on building groups"), sandbox script sweep_diff.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E3 · compatible · no sandbox · session (query brain for "train seams in combination, in sandbox environments"), sandbox script sweep_ratelimit.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E4 · compatible · no sandbox · session (query brain for "train seams, combination, 3 environments, 5 loops, until satisfied" — loop 3/5), sandbox script loop3_graphviz.mjs, no code change to a shipping project
