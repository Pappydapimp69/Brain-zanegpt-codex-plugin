# local/sandbox-combined-action-resolver — lessons

Project: local/sandbox-combined-action-resolver. Newest first.

---

## E1 — single ui action needs single execution effect
- Date: 2026-07-13
- Project: local/sandbox-combined-action-resolver
- Tags: [ui][gamedesign][input][state][architecture][testing]
- What: A single player-facing action resolver can keep prompts and buttons consistent while still allowing conflicting backend side effects if command execution fans out across every role on a multi-role entity. The same "one available action" decision has to constrain execution, not just UI display.
- Why built: `brain train` selected the high-value untested seam `dog + the-game-the-waiting-city`. The interaction claim was that dog#E20's single action resolver prevents UI-surface drift, but waiting-city#E3's multi-role command conflict can still happen underneath it unless execution also resolves one command effect.
- Design: Built `sandbox-action-resolver-multirole-command.js`, a deterministic JavaScript model with: - One entity carrying both `shop` and `quest` roles. - A UI action resolver that returns exactly one visible action: `Talk`. - A naive execution path that invokes every role handler for the `talk` command. - A resolved execution path that chooses one role/effect before invoking handlers. - Modal state and emitted-event counts as the observable result.
- Got right: The sandbox does not confuse UI consistency with command consistency. Both paths have the same single user-facing action, so the only tested difference is whether execution fans out or resolves to one effect.
- Where/why it failed: The naive path emitted two events from one `Talk` command: `talked:shop-opened` and `quests_offered:quest-opened`. Both handlers wrote the same modal state, and the quest modal overwrote the shop modal. The UI still looked structurally clean because it only exposed one `Talk` action.
- Fix: Route command execution through the same kind of single-decision resolver used for UI availability, or make multi-role handlers coordinate explicitly before mutating shared view state. Do not let every role independently react to the same command when they share side-effect targets.
- Why this fix: The resolved execution path kept the UI label `Talk` but emitted exactly one event, `quests_offered:quest-opened`, with no conflict. That proves the missing constraint was on execution fan-out, not on the displayed action surface.
- Rule of thumb: One action in the UI is not the same as one effect in the reducer. If an entity can have multiple roles, apply the action resolver at execution time too, or treat shared side-effect targets as requiring explicit coordination.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-action-resolver-multirole-command.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: single UI action + naive multi-role execution = UI label `Talk`, 2 emitted events, final modal `quest`, conflict `true`; single UI action + resolved execution = UI label `Talk`, 1 emitted event, final modal `quest`, conflict `false`.
- Composed: dog/E20, the-game-the-waiting-city/E3
- Link: Sandbox: `sandbox-action-resolver-multirole-command.js`
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-stale-hint-press-lag.md#E1 · compatible · no sandbox · brain train pass 1, 2026-09-29
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling.md#E1 · compatible · no sandbox · scheduled training pass 2, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-hint-lag-full-cycle-sweep.md#E1 · compatible · no sandbox · session (scheduled brain train pass 5)
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-first-writer-guard.md#E1 · compatible · no sandbox · brain train pass, 2026-09-28 scheduled run
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-priority-consulting-guard.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-29 · projects/local__sandbox-execute-resolve-conserves-mismatch.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/local__sandbox-first-writer-guard-mirror-batched.md#E1 · compatible · no sandbox · brain train pass 2 session
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-gamedesign-four-clauses.md#E1 · compatible · sandboxes/2026-10-09__four-clause-game-definition-ablation-and-defect-triage.py · observed RESULT: PASS every ablation fails its own probe=True, leaks={'a': ['b', 'c'], 'b': ['d'], 'c': ['b'], 'd': []}, a-b-c-d order misattributes drop-c to b while a-c-b-d attributes all=True; partial signal survivors=['a==2', 'a==2&par==0'] aft… · scheduled brain train pass 5 (gap mode)
