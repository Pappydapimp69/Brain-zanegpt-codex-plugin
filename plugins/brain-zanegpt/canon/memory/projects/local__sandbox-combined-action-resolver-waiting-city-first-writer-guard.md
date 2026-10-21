# local/sandbox-combined-action-resolver-waiting-city-first-writer-guard — lessons

Project: local/sandbox-combined-action-resolver-waiting-city-first-writer-guard. Newest first.

---

## E1 — sandbox combined action resolver waiting city first writer guard
- Date: 2026-09-28
- Project: local/sandbox-combined-action-resolver-waiting-city-first-writer-guard
- Tags: [ui][state][architecture][testing]
- What: Re-verified sandbox-combined-action-resolver#E1 from a new angle by testing its "or explicit coordination" alternative. A dual/triple-role NPC's single `talk` command emits one event per active role (waiting-city#E3 shape); each handler sets view.modal. A UI-side resolver picks exactly one role by priority. Compared three reducer strategies: ui_only (handlers unconditional, last writer wins), first_writer_guard (handler skips if modal already set — the obvious local "coordination"), exec_resolver (reducer applies the resolver's choice at execution time).
- Why built: Single-source edge sandbox-combined-action-resolver + the-game-the-waiting-city needed independent re-verification; the entry's "explicit coordination" escape hatch was never exercised.
- Design: Deterministic exhaustive sweep, no RNG/timing: 3 roles, every active subset (1-3 roles) x every priority permutation x every emission-order permutation = 252 cases per strategy. Assert modal == resolver choice, and count cases where a non-chosen role's side effect was applied.
- Got right: Execution-time resolver: 0/252 modal mismatches, 0/252 stray side effects. Confirms E1's primary fix.
- Where/why it failed: The first-writer guard is NOT coordination — it only converts last-writer-wins to first-writer-wins. It mismatches the resolver on 78/252 cases, exactly as many as no guard at all (ui_only 78/252), and still applies a non-chosen role's side effect in 78/252 (down from 144/252). Worse, it is invisible to the natural test: in a fixture where handler registration order equals priority order, the guard scores 0/24 mismatches while ui_only scores 24/24 — so the guard looks like a complete fix, then silently breaks the first time priority is re-ranked independently of handler registration order (13/24 multi-role cases mismatch under every one of the 6 emission orders).
- Fix: Put the resolver's decision inside the reducer (dispatch only the chosen role's handler), not a per-handler "don't overwrite" guard.
- Why this fix: A guard lets handler ORDER decide, a second hidden priority source that must be kept in sync with the resolver by hand; the execution-time resolver has one source of truth.
- Rule of thumb: "Explicit coordination" between handlers sharing a side-effect target means consulting the same priority the resolver uses — a don't-overwrite guard just swaps last-writer for first-writer and passes any test whose handler order happens to match priority; re-run the multi-role test with priority and registration order deliberately decoupled.
- Provenance (verified/assumed): Verified first-hand — sandbox/dual_role.py in brainwork (deterministic, exhaustive permutation sweep). Observed: ui_only 78/252 modal mismatch, 144/252 stray side effects; first_writer_guard 78/252 mismatch, 78/252 stray; exec_resolver 0/252, 0/252; aligned-order fixture ui_only 24/24 vs guard 0/24 vs exec 0/24. Assumed: real handler dispatch is sequential in registration order (true for typical event-emitter/reducer loops).
- Composed: sandbox-combined-action-resolver/E1, the-game-the-waiting-city/E3
- Link: brain train pass, 2026-09-28 scheduled run
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-priority-consulting-guard.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-29 · projects/pappydapimp69__the-game-the-waiting-city.md#E19 · compatible · no sandbox · session https://claude.ai/code/session_01Esz5rkarKWhTRgGa59f4aD
