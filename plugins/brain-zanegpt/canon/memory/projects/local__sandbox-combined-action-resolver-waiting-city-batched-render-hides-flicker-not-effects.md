# local/sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects — lessons

Project: local/sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects. Newest first.

---

## E1 — sandbox combined action resolver waiting city batched render hides flicker not effects
- Date: 2026-09-28
- Project: local/sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects
- Tags: [ui][state][architecture][testing]
- What: Re-verified guard-cannot-be-retroactive#E1 with an independent reimplementation and tested its stated assumption (synchronous render). Batched rendering (renderer observes view only at end of tick) drives the transient wrong-modal flicker of priority-consulting guards to 0/264, but leaves stray non-chosen side effects untouched (prio 264/264, prio_full 154/264). A two-phase bid/commit (handlers only bid in registration order, then only the winner commits) matches the pre-dispatch resolver at 0/0/0.
- Why built: brain train AIM listed single-source edge guard-cannot-be-retroactive + priority-consulting-guard; the prior entry's Provenance assumed a synchronous renderer, so the batched case was an untested boundary where the flicker metric might vanish and make the guard look sufficient.
- Design: Deterministic exhaustive enumeration, no RNG/timing: 4 roles with fixed priority, every multi-role subset (11) x every registration order (24) = 264 cases. Strategies none / prio (guard on view write only) / prio_full (guard wraps handler) / bid (collect bids, commit max) / exec (resolver picks before dispatch). Render modes sync (frame after every view write) vs batched (one frame at tick end). Metrics: final mismatch, any non-chosen side effect, any non-chosen frame shown.
- Got right: Sync numbers reproduce the prior entry exactly (none 154/264/264, prio 0/264/154, prio_full 0/154/154, exec 0/0/0). bid = exec = 0/0/0 in both render modes.
- Where/why it failed: batched none 154/264/154, prio 0/264/0, prio_full 0/154/0 — flicker disappears, so a visual test under a batched renderer passes while quest-offered/shop-fetch/sfx side effects still fire in 154-264 of 264 cases. Batching hides the symptom that makes the ordering bug visible, not the bug.
- Fix: Keep resolve-before-dispatch (or two-phase bid/commit when handlers must self-nominate); do not accept "renderer is batched" as a reason the in-handler guard is enough. Test side effects directly, not rendered frames.
- Why this fix: Batching only coalesces view reads; side effects execute at handler time, which the guard cannot gate retroactively. Separating nomination (pure) from commit (effectful) removes the window regardless of render mode.
- Rule of thumb: Batched render masks the flicker of a priority guard but not its stray side effects (prio_full still 154/264) — if a visual test goes green after switching to batched render, assert the side effects; split handlers into a pure bid phase and a single commit to reach 0/0/0.
- Provenance (verified/assumed): Verified first-hand — sandbox/guard_retro_batched.py in brainwork, exhaustive 264-case enumeration, run twice, identical output md5 db7dfddd. Observed sync: none 154/264/264, prio 0/264/154, prio_full 0/154/154, bid 0/0/0, exec 0/0/0; batched: none 154/264/154, prio 0/264/0, prio_full 0/154/0, bid 0/0/0, exec 0/0/0 (mismatch/stray/flicker). Assumed: batched renderer paints once per dispatch tick; side effects are synchronous at handler time.
- Composed: sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive/E1, sandbox-combined-action-resolver-waiting-city-priority-consulting-guard/E1, sandbox-combined-action-resolver/E1
- Link: brain train scheduled pass, 2026-09-28
- Cited-by: 2026-09-29 · projects/local__sandbox-first-writer-guard-mirror-batched.md#E1 · compatible · no sandbox · brain train pass 2 session
- Cited-by: 2026-09-29 · projects/local__sandbox-modal-priority-guard-order-permutations.md#E1 · compatible · no sandbox · brain train pass 1 session
