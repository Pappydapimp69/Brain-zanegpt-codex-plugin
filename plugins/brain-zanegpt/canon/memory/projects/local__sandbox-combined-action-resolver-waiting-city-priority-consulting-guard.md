# local/sandbox-combined-action-resolver-waiting-city-priority-consulting-guard — lessons

Project: local/sandbox-combined-action-resolver-waiting-city-priority-consulting-guard. Newest first.

---

## E1 — priority consulting guard is the coordination that works
- Date: 2026-09-28
- Project: local/sandbox-combined-action-resolver-waiting-city-priority-consulting-guard
- Tags: [ui][state][architecture][testing]
- What: Independent re-verification of sandbox-combined-action-resolver-waiting-city-first-writer-guard#E1 from a new angle: 4 roles with fixed priority, every handler-registration order (24) x every multi-role NPC (11 subsets of size 2-4) = 264 cases; waiting-city#E3's `talk` emits one event per role, each handler writes view. Compared no guard (last writer wins), don't-overwrite guard (first writer wins), and an in-handler guard that overwrites only when its own role outranks the current view's role (coordination that consults the resolver's priority).
- Why built: The first-writer-guard edge was single-source; its rule of thumb ("coordination must consult the resolver's priority") was stated but the priority-consulting variant was never itself run — only the execution-time resolver was.
- Design: Pure enumeration, no RNG/timing, byte-identical output across runs. Assert view == resolver choice (highest-priority present role). Extra fixtures: handler order == priority, and handler order == REVERSE priority.
- Got right: Priority-consulting guard: 0/264 mismatches (0/144 on the 2-role waiting-city shape) — in-handler coordination is viable as long as it compares priority, so the original "or explicit coordination" escape hatch is valid, just not in its don't-overwrite form.
- Where/why it failed: No guard and don't-overwrite guard mismatch on exactly the same count, 154/264 (72/144 for 2-role) — they are mirror images of each other over the full order space. Fixed-order fixtures pick a winner arbitrarily: order==priority gives none 11/11 vs guard 0/11; order==reverse-priority gives none 0/11 vs guard 11/11. So any single-order regression test certifies whichever strategy happens to align with it, and a registration-order refactor flips the verdict.
- Fix: Either dispatch only the resolver's choice in the reducer, or make the shared-target guard compare priority (`if view is None or prio[r] > prio[view]`), never "skip if already set".
- Why this fix: Both variants make priority the only ordering that matters; handler registration order drops out as a hidden second source of truth (0 mismatches across all 24 orders).
- Rule of thumb: A handler guard on a shared side-effect target is correct only if its outcome is invariant under handler reordering — test it by sweeping registration order, not with one fixture; "don't overwrite" is last-writer-wins reversed, not coordination.
- Provenance (verified/assumed): Verified first-hand — sandbox/first_writer_symmetry.py in brainwork (deterministic exhaustive enumeration, run twice, identical md5). Observed: all orders none 154/264, first 154/264, prio 0/264; order==priority none 11/11, first 0/11, prio 0/11; order==reverse none 0/11, first 11/11, prio 0/11; 2-role only none 72/144, first 72/144, prio 0/144. Assumed: handlers dispatch sequentially in registration order.
- Composed: sandbox-combined-action-resolver-waiting-city-first-writer-guard/E1, sandbox-combined-action-resolver/E1, the-game-the-waiting-city/E3
- Link: brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-29 · projects/local__sandbox-first-writer-guard-mirror-batched.md#E1 · compatible · no sandbox · brain train pass 2 session
- Cited-by: 2026-09-29 · projects/pappydapimp69__the-game-the-waiting-city.md#E19 · compatible · no sandbox · session https://claude.ai/code/session_01Esz5rkarKWhTRgGa59f4aD
