# local/sandbox-combined-game-loop — lessons

Project: local/sandbox-combined-game-loop. Newest first.

---

## E4 — integer time doesnt bound arrival distribution
- Date: 2026-07-26
- Project: local/sandbox-combined-game-loop
- Tags: [determinism][gamedev][state][realtime][testing][architecture]
- What: Three recorded lessons composed: - `game-loop/E2` — drive the
  accumulator from an INTEGER/fixed-point time source with the tick an exact
  integer of base units, so equal-total schedules run an equal tick count (a
  float-dt accumulator strands a ULP-short tick, giving ±1). - `game-loop/E1`
  — authoritative state on the integer lattice; float/feel state is
  presentation-only. - `frameacc/E1` — count discrete events per sub-step
  inside the drain loop. Tested claim: with all three applied, is the loop
  actually schedule-independent end to end, or only up to the tick count?
- Why built: Three recorded lessons (an integer/fixed-point time base with an
  exact-integer tick, authoritative state kept on the integer lattice, and
  per-sub-step event counting) each independently promise
  schedule-independence. The composed claim tested here is whether that
  promise holds end-to-end for a real consumer, or only up to the tick count.
- Design: A deterministic sandbox (`sb-integertime-burst.mjs`) drove an
  integer-microsecond time base (TICK=16666us exact) across four explicit
  frame schedules — steady 60fps, 30fps, 20fps, and a bursty schedule with
  120ms/250ms stalls — all totaling an identical 2,000,000us of simulated
  time, then compared what a drop-on-overflow consumer delivered against a
  carry-over consumer at an identical per-frame cap.
- Got right: Integer time delivers exactly what E2 promises. Across 60fps
  steady (121 frames), 30fps steady (61), 20fps steady (40) and a bursty
  schedule with 120ms and 250ms stalls (36 frames), every run produced **120
  ticks and 40 events**. Tick counts agree, event totals agree. E2 re-verified
  from a new angle (previously fuzzed for count; here checked against
  deliberately lumpy schedules).
- Where/why it failed: The per-FRAME distribution cannot agree and does not,
  because frame boundaries are exactly what differs between schedules: 60fps
  steady maxBurst=1 {0:81, 1:40} 30fps steady maxBurst=1 {0:21, 1:40} 20fps
  steady maxBurst=1 {1:40} bursty maxBurst=5 {0:19, 1:8, 2:3, 3:2, 5:4} Same
  40 events, same 120 ticks, five-to-one difference in peak arrival rate. That
  is harmless while the consumer merely buffers. It stops being harmless the
  moment the consumer DROPS on overflow — a completely standard real-time
  policy, chosen precisely to bound latency: drop-on-overflow (cap 4/frame):
  steady 40 delivered / bursty 36 delivered carry-over (cap 4/frame): 40
  delivered on every schedule A 4-event spread, 10% of the total, on
  **identical simulated time**. If those delivered events touch authoritative
  state — a hit registered, a counter, a resource granted — the simulation has
  diverged as a function of the player's frame rate, in a loop built on
  integer time specifically to prevent that. The lattice discipline of E1 does
  not catch it either: every value stayed an exact integer. What varied was
  how many of them arrived.
- Fix: Keep the drop/keep decision on the integer lattice, not on the frame:
  decide by tick index (drop the event whose tick index fails a deterministic
  rule) rather than by "what did not fit in this frame's budget". Or make the
  lossy consumer strictly presentation — audio, particles, screen shake — and
  forbid it from writing back. Carry-over is the safe default when the
  consumer is authoritative, accepting latency instead of divergence.
- Why this fix: Frame boundaries are the one thing a fixed-timestep design
  deliberately refuses to let into the simulation. A per-frame budget is a
  frame-boundary quantity, so any policy keyed on it is outside the lattice by
  construction, however integral its arithmetic looks.
- Rule of thumb: Integer time buys you an identical tick COUNT, not an
  identical arrival DISTRIBUTION. Those are different guarantees, and the
  second one is unobtainable — frame boundaries are the input that differs. So
  audit every consumer for whether it is a function of per-frame arrival. A
  buffer is safe; anything that drops, throttles, coalesces, or samples "the
  most recent" is a frame-rate-dependent function wearing deterministic
  clothing, and it silently re-couples the simulation to hardware speed. The
  test that catches it is not equal-totals — totals agree. Run identical total
  time on deliberately lumpy versus steady schedules and compare what the
  consumer DELIVERED.
- Provenance (verified/assumed): Verified first-hand — deterministic sandbox
  (`sb-integertime-burst.mjs`: integer-microsecond time base, TICK=16666us
  exact, four explicit frame schedules over an identical 2,000,000us total, no
  RNG). Numbers below are observed output.
- Composed: sandbox-combined-game-loop/E2, sandbox-combined-game-loop/E1,
  sandbox-brain-loop2-frameacc-loopseam/E1
- Link: projects/local__sandbox-combined-game-loop.md,
  projects/local__sandbox-brain-loop2-frameacc-loopseam.md

## E3 — ambient bloom seed breaks game loop fingerprints
- Date: 2026-07-13
- Project: local/sandbox-combined-game-loop
- Tags: [algo][determinism][gamedev][state][testing]
- What: An integer/fixed-timestep game loop can execute the same tick count across frame schedules and still desync canonical per-tick fingerprints if authoritative Bloom state is built with an ambient hash seed. The deterministic loop solves time; it does not make hash-seeded structures deterministic.
- Why built: `brain train` aimed at re-verifying the edge between `sandbox-bloom` and `sandbox-combined-game-loop`. The interaction claim was that Bloom hash seed persistence matters inside game-loop authoritative state: even with integer tick scheduling and integer lattice state, an ambient Bloom seed can make replay/lockstep fingerprints diverge at the first Bloom mutation.
- Design: Built `sandbox-bloom-game-loop-fingerprint.js`, a deterministic JavaScript model with: - A 16-unit fixed tick and 64 total ticks. - Two equal-total integer frame schedules: one 16-unit frame per tick, and paired 5/11-unit frames. - Integer authoritative position state. - A canonical serializer/fingerprint that includes tick, integer position, and Bloom bit state. - A Bloom structure mutated every 8 ticks. - A deterministic Bloom seed case and a two-ambient-seed case.
- Got right: The sandbox isolates time determinism from data-structure determinism. The frame schedules prove the integer accumulator executes the same tick count; the Bloom seed cases prove canonical state can still diverge even when the loop timing is fixed.
- Where/why it failed: With two ambient Bloom seeds, both runs executed 64 ticks, but their canonical fingerprints first diverged at tick 8, the first tick that mutates the Bloom filter. The authoritative integer state stayed valid; the Bloom bit positions differed because the hash seed differed.
- Fix: Use a deterministic, persisted hash seed for any Bloom/hash-based structure included in authoritative game state. Keep per-tick canonical fingerprints, because matching tick counts or end-state scalar positions do not prove hash-backed state matched throughout the run.
- Why this fix: With a deterministic Bloom seed, the two different integer frame schedules both executed 64 ticks and had no per-tick fingerprint divergence. With ambient seeds, the same schedule still diverged at tick 8, proving the remaining nondeterminism came from the Bloom seed rather than timing.
- Rule of thumb: Integer time removes frame-rate nondeterminism, not process-seed nondeterminism. If a hash-based structure participates in authoritative state, its seed is part of the replay state and must be deterministic or persisted.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-bloom-game-loop-fingerprint.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: integer schedules + deterministic Bloom seed = 64 ticks on both schedules and no first divergence; same integer schedule + ambient Bloom seeds = 64 ticks on both runs and first divergence at tick 8.
- Composed: sandbox-bloom/E2, sandbox-combined-game-loop/E1, sandbox-combined-game-loop/E2
- Link: Sandbox: `sandbox-bloom-game-loop-fingerprint.js`

## E2 — combined fixed timestep needs integer time source
- Date: 2026-07-11
- Project: local/sandbox-combined-game-loop
- Tags: [determinism][gamedev][state]
- What: For a fixed-timestep loop to run the SAME number of simulation
  ticks across different frame-rate schedules (required for deterministic
  replay / lockstep netcode), the frame accumulator must be driven by an
  INTEGER / fixed-point time source, not a float `dt` accumulator. A jittery
  float sum can land a few ULPs under the drain threshold and strand a tick,
  so two frame schedules with the same total time run a different NUMBER of
  ticks (±1). The tempting patch — a drain-test tolerance
  (`acc >= FIXED_DT - eps`) — is a band-aid, not a fix.
- Why built: A combined/integration sandbox — one deterministic real-time
  game loop stacking 8 timing/determinism/physics kernels — to test
  whether the fixed-timestep accumulator (drain-and-subtract) and the
  replay-fingerprint determinism guard actually compose.
- Design: The accumulator drains whole fixed ticks per frame and carries
  the remainder; the sim is fingerprinted per tick and re-run from
  (seed + input log) must reproduce the tick sequence across frame
  schedules.
- Got right: Per-tick CONTENT is already deterministic — each tick keys on
  the integer tick index, not wall time, so the two schedules produce
  byte-identical fingerprints for every common tick. The defect is purely
  in the tick COUNT within a wall-time window.
- Where/why it failed: A float accumulator sums float frame-dts; floating
  rounding leaves a residual a few ULPs below `FIXED_DT` on some schedules,
  so strict `acc >= FIXED_DT` drops a legitimately-due tick — one schedule
  ends one tick short of another with the same total time. Adding a
  tolerance lowers the threshold by `eps`, which just MOVES the ±1 boundary:
  it creates a new over-count band `[k·FIXED_DT − eps, k·FIXED_DT)` where an
  honestly-short schedule now over-counts, and the answer depends on the
  arbitrary epsilon (fuzzing flipped the tick count between eps=1e-9 and
  1e-6). The boundary problem is relocated, not eliminated.
- Fix: Drive the accumulator from an integer/fixed-point time source with
  `FIXED_DT` an exact integer number of base units (e.g. 1000 sub-units per
  tick), so the drain test `acc >= FIXED_DT` is EXACT — no tolerance, a
  sharp deterministic boundary, and identical tick counts for every
  equal-total schedule. (The base must divide evenly: a sloppy base like
  `round(1e9/60)` ns is still deterministic but yields a consistently-off
  count.)
- Why this fix: Determinism requires the drain decision to be exact and
  schedule-independent. A float sum makes "have we accumulated a whole tick"
  a fuzzy question; an integer time source makes it an exact integer
  comparison with no rounding residual to strand or over-pull. A tolerance
  keeps the question fuzzy and just picks a different fuzzy boundary.
- Rule of thumb: When a fixed-timestep loop must produce the same tick COUNT
  across different frame rates (deterministic replay, lockstep), drive the
  accumulator from an integer/fixed-point time source with the tick duration
  an exact integer of base units — do NOT paper over a float accumulator's
  ULP-short residual with a drain-test tolerance, which only moves the ±1
  boundary and makes the count depend on the chosen epsilon. Per-tick
  content is usually already deterministic (it keys on the tick index); it's
  the count-in-a-wall-window that the integer time source fixes.
- Provenance (verified/assumed): Verified first-hand this session and
  confirmed by an independent adversarial re-run with fuzzing: over 400
  jittery schedules all summing to the same total, a float accumulator gave
  50/400 the wrong tick count (119 vs 120); a drain tolerance fixed those
  but over-counted constructed adversarial schedules and flipped between
  eps=1e-9 and 1e-6; an integer/fixed-point time source gave 0/400 wrong
  with a sharp boundary and no epsilon.
- Link: session (dog-game-continue-oc3xqh); combined sandbox
  combined-game-loop (`lib.js` accumulator drain test). Refines the
  frame-accumulator kernel in ideas `idea-repository.md`
  (SYSTEM/animation/frame-accumulator-must-while-drain-and-subtract).
- Cited-by: 2026-07-13 · projects/local__sandbox-brain-loop2-frameacc-loopseam.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); scratchpad loop2-frameacc-loopseam.mjs.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-cadence-frametick.md#E1 · compatible · no sandbox · this session's sandbox (sb1_cadence.py); source entries the-game-the-recursion#E16 and sandbox-combined-game-loop#E2.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-cadence-frametick.md#E2 · compatible · no sandbox · session (query brain for "loop: aim, compose from recorded lessons, sandbox, file" — loop 3), sandbox script reverify3_cadence_gameloop.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-game-loop.md#E3 · compatible · no sandbox · Sandbox: `sandbox-bloom-game-loop-fingerprint.js`
- Cited-by: 2026-07-26 · projects/local__sandbox-combined-game-loop.md#E4 · compatible · no sandbox · projects/local__sandbox-combined-game-loop.md, projects/local__sandbox-brain-loop2-frameacc-loopseam.md
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-garden-viz.md#E9 · compatible · no sandbox · Sandbox: `sandbox-garden-viz-schedule.js`; related local artifact: `brain-garden-viz.html`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-realtime-loop.md#E1 · compatible · no sandbox · this session's sandbox (sbT.py); source entries sandbox-combined-game-loop#E2, the-game-the-recursion#E16, sandbox-dbz-combat#E1.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-replan-gameloop.md#E1 · compatible · no sandbox · this session's sandbox build (sandbox_replan_gameloop.py); source entries sandbox-astar-replan#E1 and sandbox-combined-game-loop#E2.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-replan-save.md#E1 · compatible · no sandbox · this session's sandbox (sbR.py); source entries sandbox-astar-replan#E1, sandbox-combined-game-loop#E2, sandbox-savemigrate#E3.
- Cited-by: 2026-09-29 · projects/local__sandbox-lockstep-frame-delta-clamp-tick-parity.md#E1 · compatible · no sandbox · session (scheduled brain train pass 4)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E20 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), harness.mjs (real startGame() executed via Node with browser-global stubs, real frame-schedule sweep), live-unfixed bug flagged at src/app/game.js lines 326-329, NOT applied — pending explicit confirmation
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-recursion.md#E16 · compatible · no sandbox · session (brain train combinations), sandbox script test.mjs (verbatim-logic reproduction, no code change to the shipping project), constants/logic cross-checked directly against the-game-the-recursion's own src/app/explore.js and src/main.js at commit time of this session
- Audited: 2026-10-13 · modeled · The entry has no stored sandbox script, only a description of a fuzz of 400 schedules (50 of 400 float tick counts wrong), so the original run could not be reread or rerun. The mechanism (a float accumulator can land a few ULPs under the drain threshold, an epsilon only moves the boundary, an integer time base makes the test exact) is sound. A quick throwaway check with my own deterministic jitter (400 schedules of 120 frames, 8 to 28 ms, equal-total comparison against an exact integer count) gave 0 wrong for the float accumulator and 0 for the integer one, so the 12.5 percent failure rate depends on how the original schedules were built and is not reproduced by generic jitter. The rule of thumb is therefore a design principle supported by a hand-built schedule family, not a measured rate, which is why the fair verdict is modeled and not pass. · brain train auto audit session 2026-10-13; session_01HK1W7JLSbLXCV3BweWrzfF

## E1 — combined deterministic loop integer lattice arbiter
- Date: 2026-07-11
- Project: local/sandbox-combined-game-loop
- Tags: [determinism][architecture][testing]
- What: In a deterministic real-time game loop, the single decision that
  resolves nearly every timing↔determinism conflict is the DISCRETE /
  CONTINUOUS split: keep authoritative (fingerprinted) state on the INTEGER
  LATTICE and push everything float/feel/tolerance to a read-only
  presentation layer. Draw that line correctly and float-time-tolerance,
  frame-rate-independent motion, and animation completion edges all become
  safe. Two things enforce and complete it: a canonical serializer that
  THROWS on any non-integer authoritative value, and quantization of any
  unavoidable transcendental (the split alone does not cover sqrt/sin/cos).
- Why built: A combined/integration sandbox — one deterministic real-time
  loop stacking 8 kernels (authoritative reducer, split-state,
  fixed-timestep accumulator, float-tolerance, frame-rate-independent
  motion, replay-fingerprint, transcendentals, swept-collision) — to test
  whether the timing kernels and the determinism kernels compose.
- Design: A pure reducer advances discrete state per integer tick; a
  presentation layer interpolates continuous motion; per-tick canonical
  fingerprints must match across frame schedules and platforms.
- Got right: The split-state kernel turned out to be the load-bearing
  arbiter — it single-handedly resolved the float-tolerance-vs-bit-identical,
  frame-rate-independence-vs-determinism, and completion-edge-vs-fingerprint
  conflicts, without having to weaken any other kernel.
- Where/why it failed (before the discipline): putting a float anim-clock +
  tolerance edge in the discrete path fired a discrete event a tick off
  under a big frame; `pos += vel*dt` (float) in the core was bit-unstable
  across schedules (17440 vs 17440.00000000001); a sqrt in authoritative
  logic diverged 1 ULP across libm implementations and flipped the
  fingerprint; a completion edge that applied damage on a float-tolerance
  boundary desynced the per-tick fingerprint even though the final HP
  coincidentally matched (75=75). Each is a float/schedule/platform value
  leaking into the fingerprinted core.
- Fix: Keep the authoritative core on the integer lattice: integer/fixed-
  point positions and timers (float motion is presentation-only
  interpolation); discrete events fire on an integer TICK COUNT, never a
  float-tolerance edge; unavoidable transcendentals are reformulated to
  integer math (squared-distance instead of distance) or truncated back onto
  the lattice; and the canonical fingerprint serializer THROWS on a
  non-integer authoritative value so a mis-drawn line fails loudly at the
  seam. Fingerprint PER TICK, because end-state agreement hides a mid-run
  desync.
- Why this fix: Determinism is exactly "the fingerprinted state is a
  function of integer ticks and integer inputs only." Every conflict was a
  continuous/float quantity leaking into that state; the discrete/continuous
  split names precisely which quantities may not, the integer lattice makes
  the core bit-reproducible, and the serializer-throws guard makes a leak
  detectable immediately instead of as a rare cross-platform desync.
- Rule of thumb: In a deterministic real-time loop, the discrete/continuous
  split is the load-bearing decision — keep authoritative state on the
  integer lattice and make everything float/feel presentation-only. Enforce
  it with a canonical serializer that THROWS on non-integer core state, fire
  discrete events on integer tick counts (never float-tolerance edges),
  quantize unavoidable transcendentals (or use squared-distance), and
  fingerprint PER TICK — because end-state agreement hides a mid-simulation
  desync that a networked/lockstep match would still hit.
- Provenance (verified/assumed): Verified first-hand this session and
  confirmed by an independent adversarial re-run: reproduced each leak
  (float completion edge off by a tick, float `pos` bit-unstable across
  schedules, 1-ULP sqrt divergence, per-tick desync-at-tick-28 while final
  HP matched 75=75) and its integer-lattice fix; confirmed the split-state
  kernel resolves S2/S3/S6 alone and that S4 additionally needs quantization
  of the transcendental (the split is necessary but not sufficient there).
- Link: session (dog-game-continue-oc3xqh); combined sandbox
  combined-game-loop. Refines the split-state, replay-fingerprint, and
  transcendentals kernels in ideas `idea-repository.md`.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E4 · compatible · no sandbox · session (query brain for "5 loops" — loop 2/5), sandbox script loop2_bloom_gameloop.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-game-loop.md#E3 · compatible · no sandbox · Sandbox: `sandbox-bloom-game-loop-fingerprint.js`
- Cited-by: 2026-07-26 · projects/local__sandbox-combined-game-loop.md#E4 · compatible · no sandbox · projects/local__sandbox-combined-game-loop.md, projects/local__sandbox-brain-loop2-frameacc-loopseam.md
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-loop-combat.md#E1 · compatible · no sandbox · session (query brain for "brain analyze groups and train in sandbox, 3 sandbox environs"), sandbox script sweep.mjs/sweep_fixed.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E3 · compatible · no sandbox · session (query brain for "brain analyze groups and train in sandbox, 3 sandbox environs"), sandbox scripts engine.mjs/sweep4_anim.mjs/sweep4b_anim_fixed.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-tickorder-cancel.md#E1 · compatible · no sandbox · this session's sandbox (sb3_cancelorder.py); source entries sandbox-dbz-combat#E1 and sandbox-combined-game-loop#E1.
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-determinism.md#E8 · compatible · sandboxes/2026-09-28__train-gap-b06.py · session 2026-09-28, brain train gap batch 6 loop 28
- Cited-by: 2026-07-13 · projects/local__sandbox-seam-loop-movement.md#E1 · compatible · no sandbox · session (brain train edge/group), sandbox scripts test.mjs (discarded, non-converging setup) / test2.mjs (kept), no code change to a shipping project
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E20 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), harness.mjs (real startGame() executed via Node with browser-global stubs, real frame-schedule sweep), live-unfixed bug flagged at src/app/game.js lines 326-329, NOT applied — pending explicit confirmation
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E218 · compatible · sandboxes/2026-10-14__kawasaki-float-angles-need-integer-lattice.py · observed RESULT: PASS float == rejects 63494/358801 foldable vertices, float reflection 123305/358801, 1e-9 tol and integer tenths 0; grid-step tolerance accepts 358801/358801 non-foldable · brain train auto loop 2 pass 2, 2026-10-14; session_01Fej6hmi1TecJBFrsQdbvMU
