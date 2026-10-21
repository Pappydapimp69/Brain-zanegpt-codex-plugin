# local/sandbox-combined-cutscene-resume — lessons

Project: local/sandbox-combined-cutscene-resume. Newest first.

---

## E1 — cutscene resume tolerance vs marker dispatch
- Date: 2026-07-26
- Project: local/sandbox-combined-cutscene-resume
- Tags: [gamedev][cutscene][state][determinism][testing]
- What: Applying sandbox-anim/E1's prescribed fix (compare accumulated
  timeline float time with a TOLERANCE, don't use a bare `>=`) to a cutscene
  marker-dispatch loop that also has to catch up after a big dt gap
  REINTRODUCES a different bug: markers double-fire. The tolerance makes a
  marker eligible in frame N (`m <= t + eps`) and eligible again in frame N+1
  (`m > prev`, since `m` is barely above the previous `t`), so a
  range-rescan dispatch fires it twice. The two recorded lessons are
  individually correct and actively conflict at this seam; only a MONOTONIC
  POINTER dispatch (consume marker index i, increment, never revisit) is
  idempotent under tolerance by construction.
- Why built: A combined sandbox composing three recorded lessons around one
  real feature — saving and resuming a cutscene mid-playback — to test
  whether their prescriptions compose: sandbox-anim/E1 (float timeline
  tolerance), the-game-prologue/E20 (frame-time/dt handling, a gap loses
  ticks), sandbox-combined-save-system/E2 (persisted positional refs
  silently repoint after reshaping).
- Design: A cutscene timeline of markers at t=1..5s, saved at t=0.5s, then
  resumed after a 5.0s gap with no frames rendered. Three dispatch variants
  compared under the identical gap: (a) uncapped dt firing only the single
  "just passed" marker, (b) capped dt (0.1s) with a per-frame range rescan
  using E1's tolerance, (c) capped dt with a monotonic marker pointer.
- Got right: E1's tolerance IS necessary — the drift is real and
  direction-dependent exactly as E1 states: 30 accumulations of 1/30 give
  0.9999999999999999 (a bare `>=1.0` is FALSE, marker missed) while 60
  accumulations of 1/60 give 1.0000000000000013 (`>=1.0` TRUE, marker fires),
  so the same code silently succeeds at one frame rate and fails at another.
  At a boundary save the drift also changes the already-fired set (0 markers
  considered fired without tolerance vs the intended 1 with it). E20's
  gap-handling concern is also real and severe.
- Where/why it failed: Measured across the 5-marker timeline and the 5.0s
  resume gap — (a) uncapped single-fire dispatch fired only marker 5 and
  SKIPPED 4 of 5; (b) capped-dt range rescan with E1's tolerance skipped
  nothing but DOUBLE-FIRED markers 1 and 5 (fired sequence
  [1,1,2,3,4,5,5], 7 dispatches for 5 markers); (c) the monotonic pointer
  fired exactly [1,2,3,4,5] — 0 skipped, 0 doubled, in order. So the naive
  composition of E1+E20 (add tolerance, add a catch-up loop) trades a
  skipped-marker bug for a duplicate-marker bug, which is worse in a
  cutscene: a re-fired `cmd` marker can re-apply an authoritative state
  change (award an item twice, replay a death).
- Fix: Make marker dispatch pointer-based and idempotent rather than
  range-predicate-based: keep a `nextMarkerIndex`, and per frame run
  `while (next < n && markers[next].at <= t + eps) { fire(markers[next]);
  next++; }`. Cap dt so the catch-up loop can't be starved, and persist
  `nextMarkerIndex` alongside the clock so a resume can't re-derive a
  different already-fired set from the raw float.
- Why this fix: A pointer encodes "already fired" as consumed STATE rather
  than recomputing it from a float comparison every frame, so no epsilon,
  frame-rate, or dt-gap can make the same marker eligible twice — the
  idempotency is structural, not a tuned tolerance. It keeps both source
  lessons' benefits (tolerance still prevents the missed marker; capped dt
  still prevents the starved catch-up) without their interaction.
- Rule of thumb: When one lesson prescribes a TOLERANCE and another
  prescribes a CATCH-UP LOOP over discrete events, check the seam — a
  tolerance widens an event's eligibility window and a catch-up loop
  re-evaluates that window every frame, so together they double-fire unless
  the dispatch consumes events as monotonic state. Prefer consumed-index
  dispatch over recomputed-predicate dispatch for anything that fires side
  effects.
- Provenance (verified/assumed): Verified first-hand. Deterministic Node
  sandbox, no RNG and no real timing (every dt/rate a literal); all numbers
  above are observed output. Honest scope note: the third composed lesson
  (sandbox-combined-save-system/E2) was RE-VERIFIED here rather than
  extended — E2 already names "a cutscene program-counter" as a silent-
  failing ordinal ref, and this sandbox reproduced the same failure in the
  TIME axis (a raw stored clock of 3.5s resolved to beat 'line' before a 2s
  beat was inserted and silently to 'establishing' after, while a symbolic
  marker-id + offset resolved correctly to 'line' both times). That is a
  second independent angle on E2, not a new kernel.
- Composed: sandbox-anim/E1, the-game-prologue/E20, sandbox-combined-save-system/E2
- Link: this session; sandbox scripts compose_cutscene_save.js and
  compose_testd_v2.js (scratchpad, not committed)

