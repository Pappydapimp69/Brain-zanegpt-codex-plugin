# local/sandbox-capture-layer-starves-tutorial — lessons

Project: local/sandbox-capture-layer-starves-tutorial. Newest first.

---

## E4 — generic trigger masks capture layer
- Date: 2026-09-28
- Project: local/sandbox-capture-layer-starves-tutorial
- Tags: [ui][gamedesign][input][testing]
- What: Re-verified the draft#E9 x the-game-prologue#E15 edge from a new angle: whether the tutorial trigger is entity-pinned or generic decides whether the closed-vocabulary capture-layer bug is visible at all.
- Why built: capture-layer-starves-tutorial#E1 assumed the tutorial step was pinned (per the-game-prologue#E15). The unpinned case was never tested — does starvation still surface there?
- Design: Deterministic sandbox (pin_masks.py, no RNG): 3 entities (a1,a2 in old zone A; b1 in new zone B), tutorial target = tap b1. All 65 click sequences of length 4 over {a1,a2,b1} that contain b1. Capture vocab buggy={A} vs fixed={A,B}; trigger generic (any tap) vs pinned (tap on b1).
- Got right: Pinned trigger (the-game-prologue#E15) behaves as a detector: buggy vocab -> 0/65 completions, so the dead zone B shows up as "tutorial never completes"; fixed vocab -> 65/65 complete exactly at the b1 tap, 0 early.
- Where/why it failed: Generic trigger + buggy vocab -> tutorial "completes" in 64/65 sequences while zone B reaches the resolver in 0 of them (bug fully masked); the only failure is the degenerate all-b1 sequence. Even with fixed vocab the generic trigger completes early (before b1 is touched) in 38/65.
- Fix: Pin tutorial triggers to the specific entity/zone they teach; treat a pinned tutorial step on a newly added zone as an end-to-end smoke test of the capture vocabulary.
- Why this fix: Generic triggers are satisfied by in-vocabulary events from old zones, so the tutorial's completion signal stays green while the new zone is dead — the one symptom that would have exposed draft#E9 disappears.
- Rule of thumb: An unpinned tutorial step doesn't just fire by accident (the-game-prologue#E15) — it hides capture-layer starvation (draft#E9); pinning turns the tutorial into a free detector for a dead new zone.
- Provenance (verified/assumed): Verified first-hand — sandbox pin_masks.py, observed: buggy/generic completed 64/65 with 64 masked (zone B reached resolver 0/64), early 38; buggy/pinned completed 0/65; fixed/generic 65/65, early 38, exact 27; fixed/pinned 65/65, exact 65, early 0. Assumed: real tutorials consume the same post-capture event stream as the resolver.
- Composed: draft/E9, the-game-prologue/E15, sandbox-capture-layer-starves-tutorial/E1
- Link: scheduled brain train session 2026-09-28
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E177 · compatible · sandboxes/2026-10-13__assertion-discrimination-matrix-capture-layer-and-shared-resource-fsm.py · observed RESULT: PASS checks all true; generic 0.015, pinned 1.000, resolver 1.000, position 0.000, fsm 1.000, any-green 64/65 on buggy, all-pass 0/65, inverted-bug pinned green 1.000. · scheduled brain train session, loop 2 pass 2; session_01Vd1XXerYpxYYjyMDy9FPmH

## E3 — safety guard placement is a capture layer decision
- Date: 2026-07-26
- Project: local/sandbox-capture-layer-starves-tutorial
- Tags: [input][ui][architecture][gamedev][testing][state]
- What: `capture-layer/E1` records that a closed-vocabulary capture layer
  silently starves every downstream consumer of the same event stream.
  Separately, a platform-key guard was added to Dog so browser keystrokes
  (Ctrl, F11, R) stop launching the game. The claim tested: those are the same
  object. A safety filter and a capture layer both drop events before
  consumers see them, so "add a guard" carries the identical starvation risk —
  and the only thing separating a safe guard from a starving one is WHERE it
  sits.
- Why built: capture-layer#E1 already recorded that a closed-vocabulary
  capture layer silently starves every downstream consumer of the same event
  stream, and Dog separately needed a platform-key guard so browser keystrokes
  (Ctrl, F11, R) stop launching the game. The claim tested here is whether
  those are the same object — whether a safety filter and a capture layer
  carry the identical starvation risk, distinguished only by WHERE the guard
  sits.
- Design: A deterministic sandbox (`sb-guard-placement.mjs`) ran a fixed
  9-event keydown stream (5 platform keys, 4 genuine intents) through four
  downstream consumers, comparing the guard placed at the shared entry point
  (a capture layer) against the same guard placed inside the one consumer that
  needed it (a precondition).
- Got right: The motivating fix itself worked exactly as intended for the
  consumer it was written for: startGame received the identical 4
  genuine-intent events under both placements. The guard's own logic was never
  wrong — only its position in the event pipeline was.
- Where/why it failed: Placing the guard at the shared entry point starved 3
  of 4 consumers by 5 events each — 56% of the stream — while the consumer it
  was written for got exactly the same 4 events under both placements.
  Held-key tracking, the device-hint switch and a settings rebind-capture all
  lost every platform key; the rebind screen could no longer bind Tab or R at
  all, which is not a plausible product decision, just a side effect nobody
  chose. **The starvation is silent in the strict sense that matters.** The
  motivating check — "does startGame still receive platform keys?" — answers
  *no* under both placements. The test written alongside the fix passes
  identically whether the guard is safe or catastrophic, because nothing in it
  looks at the other consumers. There is no failing signal anywhere. A nuance
  worth keeping: the starvation is SELECTIVE, scoped to the denylist's overlap
  with each consumer's needs. Movement keys survived 3/3 here purely because
  WASD is not on the platform list. So spot-checking one downstream consumer
  can return a clean result while another is fully starved — checking "is
  anything else broken?" on the first consumer you think of is not coverage.
  `capture-layer/E2` re-verified in passing: widening the guard mid-session
  recovered nothing already dropped (2 of 5 pre-patch events reached
  consumers, 3 permanently lost; 3 of 4 post-patch). A shipped filter fix
  protects only events going forward.
- Fix: Scope the guard to the consumer that wants it. `if (isStartIntent(e))
  startGame()` at the entry point and `startGame(e)` self-guarding inside look
  equivalent and are not: the first is a capture layer, the second is a
  precondition. Prefer the precondition.
- Why this fix: It also composes better with the union-exposure result on the
  same bug class: a guard living with the capability protects every call site
  at once, and a guard living at one call site protects only that path.
  Placement therefore decides both how much the guard protects and how much it
  breaks, in opposite directions — inside the consumer is better on both axes,
  which is unusual enough to be worth stating.
- Rule of thumb: Before adding any filter to a SHARED entry point, enumerate
  the other consumers of that stream and ask what each one needs the events
  you are about to drop for. A filter that is obviously correct for the
  consumer you are thinking about is a capture layer for everyone else. Guard
  the CONSUMER, not the stream, whenever the guard encodes one consumer's
  preconditions rather than a genuine property of the stream itself. The
  distinguishing question: is this event malformed, or merely irrelevant to
  me? Only the first belongs at the entry point. And note the verification
  trap explicitly: the test you write alongside a guard asserts the symptom is
  gone, which is true in both the safe and the starving placement. Starvation
  needs its own assertion, on a DIFFERENT consumer.
- Provenance (verified/assumed): Verified first-hand — deterministic sandbox
  (`sb-guard-placement.mjs`: a fixed 9-event keydown stream, 5 platform / 4
  genuine, four downstream consumers, no RNG). Numbers below are observed
  output.
- Composed: sandbox-capture-layer-starves-tutorial/E1,
  sandbox-capture-layer-starves-tutorial/E2,
  dog/any-key-to-start-eats-browser-controls
- Link: projects/local__sandbox-capture-layer-starves-tutorial.md,
  projects/pappydapimp69__dog.md
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E18 · compatible · no sandbox · August-10 sandboxes/loop09_event_queue_coalescing_reintroduces_the_bug.mjs
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E20 · compatible · no sandbox · August-10 sandboxes/loop04_timeout_dump_cannot_name_the_layer.py
- Cited-by: 2026-10-08 · projects/local__sandbox-own-four-comparisons-boundary.md#E1 · compatible · sandboxes/2026-10-08__own-four-comparisons-boundary.py · observed RESULT: PASS owned_wrong=0 pipeline_wrong=319/72000; coord-mapping break=464; dual-path doubles fires · scheduled brain train session 2026-10-08

## E2 — capture layer starvation generalizes and loss is permanent
- Date: 2026-07-20
- Project: local/sandbox-capture-layer-starves-tutorial
- Tags: [ui][gamedesign][input]
- What: Re-verifies `sandbox-capture-layer-starves-tutorial#E1`'s claim
  ("a closed-vocabulary capture layer silently starves EVERY downstream
  consumer of the dispatched-event stream") from a genuinely new angle:
  a THIRD, structurally different consumer type (a running achievement/
  analytics counter, not a pinned single-step tutorial tracker), a
  realistic MIXED event stream across four zones instead of one zone
  repeated uniformly, and — new territory neither original entry
  touched — a mid-stream vocabulary PATCH testing whether already-
  dropped events are retroactively recoverable once the missing id is
  added. They are not: loss at the capture layer is permanent per-event,
  not per-session.
- Why built: `brain train` (bare) flagged `sandbox-capture-layer-
  starves-tutorial + draft` as a single-source edge needing
  re-verification from a new angle to raise independence (58/216 edges
  currently multi-source). The existing chain — draft#E9 (a closed-
  vocabulary capture layer starves a resolver branch) →
  the-game-prologue#E15-shaped tutorial trackers inherit the same gap
  (capture-layer-starves-tutorial#E1) — had only ever been tested with
  ONE always-unknown zone over 300 uniform frames, checking exactly two
  downstream consumer types' final boolean state.
- Design: `sandbox.mjs` — deterministic (no RNG, no wall-clock), a fixed
  40-event schedule interspersing four zones (`well`, `bell`, `statue`
  all pre-known; `shrine_altar` starting OUTSIDE the known-id
  vocabulary). Three downstream consumers wired to the same dispatched-
  event stream: a resolver-fired counter (mirrors draft#E9), a pinned
  `(shrine_altar, "pray")` tutorial tracker (mirrors
  the-game-prologue#E15/capture-layer-starves-tutorial#E1), and a NEW
  achievement counter tallying ALL dispatched `"pray"` events regardless
  of which zone (both `shrine_altar` and `statue` share the `pray` verb
  — a consumer that aggregates across sources, structurally distinct
  from a single pinned-id tracker). Two scenarios: (A) `shrine_altar`
  never added to the vocabulary; (B) added mid-stream at event index 20
  (a simulated live patch), comparing pre-patch vs post-patch shrine
  clicks explicitly.
- Got right: reused the exact same `captureClick`/`resolveAction`
  mechanics as the original sandbox (no drift in what's being tested),
  changing only the event-stream shape, consumer count/type, and adding
  the mid-stream-patch condition — an intentionally different angle on
  the identical underlying mechanism, not a different mechanism.
- Where/why it failed: N/A — this re-verifies and extends a known
  finding, it does not report a new bug. Scenario A: all 15 shrine
  clicks dropped at capture, resolver never fires, tutorial never
  completes, achievement count settles at exactly 9 (the schedule's
  statue-only prays) — confirming the starvation generalizes to a THIRD
  consumer type exactly as the original entry's rule of thumb predicted
  but never checked. Scenario B (mid-stream patch at event 20): of 15
  total shrine clicks, the 7 that occurred BEFORE the patch are dropped
  permanently (never resolved, never counted, never recoverable), while
  the 8 AFTER the patch resolve normally and the tutorial completes —
  demonstrating that fixing the vocabulary gap protects only events
  from that point forward, with zero retroactive recovery of what was
  already silently lost.
- Fix: same underlying fix as draft#E9 (make the capture layer open-set,
  validated against real content, not a hand-maintained fixed
  vocabulary) — this re-verification adds a documented consequence: a
  live hotfix to the vocabulary does NOT repair damage already done to
  a session in progress (any tutorial/achievement/analytics state that
  depended on a pre-patch event is permanently wrong for that session)
  — a full state audit or reset may be needed post-patch, not just the
  vocabulary fix itself.
- Why this fix: the capture layer has no buffer or replay of dropped
  raw events by design (mirroring draft#E9/the original sandbox
  exactly) — once an event fails the known-id check, it is discarded,
  not queued, so no later vocabulary change can reach back and re-offer
  it to the resolver.
- Rule of thumb: when re-verifying a "silently starves every downstream
  consumer" claim, don't stop at confirming it holds for the exact
  consumer types already tested — check whether it generalizes to a
  STRUCTURALLY DIFFERENT consumer shape (a pinned single-step tracker
  vs. an aggregate counter), and separately check its TEMPORAL property:
  does fixing the root cause mid-session recover state that was already
  silently lost, or only protect events going forward? These are
  independent questions — a claim can be fully correct on the first and
  still surprise a team that assumes "we shipped the fix" also means
  "existing affected players are now fine."
- Provenance (verified/assumed): Verified first-hand — `sandbox.mjs` run
  to completion for both scenarios, deterministic (fixed 40-event
  schedule, no RNG, no wall-clock), all checks (generality to a third
  consumer type, mixed-stream isolation of unrelated zones, and the
  permanent-loss-vs-recovery-going-forward split) passed programmatically
  (`allPass` gate). Re-ran as two independent process invocations;
  output byte-identical both times.
- Composed: pappydapimp69/draft/E9, pappydapimp69/the-game-prologue/E15,
  local/sandbox-capture-layer-starves-tutorial/E1
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (bare `brain
  train`, re-verifying the flagged single-source edge
  `sandbox-capture-layer-starves-tutorial + draft`); sandbox
  `scratchpad/reverify_capture/sandbox.mjs`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-07-26 · projects/local__sandbox-capture-layer-starves-tutorial.md#E3 · compatible · no sandbox · projects/local__sandbox-capture-layer-starves-tutorial.md, projects/pappydapimp69__dog.md

## E1 — closed vocabulary capture layer also silently starves an onboarding step
- Date: 2026-07-20
- Project: local/sandbox-capture-layer-starves-tutorial
- Tags: [ui][gamedesign][input]
- Composed: pappydapimp69__draft/E9, pappydapimp69__the-game-prologue/E15
- What: `brain train` flagged `draft + the-game-prologue` as an untested high-value seam. draft#E9 found that a closed-vocabulary input-capture layer (fixed known ids) silently drops a NEW UI zone's raw click before a single-action resolver ever sees it, leaving a fully-correct resolver branch permanently inert with zero error. Composed with the-game-prologue#E15 (an onboarding observer watching the DISPATCHED event stream, pinned to a specific entity) and found the same root cause has a SECOND symptom neither entry names alone: the onboarding step pinned to that new zone's verb never fires either, for the identical reason — the observer only ever sees an event AFTER capture-and-resolve, so anything that silently prevents an event from being dispatched silently prevents both the UI branch AND the tutorial from working, and the two would very plausibly get investigated as two unrelated bugs by whoever reports "the new shrine doesn't do anything" versus "the prayer tutorial step never completes."
- Why built: draft#E9 was recorded from an isolated end-to-end test of the resolver branch specifically; the-game-prologue#E15 was recorded from a tutorial-trigger design investigation with no capture-layer failure in scope. Neither session had reason to ask whether the SAME missing-vocabulary condition would also silently break something built on top of the resolver's output, like an onboarding tracker. External research on game-analytics/event-tracking convention (a tracked event is standardly defined as "the action or the RESULT of an action," i.e. built on dispatched/resolved events, not raw input) supports why an observer architecture shaped like the-game-prologue#E15's would structurally inherit any upstream capture-layer gap rather than being independent of it.
- Design: Deterministic Node script (`sandbox_capture_layer_starves_tutorial.mjs`), no RNG, no wall-clock. `captureClick(rawId, knownIds)` mirrors draft#E9/the-game-prologue#E6 — returns the id only if it's in a fixed known-id `Set`, silently drops anything else. `resolveAction(capturedId, actionsById)` is a minimal single-action resolver. `makeTutorialTracker(steps)` mirrors the-game-prologue#E15 — marks a step done only when its pinned `(entityId, verb)` pair is dispatched post-resolve. Two scenarios, 300 simulated frames of the player clicking a new "shrine_altar" zone every frame: (A) the zone's id was never added to the capture layer's known-id vocabulary (draft#E9's original bug condition); (B) control — the id WAS added.
- Got right: Scenario B (control) confirms both the resolver and the tutorial tracker work correctly on their own — the resolver fires for the shrine and the tutorial step completes — when the capture layer's vocabulary is current, isolating the failure to specifically the missing-vocabulary condition, not a defect in either downstream system.
- Where/why it failed: Scenario A ran 300 frames of clicking the shrine zone; the resolver never once fired for it (`resolverFiredForShrine=false`, matching draft#E9's original finding exactly) AND the onboarding step pinned to `(shrine_altar, "pray")` never completed (`tutorialStepDone=false`) — from the SAME single root cause (the capture layer's `knownIds` set was never updated), with no error from any of the three layers (capture, resolve, tutorial), because each one is individually behaving exactly as designed for the inputs it actually receives.
- Fix: Same fix as draft#E9 (confirm the capture layer is open-set — validated against the game's real content list, not a hand-maintained fixed vocabulary — whenever a single-resolver pattern gains a new verb/zone), now with an added consequence to check for: when THAT fix is missing, don't stop at "the new UI branch doesn't work" as the only expected symptom — anything built on the dispatched-event stream downstream of the resolver (tutorials, analytics, achievement triggers) needs the same audit, since they all silently inherit the same gap.
- Why this fix: The capture-layer vocabulary is the single point where the whole downstream pipeline (resolver, tutorial, and anything else listening post-dispatch) either does or doesn't receive an event for a given entity — fixing it there fixes every downstream consumer at once, whereas patching each downstream symptom individually (special-casing the tutorial tracker, say) would leave the same root cause free to produce a THIRD silent-failure symptom in the next system built on the dispatched-event stream.
- Rule of thumb: A single missing-vocabulary/closed-set bug at a capture or dispatch layer doesn't produce one symptom — it silently starves EVERY downstream consumer of that layer's output at once (a UI branch, a tutorial step, an analytics funnel, an achievement), and because each downstream system is individually correct, the symptoms surface as separate-looking bug reports investigated independently unless someone traces them back to the shared capture layer. When investigating "a specific new-content feature seems dead," check whether ANY OTHER system also listens on the same event stream before concluding the bug is local to the one symptom you found first.
- Provenance (verified/assumed): Verified first-hand — `sandbox_capture_layer_starves_tutorial.mjs` run to completion for both scenarios, deterministic (no RNG, no wall-clock, fixed 300-frame loops), each scenario's resolver-fired and tutorial-done booleans printed and checked programmatically (an `allPass` gate; exits 1 and prints "CLAIM DID NOT REPRODUCE — do not file" if either scenario disagreed with the prediction — neither did). External research (not internal reasoning alone) checked whether an event-observer architecture built on dispatched/resolved events (rather than raw input) is standard practice, supporting why the-game-prologue#E15-shaped tutorial systems would structurally inherit an upstream capture-layer gap: game-analytics event-tracking documentation (GameAnalytics, generalistprogrammer.com) defines a tracked event as the action or the RESULT of an action.
- Link: session (this conversation, "brain train external research prologue" — draft + the-game-prologue seam); scratchpad `sandbox_capture_layer_starves_tutorial.mjs`; external source: https://generalistprogrammer.com/tutorials/game-analytics-complete-data-tracking-guide-2025.
- Cited-by: 2026-07-20 · projects/local__sandbox-capture-layer-starves-tutorial.md#E2 · compatible · no sandbox · session 7195397b-63a9-5efe-a80b-2792eaa6645e (bare `brain train`, re-verifying the flagged single-source edge `sandbox-capture-layer-starves-tutorial + draft`); sandbox `scratchpad/reverify_capture/sandbox.mjs`, run twice as independent process invocations, outputs diffed identical
- Cited-by: 2026-07-26 · projects/local__sandbox-capture-layer-starves-tutorial.md#E3 · compatible · no sandbox · projects/local__sandbox-capture-layer-starves-tutorial.md, projects/pappydapimp69__dog.md
- Cited-by: 2026-09-28 · projects/local__sandbox-capture-layer-starves-tutorial.md#E4 · compatible · no sandbox · scheduled brain train session 2026-09-28
- Cited-by: 2026-07-13 · projects/local__sandbox-resolver-starves-tutorial.md#E2 · compatible · no sandbox · session (brain train new-domain tutorial); sandbox `sandbox.py`, scratchpad `gap3/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E16 · compatible · no sandbox · August-10 sandboxes/loop02_fingerprint_blind_to_capture_bug.py
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E18 · compatible · no sandbox · August-10 sandboxes/loop09_event_queue_coalescing_reintroduces_the_bug.mjs
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E20 · compatible · no sandbox · August-10 sandboxes/loop04_timeout_dump_cannot_name_the_layer.py
- Cited-by: 2026-09-28 · projects/pappydapimp69__brain.md#E48 · compatible · no sandbox · session 2026-09-28, brain train target `sandbox-capture-layer-starves-tutorial + dog`; sandbox scratchpad/sbx/sched_capture.py
- Audited: 2026-10-13 · modeled · No sandbox file is stored (the Node script is named in the entry but not shipped), so I judged the written design. The model computes its two scenarios, but the key result is built in: the tracker is defined to see only dispatched events, so a closed capture vocabulary starves it by construction, and the control scenario merely confirms the code behaves as written. The Rule of thumb says a missing vocabulary starves every downstream consumer (UI branch, tutorial, analytics funnel, achievement) but only one consumer, a post-resolve tutorial tracker, was modelled; a consumer reading raw input before capture would not be starved, and the later entry E4 shows a generic trigger masks the bug rather than being starved by it. The claim is about the architecture of a real game reproduced as a hand-written model, so it is modeled rather than pass; it is not a fail because the specific two-symptom finding matches E4's recount (64 of 65 masked). · scheduled brain train session, loop 2 pass 3 (audit); session_01Vd1XXerYpxYYjyMDy9FPmH
