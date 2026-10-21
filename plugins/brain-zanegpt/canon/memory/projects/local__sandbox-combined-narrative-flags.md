# local/sandbox-combined-narrative-flags — lessons

Project: local/sandbox-combined-narrative-flags. Newest first.

---

## E2 — combined narrative emit must snapshot listeners
- Date: 2026-07-13
- Project: local/sandbox-combined-narrative-flags
- Tags: [gamedesign][state]
- What: Combined an event bus with a quest-completion handler that
  unsubscribes itself as part of its own teardown logic. Implementing
  `emit()` by iterating the LIVE listener array while a handler unsubscribes
  mid-dispatch caused a real listener to be silently skipped — removing the
  handler shifts every subsequent listener's index down by one, so a
  standard `for` loop over the live array skips whichever listener now
  occupies the index the loop is about to visit next.
- Why built: The event-bus kernel's "decouples but hides control flow"
  finding had been verified in isolation with listeners that don't mutate
  the bus. This combined test specifically stacked it with a
  self-unsubscribing completion handler — a realistic and common pattern
  (a quest listener that only needs to fire once) — to check whether
  mid-dispatch mutation of the listener list is safe.
- Design: Registered three listeners for one event type, where the second
  listener unsubscribes itself as part of handling the event, then emitted
  the event once and logged which listeners actually ran.
- Got right: Nothing about the individual listener registration/removal
  API was wrong — `subscribe`/`unsubscribe` each work correctly in
  isolation. The bug is specifically in `emit()`'s iteration strategy over
  a collection that a handler is allowed to mutate mid-iteration.
- Where/why it failed: Iterating a live array with `for (let i = 0; i <
  listeners.length; i++)` while a callback at index i removes itself (or
  another listener) shifts the array in place — the listener that used to
  be at i+1 is now at i, but the loop has already advanced past i, so it's
  skipped entirely for this dispatch. This is invisible unless a test
  specifically has a handler mutate the subscriber list during its own
  dispatch, which a straightforward "does each listener get called"
  isolation test won't do unless it's deliberately constructed to.
- Fix: `emit()` must dispatch against an IMMUTABLE SNAPSHOT of the listener
  array taken before the dispatch loop starts (e.g. `[...listeners].forEach
  (...)` or an array copy), so any subscribe/unsubscribe triggered by a
  handler mid-dispatch affects only future emits, never the one currently
  in progress. Re-ran the same three-listener scenario with a snapshot
  taken at dispatch start and confirmed all three listeners ran.
- Why this fix: It makes "who gets called for this emit" a decision made
  once, atomically, at the start of dispatch — rather than a decision
  that's still being computed live while dispatch is in progress and can
  therefore be perturbed by the very dispatch it's driving.
- Rule of thumb: Any pub/sub or observer implementation whose `emit`/
  `notify`/`dispatch` iterates its listener collection must snapshot that
  collection before the loop starts, as a hard requirement rather than an
  implementation detail — this is not optional hardening, it is required
  correctness the moment ANY listener is allowed to subscribe or
  unsubscribe (itself or another) as part of handling the event, which
  includes the common and unremarkable "unsubscribe on completion"
  pattern. Treat "a handler mutates the subscriber list mid-dispatch" as a
  standard case to test, not an edge case.
- Provenance (verified/assumed): Verified first-hand — reproduced a real
  listener being silently skipped when `emit()` iterated the live array
  during a self-unsubscribing handler's dispatch, and confirmed a snapshot-
  before-dispatch fix resolves it (all listeners run) without changing
  subscribe/unsubscribe semantics, in a combined narrative-flags sandbox
  stacking the event bus with a self-unsubscribing completion handler.
- Link: session (dog-game-continue-oc3xqh); combined-narrative-flags
  sandbox, lib/bus.js (emit dispatch loop), pass4.js.
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E253 · compatible · sandboxes/2026-10-14__live-emit-skip-desyncs-shared-rng-snapshot-and-addressed-draws-contain-it.py · observed RESULT: PASS skipped_first_emit=[0, 1, 3, 4] shared_diffs=4/5 addressed_diffs=1/5 nounsub_diffs=0,0 · brain train auto loop 2 pass 2; session_015vYTjNJNEjDvnZgWaJaTSv

## E1 — combined narrative causal token vs type only events
- Date: 2026-07-13
- Project: local/sandbox-combined-narrative-flags
- Tags: [gamedesign][state][testing]
- What: Combined a typed quest-state-machine with an event-bus pub/sub
  layer and a causal-spine narrative requirement (a quest stage must
  advance only as a consequence of a SPECIFIC prior trigger, not merely
  "an event of this type happened"). A quest listening for a generic
  `monster-died` event type advanced on an unrelated monster's death (a
  different wolf, not the quest's target) — reproduced directly: killing
  an unrelated wolf wrongly completed a hunt quest that should have
  required killing the quest's specific target.
- Why built: The event-bus kernel and the typed-quest-state-machine kernel
  had each been verified independently. This combined test specifically
  stacked them with a causal-spine requirement to check whether type-based
  subscription is sufficient once "this specific thing must have caused
  that specific outcome" becomes a real design requirement, which isolated
  testing of either kernel alone never exercised.
- Design: Built an event bus, a typed quest state machine subscribing to a
  `monster-died` event type to advance a "hunt the alpha wolf" quest, and a
  second unrelated wolf entity. Killed the unrelated wolf first and checked
  quest state.
- Got right: The event-bus decoupling and the typed quest state machine
  are each independently correct for what they're designed to do — the bus
  correctly delivers `monster-died` events to all subscribers, and the
  state machine correctly transitions on receiving one. Neither component
  has a bug; the gap is in what "receiving one" was allowed to mean.
- Where/why it failed: Subscribing by event TYPE alone conflates "an event
  of this type happened" with "the specific causally-relevant event
  happened" — these are the same question only when there's exactly one
  possible source of that event type in the whole game, which is rarely
  true. A causally-unrelated event of the identical type and shape (a
  different monster's death) satisfies a naive type-only listener with no
  way to distinguish it from the one the quest actually cares about,
  because nothing in the event carries information about WHICH prior
  trigger the downstream logic is supposed to be gated on.
- Fix: Mint an explicit causal token at the specific outcome that should
  gate the downstream stage (e.g. tag the death event with the specific
  quest-target entity id, or emit a quest-specific event rather than a
  generic type), and require that token match downstream instead of
  matching on type alone. Re-ran the same scenario (unrelated wolf killed
  first, then the actual target) with token-gating in place and confirmed
  the quest only advanced on the target's death.
- Why this fix: It moves the causal relationship from being inferred (type
  + coincidental timing) to being explicit and checkable (a token that
  specifically identifies the triggering entity/outcome), which is the
  only way to distinguish "the right thing happened" from "a similar
  thing happened" when the event bus's whole design point is decoupling
  emitters from listeners.
- Rule of thumb: Whenever a later stage in a quest/narrative/game-logic
  chain must be causally downstream of a SPECIFIC prior outcome (not just
  "an event of this general type"), subscribing by event type alone is
  insufficient the moment more than one possible source of that type can
  exist — which is the common case, not the exception, in any game with
  more than one instance of a given enemy/item/interactable type. Mint and
  require a causal token at the specific outcome; never infer causality
  from type-plus-coincidental-ordering, since a same-type unrelated event
  will silently satisfy the listener and no test that only exercises the
  "happy path" single-source case will ever catch it.
- Provenance (verified/assumed): Verified first-hand — reproduced a quest
  wrongly completing when an unrelated same-type monster died before the
  actual target, and confirmed causal-token gating fixes the exact
  scenario without breaking the legitimate completion path, in a combined
  narrative-flags sandbox stacking the event bus, typed quest state
  machine, and causal-spine requirement.
- Link: session (dog-game-continue-oc3xqh); combined-narrative-flags
  sandbox, lib/bus.js/lib/engine.js/lib/quest-defs.js, pass3.js.
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E22 · compatible · no sandbox · session (brain train, sandboxed until satisfied), sandbox script quest_typematch_sandbox.mjs (live import of real repo source, real seeded RNG), live-unfixed structural gap flagged at src/sim/reduce.js questProgress/hitEnemy kind-matching, not applied
