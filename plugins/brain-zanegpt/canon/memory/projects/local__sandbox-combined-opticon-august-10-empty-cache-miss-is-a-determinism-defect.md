# local/sandbox-combined-opticon-august-10-empty-cache-miss-is-a-determinism-defect — lessons

Project: local/sandbox-combined-opticon-august-10-empty-cache-miss-is-a-determinism-defect. Newest first.

---

## E1 — sandbox combined opticon august 10 empty cache miss is a determinism defect
- Date: 2026-08-29
- Project: local/sandbox-combined-opticon-august-10-empty-cache-miss-is-a-determinism-defect
- Tags: [determinism][performance][state][testing]
- What: A deterministic sandbox (fixed tick count, explicit shared LCG, no wall-clock) running opticon#E22's empty-result cache miss against a pathfinding call that consumes from a shared sequence, comparing call counts and final shared state under the buggy truthy check and the prescribed existence check.
- Why built: opticon#E22 records that a path cache treating an EMPTY result as uncached re-runs BFS every tick, measured as a 6x whole-sim slowdown with zero visible symptom, and prescribes using null for not-computed. august-10#E28 records that memoization changes call count and that for a function touching a shared sequence, call count IS behaviour. This tests whether opticon#E22's bug is correctly classified as a performance issue once the cached call has a shared-state side effect.
- Design: A BFS stub returning an empty path for an unreachable target and consuming one roll from a shared LCG for tie-breaking. Twenty ticks query one reachable and one unreachable target, run twice — once with the truthy cache check that treats `[]` as a miss, once with an `in` existence check.
- Got right: Giving the cached function a shared-sequence side effect that is realistic for pathfinding (tie-break rolls) rather than an artificial counter, so the divergence follows from the call itself rather than from instrumentation.
- Where/why it failed: The buggy check makes 21 BFS calls against the fix's 2, a 10.5x redundant work factor, but more importantly the two runs end in different shared RNG state (2364415445 versus 378494188). The extra calls are not merely wasted work — they advance the shared sequence, so every downstream consumer of that sequence diverges. The bug is a determinism defect, not a performance one.
- Fix: Classify an empty-result cache miss by whether the cached call has a side effect on shared state, and where it does, treat it as a correctness bug requiring the existence-check fix immediately rather than as a profiling finding that can be deferred.
- Why this fix: opticon#E22's own framing — a slowdown with zero visible symptom — is what makes the bug look safe to leave in place, and that framing is accurate only while the cached function is pure. Under august-10#E28's condition the same code produces a silent replay divergence, which is exactly the class of defect a determinism suite exists to prevent and which no profiler would flag.
- Rule of thumb: opticon#E22's empty-result cache miss is a determinism defect rather than a performance one whenever the cached call touches a shared sequence (august-10#E28) — sandbox-confirmed 21 BFS calls against 2 and, critically, divergent final shared RNG state; the "slowdown with no visible symptom" framing is what makes it look deferrable.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b5/l15.py) and confirmed the truthy check yields 21 calls and final shared state 2364415445 while the existence check yields 2 calls and 378494188, a 10.5x work factor with confirmed sequence divergence. opticon#E22 and august-10#E28 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__opticon/E22, pappydapimp69__august-10/E28
- Link: session_014mRpopK9xnhvk35tT8ozkX

