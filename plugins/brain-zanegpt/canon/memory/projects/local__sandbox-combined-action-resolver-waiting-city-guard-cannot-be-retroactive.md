# local/sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive — lessons

Project: local/sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive. Newest first.

---

## E1 — sandbox combined action resolver waiting city guard cannot be retroactive
- Date: 2026-09-28
- Project: local/sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive
- Tags: [ui][state][architecture][testing]
- What: Re-verified priority-consulting-guard#E1 against action-resolver#E1 from a new angle: the priority-consulting in-handler guard fixes the FINAL shared view (0 mismatches) but not what happens along the way. Handlers run in registration order and a lower-priority role that runs first cannot know a higher-priority role is still coming, so it wins the guard, writes a transient wrong modal and fires its own non-shared side effects (quest marked offered, shop stock fetched, sfx) before being overwritten. Only an execution-time resolver that dispatches just the chosen role gets all three metrics to zero.
- Why built: brain train AIM listed the single-source edge sandbox-combined-action-resolver-waiting-city-priority-consulting-guard + sandbox-combined-action-resolver; prior passes measured only final view state, never transient view writes or per-role side effects under the priority guard.
- Design: Deterministic exhaustive enumeration, no RNG/timing: 4 roles with fixed priority, every multi-role subset (11) x every handler registration order (24) = 264 cases; 2-role waiting-city#E3 shape = 144. Strategies: none (unconditional), prio (guard wraps only the shared view write), prio_full (guard wraps the whole handler body), exec (reducer dispatches only the resolver's choice). Metrics per case: final view != resolver choice; any non-chosen role's side effect applied; any non-chosen modal ever written to view (what a subscribed renderer would flash).
- Got right: Reproduced the prior numbers as a cross-check (none 154/264 final mismatch, prio 0/264). exec: 0/264 mismatch, 0/264 stray side effect, 0/264 transient wrong modal.
- Where/why it failed: prio: 0/264 final mismatch but 264/264 stray side effects (guard only gates the view write) and 154/264 transient wrong modal. prio_full (whole handler gated): still 154/264 stray side effects and 154/264 transient wrong modal — exactly the cases where a lower-priority role is registered before the chosen one. 2-role shape: prio 144/144 stray, 72/144 flicker; prio_full 72/144 stray, 72/144 flicker. The floor is structural: a guard evaluated at handler time is not retroactive, so no in-handler variant can beat it.
- Fix: Resolve before dispatch — the reducer picks the role once (same priority as the UI resolver) and invokes only that handler. Treat in-handler priority guards as fixing final shared state only.
- Why this fix: Deciding before any handler runs removes the ordering window entirely (0/0/0 across all 264 cases); any guard inside handlers sees only the past, not the handlers still queued.
- Rule of thumb: A priority-consulting handler guard makes the END state correct but not the PATH — lower-priority handlers that run first still flash their modal and fire their own effects; if handlers have any effect besides the shared target, or a renderer observes intermediate state, resolve the role before dispatch, and test transient writes and side effects, not just final view.
- Provenance (verified/assumed): Verified first-hand — sandbox/prio_guard_side_effects.py in brainwork (exhaustive enumeration, run twice, identical md5 a92ba657). Observed: none 154/264 mismatch, 264/264 stray, 264/264 flicker; prio 0/264, 264/264, 154/264; prio_full 0/264, 154/264, 154/264; exec 0/264, 0/264, 0/264. Assumed: handlers dispatch sequentially in registration order and a renderer can observe view between handlers (true for synchronous emitters with a store subscription, not for batched render).
- Composed: sandbox-combined-action-resolver-waiting-city-priority-consulting-guard/E1, sandbox-combined-action-resolver/E1, the-game-the-waiting-city/E3
- Link: brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-29 · projects/local__sandbox-modal-priority-guard-order-permutations.md#E1 · compatible · no sandbox · brain train pass 1 session
- Cited-by: 2026-09-29 · projects/pappydapimp69__the-game-the-waiting-city.md#E18 · compatible · no sandbox · session https://claude.ai/code/session_01Esz5rkarKWhTRgGa59f4aD
