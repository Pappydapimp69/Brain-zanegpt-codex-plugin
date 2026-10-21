# local/sandbox-anim — lessons

Project: local/sandbox-anim. Newest first.

---

## E6 — event recovery fixes are burst amplifiers
- Date: 2026-07-26
- Project: local/sandbox-anim
- Tags: [animation][state][dsp][realtime][testing][gamedev]
- What: Three recorded lessons composed: - `sandbox-anim/E5` — fire
  looping-timeline events as crossings in raw unwrapped time; enumerate each
  event's loop-copies in (lo,hi]. Wrapping first makes a seam-crossing
  interval unsatisfiable and silently drops the event. -
  `sandbox-brain-loop2-frameacc-loopseam/E1` — count threshold-crossing events
  per sub-step inside the drain loop; once-per-frame undercounts by up to N-1.
  - `sandbox-combined-audio-realtime/E1` — a drain-until-empty consumer is
  real-time-safe only if the producer's burst is bounded. Both event fixes
  exist to stop losing events when dt is large. Tested claim: applied together
  they are precisely a burst amplifier, breaking the third lesson's
  precondition.
- Why built: Two independently-recorded fixes (anim#E5's unwrapped
  seam-crossing detection and frameacc#E1's per-sub-step event counting) both
  exist to stop losing events under a large dt, and both feed a
  drain-until-empty consumer whose safety (audio-realtime#E1) depends on the
  producer's burst staying bounded. The three were tested together because
  each was verified in isolation but never against the precondition the others
  depend on.
- Design: A deterministic sandbox (`sb-loopseam-burst.mjs` + `sb-p5.mjs`)
  drove a fixed sub-step of 1/60s against explicit per-frame dt spikes (0.25s,
  1.0s, 3.0s, 10.0s) and independently varied the sub-step-to-period ratio
  (0.07 to 8.33), comparing wrap-first single-fire detection, per-sub-step
  unwrapped detection, and both a capped and uncapped drain consumer — no RNG,
  so every run is exactly reproducible.
- Got right: Aggregate counts stayed exactly correct under composition at
  every spike tested (4/4, 5/5, 8/8, 16/16) — the two fixes do not lose or
  fabricate events in total, only in per-frame distribution, which is
  precisely why a count-based regression test cannot catch the amplification.
- Where/why it failed: The burst is `ceil(spike / period)` and unbounded in
  spike length: a 0.25s lag spike on a 0.25s-period timeline emits 1 event in
  one frame, 1.0s emits 4, 3.0s emits 12, 10.0s emits 40. Against a drain cap
  of 8 the 3s and 10s spikes overrun by 1.5x and 5x. Aggregate counts stay
  exactly correct throughout (4/4, 5/5, 8/8, 16/16) — the composition is wrong
  in *distribution*, not in total, which is why a count-based test cannot see
  it. The lossy alternative is genuinely lossy: wrap-first, once-per-frame
  detection holds the burst at 1 but delivers 4 of 8, 4 of 16, 4 of 44 events.
  "Safe" here means silently dropping 90% of them. **1. A transient spike is
  survivable; only a sustained rate diverges.** Feeding these bursts to the
  capped consumer, the queue absorbs and clears them: a 10s spike peaks the
  queue at 32 and costs 67ms of worst-case delay across 4 backlogged frames,
  then returns to empty. That is the opposite of a sustained over-cap
  producer, which diverges without bound (a companion sandbox measured 2400
  messages queued after 10s at 12/frame against a cap of 8 — 5.0 seconds of
  latency). So `audio-realtime/E1`'s "bounded burst" precondition needs
  splitting: a bounded-INTEGRAL transient is fine under a cap, a rate above
  the cap is not. Burst size alone does not predict which one you have. **2.
  `anim/E5`'s unwrapping is not always load-bearing.** Once events are
  detected per sub-step, wrap-first detection is *exact* while the sub-step is
  small relative to the period, and only then breaks — measured against an
  exact reference at a 0.5s spike: substep/period 0.07 → wrap-first 5/5 exact
  substep/period 0.17 → wrap-first 12/12 exact substep/period 0.33 →
  wrap-first 23/23 exact substep/period 0.83 → wrap-first 12/58 WRONG
  substep/period 1.00 → wrap-first 3/70 WRONG substep/period 8.33 → wrap-first
  23/583 WRONG Unwrapped enumeration was exact at every ratio. The
  seam-straddle E5 describes cannot occur while one sub-step never spans a
  whole period — the per-sub-step drain already prevents it. Unwrapping
  becomes necessary somewhere between 0.33 and 0.83, i.e. as the timeline
  period approaches the fixed timestep.
- Fix: Split audio-realtime#E1's bounded-burst precondition into two cases: a
  bounded-INTEGRAL transient is safe under the existing drain cap, but a
  sustained rate above the cap is not and needs its own detection (e.g. an
  alarm on persistent carryover), not a bigger cap. Keep anim#E5's unwrapped
  seam-crossing detection only where the sub-step can approach the timeline's
  period (empirically, above roughly a third of the period); below that,
  per-sub-step wrap-first detection is already exact and the extra unwrapping
  machinery is unnecessary.
- Why this fix: Treating every burst the same — either always capping or
  always unwrapping — either misses the sustained-rate divergence a
  transient-only mental model can't see, or pays for seam-unwrapping machinery
  in the regime where it provably makes no difference. Each composed lesson's
  precondition needs to be checked against what the OTHER lessons in the same
  loop can actually produce, not assumed to hold from its own isolated test.
- Rule of thumb: Two independently-correct "recover the events we were
  dropping" fixes compose into a burst amplifier: each one raises the event
  count under exactly the condition (a large dt) that the downstream consumer
  is least able to absorb. Whenever you fix event loss, ask what now receives
  the recovered events, and check the per-frame distribution rather than the
  total — a count assertion passes on both the safe and the pathological
  version. Distinguish a bounded-integral TRANSIENT from a sustained over-cap
  RATE before deciding a drain cap protects you: the first drains and costs
  latency measured in milliseconds, the second diverges and costs seconds.
  They look identical at the instant of overrun. And check whether a "always
  do X" timing rule has a regime where it is inert: here, per-sub-step
  detection subsumes unwrapping entirely while sub-step is under a third of
  the period. Knowing the ratio at which a rule starts mattering is worth more
  than the rule.
- Provenance (verified/assumed): Verified first-hand — deterministic sandbox
  (`sb-loopseam-burst.mjs` + `sb-p5.mjs`, fixed sub-step 1/60s, dt supplied
  explicitly per frame, no RNG). All numbers below are observed output; the
  part-5 reference count is derived from the accumulator's own final time in
  integer period-counts, not from the sum of dts, which differs by the
  undrained remainder.
- Composed: sandbox-anim/E5, sandbox-brain-loop2-frameacc-loopseam/E1,
  sandbox-combined-audio-realtime/E1
- Link: projects/local__sandbox-anim.md,
  projects/local__sandbox-brain-loop2-frameacc-loopseam.md

## E5 — sandbox anim timeline events dropped by wrapping
- Date: 2026-07-11
- Project: local/sandbox-anim
- Tags: [animation][state]
- What: A looping timeline fires time-stamped events (a callback at t=0.7, a
  footstep frame) by wrapping the playhead's from/to times into local phase
  FIRST and then comparing `ev.t > wrap(from) && ev.t <= wrap(to)`. Wrapping
  before the comparison destroys the winding information, so events are
  silently dropped whenever an advance crosses the loop seam or spans
  multiple loops.
- Why built: A keyframe timeline/sequencer that advances a playhead by dt
  and fires events as the playhead crosses their times, in loop and
  ping-pong modes.
- Design: `advance(dt)` moves the playhead, wraps both endpoints modulo the
  loop length, and fires events whose time falls in the wrapped interval.
- Got right: Sampling values and simple within-loop event firing worked; the
  bug appears only at seam-crossing and multi-loop advances.
- Where/why it failed: Advancing 0.6→1.4 on a length-1 loop wraps to
  `from=0.6, to=0.4`, so the test `ev.t > 0.6 && ev.t <= 0.4` is
  unsatisfiable and NO event fires; a dt spanning two full loops collapses
  to `wrap 0..0` and drops everything. The failure is invisible until a
  single frame is long enough to straddle the seam, so it hides at high
  frame rates and appears under lag.
- Fix: Stay in raw, monotonic (unwrapped) time and enumerate every
  loop-copy of each event in the open-closed interval `(lo, hi]`
  (`n = floor((lo - ev.t)/L)+1 … floor((hi - ev.t)/L)`), firing them sorted
  by absolute time so order and multiplicity are correct across seams,
  multi-loop steps, and backward scrubs. The unwrap must also MATCH the play
  mode — a loop is a sawtooth phase warp while ping-pong is a triangle warp,
  and reusing the sawtooth logic for ping-pong fires a phantom event at a
  phase never reached and misses the double-cross at the turn.
- Why this fix: Event firing is a crossing question over continuous time;
  the winding number (how many times and in what direction the playhead
  passed the event) only exists in unwrapped time. Comparing wrapped phases
  throws that away.
- Rule of thumb: Detect timeline/sequencer events as CROSSINGS in raw,
  unwrapped monotonic time and enumerate each event's loop-copies in the
  interval — never wrap the playhead endpoints first, which makes the
  seam-crossing interval unsatisfiable and drops events (and a multi-loop dt
  drops all of them). Fire sorted by absolute time; and the unwrap must
  match the play mode (sawtooth for loop, triangle for ping-pong) or you get
  phantom/missed events at the turn. Invisible until a frame straddles the
  seam, so test with large dt.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: wrapping before comparison fired `[]` (nothing) for
  a 0.6→1.4 seam-crossing advance (expected C,A), for a two-loop advance
  (expected each event twice), and for a backward advance; the raw-time
  loop-copy-enumeration fix produced `[C,A]`, `[A,B,C,A,B,C]`, and
  `[C,B,A]`; reusing the loop unwrap for ping-pong produced a phantom event
  and missed a double-cross.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-anim-timeline
  (`timeline.js` `advance` event loop). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/animation/timeline-events-fire-on-crossings-in-unwrapped-time).
- Cited-by: 2026-07-26 · projects/local__sandbox-anim.md#E6 · compatible · no sandbox · projects/local__sandbox-anim.md, projects/local__sandbox-brain-loop2-frameacc-loopseam.md
- Cited-by: 2026-07-13 · projects/local__sandbox-brain-loop2-frameacc-loopseam.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); scratchpad loop2-frameacc-loopseam.mjs.

## E4 — sandbox anim fsm transition state leak
- Date: 2026-07-11
- Project: local/sandbox-anim
- Tags: [animation][state][gamedev]
- What: In an animation state machine, per-clip state — the frame index, the
  time accumulator, and the `done`/completion flag — belongs to the CURRENT
  clip and must all be reset on transition. Leaking them across clips (the
  most common animation-FSM bug) makes a new clip start on the previous
  clip's frame with its carried accumulator, and — worse — playing a clip
  right after a finished one-shot inherits `done = true` and a past-the-end
  index, so the new clip is born "already complete" and displays an
  `undefined` frame. Relatedly, one-shot completion must be an edge fired
  once (clamp on the last frame and latch), not a per-tick level.
- Why built: A sprite animation FSM with idle/run/jump/attack clips
  (looping and one-shot), transitioning on state changes, tested across
  transitions and interrupt/re-entry.
- Design: An animator holds `currentClip`, `frameIndex`, `accumulator`,
  `done`; `play(clip)` switches clips; `tick(dt)` advances frames.
- Got right: Playing and looping a single clip worked; the bugs are in
  transitions and one-shot termination.
- Where/why it failed: `play()` swapped the clip but shared the animator's
  fields, so `run` began on `idle`'s frame 3 with its accumulator, and
  after a finished `attack` (done=true, index past the end) a `play('hit')`
  inherited both and showed frame[length] = undefined while reporting
  instantly done. Separately, a one-shot with no terminal handling either
  wrapped to 0 (ignoring the non-loop flag), overran into an undefined
  frame, or re-fired "done" on every tick.
- Fix: `play()` resets `frameIndex = 0`, `accumulator = 0`, and
  `done = false` — guarded by a same-clip no-op so re-requesting the
  currently-playing clip doesn't restart/pop a held state. One-shot end:
  clamp on the last frame and latch `done` so completion emits exactly once.
- Why this fix: Clip playback state is per-clip; sharing the animator's
  fields across clips leaks index/timing/completion into the next clip.
  Resetting on enter makes each clip start clean; the same-clip no-op keeps
  a continuous state from popping. Latching `done` turns completion into the
  edge event that listeners (chain the next attack, return to idle) actually
  need.
- Rule of thumb: An animation FSM's per-clip state (frame index, time
  accumulator, `done` flag) must be reset on every transition — sharing the
  animator's fields leaks the previous clip's frame/timing/completion into
  the next, and a clip played after a finished one-shot is born "already
  done" showing an undefined frame. Reset all three in `play()`, guard with
  a same-clip no-op so a held state doesn't pop, and make one-shot
  completion an edge (clamp the last frame + latch done once), never a
  per-tick level.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: an inheriting `play()` started `run` on idle's
  frame 3, and `play('hit')` after a finished `attack` was born done with
  frame index past the end (undefined frame); the reset-on-enter +
  same-clip-no-op fix started each clip at frame 0 with done=false and
  preserved a held state; a one-shot without terminal handling variously
  wrapped to 0, overran to `undefined`, or re-fired done every tick, all
  fixed by clamp+latch.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-anim-fsm
  (`animator.js` `play()` / one-shot end). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/animation/reset-all-per-clip-state-on-transition-and-fix-render-vs-step-order).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E3 · compatible · no sandbox · session (query brain for "brain analyze groups and train in sandbox, 3 sandbox environs"), sandbox scripts engine.mjs/sweep4_anim.mjs/sweep4b_anim_fixed.mjs, no code change to a shipping project
- Cited-by: 2026-07-26 · projects/local__sandbox-voice-pool-reset.md#E1 · compatible · no sandbox · projects/local__sandbox-anim.md, projects/local__sandbox-combined-audio-realtime.md

## E3 — sandbox anim framerate dependent smoothing
- Date: 2026-07-11
- Project: local/sandbox-anim
- Tags: [animation][gamedev]
- What: Motion written as a fixed per-frame factor —
  `value += (to - value) * 0.1` ("ease toward the target by 10% each
  frame") — runs at a speed that depends on frame rate. It's a geometric
  decay measured in FRAMES, not seconds, so it converges faster on faster
  hardware: the same intended 1-second move reached 99.82 at 60fps but only
  95.76 at 30fps.
- Why built: A value-smoothing / ease-toward-target helper, tested at
  multiple dt values to confirm frame-rate independence.
- Design: Per-tick, nudge the value a fixed fraction of the remaining
  distance toward the target.
- Got right: The feel (exponential approach) is desirable; the flaw is only
  that the rate is expressed per-frame instead of per-second.
- Where/why it failed: A constant fraction applied once per frame compounds
  once per frame, so total progress over a fixed wall-clock second scales
  with how many frames occurred in that second. It looks correct at the fps
  it was tuned on and is subtly wrong everywhere else — slower on slow
  devices, faster on fast ones.
- Fix: Either drive from elapsed/duration with an easing function of `t =
  elapsed/duration` (frame-rate exact by construction), or, to keep the
  exponential-smoothing feel, make the factor time-aware:
  `value += (to - value) * (1 - Math.exp(-rate * dt))`.
- Why this fix: Both forms express the motion as a function of elapsed TIME
  rather than a count of frames, so the same wall-clock duration produces
  the same progress regardless of frame rate.
- Rule of thumb: Every per-frame increment in an animation/motion update
  must be a function of `dt` — a bare constant multiplier
  (`value += (to-value)*0.1` per frame) is a geometric decay in frames, not
  time, so it runs faster on faster hardware and is the single most common
  frame-rate-dependence bug. Use elapsed/duration easing, or a time-aware
  factor `1 - exp(-rate*dt)`. Applies to camera follow, value smoothing,
  any real-time motion.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: `value += (to-value)*0.1` per frame reached 99.82 at
  60fps versus 95.761 at 30fps for the same intended 1-second move;
  elapsed/duration easing finished at the identical value across dt = 1/60,
  1/30, and a single dt = 0.5.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-anim-tween
  (`engine.js` `smoothingTick`). Kernel filed in ideas `idea-repository.md`
  (SYSTEM/animation/frame-rate-independent-motion).
- Cited-by: 2026-10-08 · projects/local__sandbox-step-transition.md#E1 · compatible · sandboxes/2026-10-08__step-transition-direction-survives-rapid-nav-only-if-retargeted.py · observed RESULT: PASS 5 scenarios; teleport at input: retarget 0.000 vs naive 0.296. First run had two harness errors of mine (settle threshold 0.01 settled early; max-jump metric dominated by normal easing speed), fixed to measure exact settle and… · brain train auto pass 1 (kernel mode)
- Cited-by: 2026-10-09 · projects/local__sandbox-caffeine-cutoff.md#E1 · compatible · sandboxes/2026-10-09__caffeine-cutoff-is-a-half-life-and-dose-claim-not-a-clock-time.py · observed RESULT: PASS caffeine cutoff as residual target: 9 h residual spans 6.0x across half-life 2.5-10 h, 400 mg@12 h 80 mg > 100 mg@6 h 46 mg, 14:00 cutoff passes only half-life <= 2.7 h, linear scaling breaks at 2000 mg (fraction 0.62 vs 0.31)… · session_01YFLLRpDsfZpRstb2KT2MQy

## E2 — sandbox anim frame accumulator drain and subtract
- Date: 2026-07-11
- Project: local/sandbox-anim
- Tags: [animation][gamedev][state]
- What: A delta-time frame stepper (accumulate `dt`, advance one frame per
  `1/fps`) has two independent correctness rules, and violating either
  degrades animation under real frame timing. It must (1) DRAIN the
  accumulator in a while-loop rather than capping at one frame-step per
  tick, and (2) SUBTRACT the frame duration from the accumulator rather than
  resetting it to zero.
- Why built: A sprite-frame animator advancing clip frames from accumulated
  delta time, tested under lag spikes and sustained low frame rate.
- Design: `tick(dt)` adds dt to an accumulator and, while the accumulator
  holds at least one frame's duration, advances the frame.
- Got right: Under smooth small dt the animator was correct; the two bugs
  only manifest under frame drops / large dt.
- Where/why it failed: (1) A "one frame per tick" cap strands the excess
  when a tick is worth several frames — a `dt = 0.35s` lag spike at 10fps is
  3.5 frames, but only one is consumed, so under sustained large dt the
  animation falls progressively behind real time (measured ~0.6s behind
  after one second of `dt = 0.25`). (2) Resetting the accumulator to 0 after
  a frame discards the sub-frame remainder every step, so timing drifts even
  in exact arithmetic (dropped ~15% of frames over 10 seconds) — this is
  remainder loss, distinct from float imprecision.
- Fix: `while (acc >= frameDur) { acc -= frameDur; step(); }` — drain all
  whole frames the accumulator has earned, and carry the leftover remainder
  forward.
- Why this fix: The accumulator represents "unspent time"; capping spends
  less than earned (lag), and resetting throws away the fractional
  leftover (drift). Draining in a loop and subtracting conserves time
  exactly, so displayed frames track real elapsed time.
- Rule of thumb: A dt-driven frame stepper must DRAIN in a while-loop (a
  cap of one step per tick makes animation lag behind real time under any
  frame drop) AND SUBTRACT the frame duration, never reset the accumulator
  to 0 (resetting discards the sub-frame remainder and drifts, even in exact
  arithmetic). `while (acc >= frameDur) { acc -= frameDur; step() }`. Same
  pattern applies to physics substepping and any fixed-timestep consumer of
  a variable-dt clock.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: a one-step-per-tick cap left the accumulator ~0.6s
  unconsumed after one second of `dt = 0.25` (animation lagging real time);
  resetting the accumulator to 0 produced 85 frame-steps over 10 seconds
  versus 99 for the subtract-remainder version (~15% dropped); the
  while-drain + subtract form tracked real time.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-anim-fsm
  (`animator.js` accumulator modes). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/animation/frame-accumulator-must-while-drain-and-subtract-the-remainder).

## E1 — sandbox anim float time completion miss
- Date: 2026-07-11
- Project: local/sandbox-anim
- Tags: [animation][state][testing]
- What: A tween/animation drives completion off an exact float comparison
  `elapsed >= duration`. Because animation time is a sum of float dt, that
  comparison can be FALSE at the intended end: summing `dt = 1/30` thirty
  times gives `0.9999999999999999`, so `elapsed` never reaches `duration`,
  the value hangs at `99.99999999999999`, and the `onComplete` callback
  never fires — the classic "animation stuck at 99% / callback never runs"
  bug.
- Why built: A tween engine animating a value from A to B over a duration,
  tested for exact arrival and completion firing across several dt values.
- Design: `tick(dt)` accumulates `elapsed += dt`, computes `t =
  elapsed/duration`, samples the easing, and marks done when `elapsed >=
  duration`.
- Got right: The easing and interpolation were correct; the defect is
  solely the exact-equality completion test against accumulated float time.
- Where/why it failed: Float summation doesn't land exactly on the target,
  and — worse — the error DIRECTION depends on the dt: `60×(1/60) =
  1.0000000000000013 > 1` overshoots and fires fine, while `30×(1/30) < 1`
  undershoots and never fires. So the identical code works at one frame
  rate and silently fails at another, making it look intermittent rather
  than deterministic.
- Fix: Test completion with tolerance (`t >= 1 - 1e-9`) AND snap the value
  to the exact target on completion, so both the callback and the final
  value are correct regardless of float rounding direction.
- Why this fix: The intent is "reached the end," which is a tolerance
  question, not an exact-equality one, on any accumulated float. Snapping
  guarantees the visible end state is exact even though the accumulated time
  isn't.
- Rule of thumb: Never gate an animation/timeline completion (or any
  milestone) on an exact `>=`/`==` against accumulated float time — the sum
  lands just under or just over the target depending on the dt, so the
  callback silently never fires (or the value hangs a hair short) at some
  frame rates and not others. Use a small tolerance and SNAP to the exact
  target on completion. Same float reality means a fixed-fps sampler holds a
  frame ±1 tick vs the analytic count and an interval endpoint is a
  fencepost — tolerate ±1 tick and don't assert exact advance counts.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check that reproduced the exact sum: `30 * (1/30) =
  0.9999999999999999 < 1`, so an `elapsed >= duration` tween hung at
  `99.99999999999999` and never fired complete, while at dt=1/60 the sum
  overshot and fired — confirming the rounding-direction dependence; the
  tolerance+snap fix landed exactly 100 and fired once across dt = 1/10,
  1/24, 1/30, 1/60.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-anim-tween
  (`engine.js` `tweenTick` completion test). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/animation/accumulated-float-time-needs-tolerance-not-exact-equality).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-brain-viz-growth.md#E8 · compatible · no sandbox · `scripts/brain-viz-three-train.mjs`
- Cited-by: 2026-07-26 · projects/local__sandbox-combined-cutscene-resume.md#E1 · compatible · no sandbox · this session; sandbox scripts compose_cutscene_save.js and compose_testd_v2.js (scratchpad, not committed)
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E218 · compatible · sandboxes/2026-10-14__kawasaki-float-angles-need-integer-lattice.py · observed RESULT: PASS float == rejects 63494/358801 foldable vertices, float reflection 123305/358801, 1e-9 tol and integer tenths 0; grid-step tolerance accepts 358801/358801 non-foldable · brain train auto loop 2 pass 2, 2026-10-14; session_01Fej6hmi1TecJBFrsQdbvMU
- Audited: 2026-10-14 · pass · The entry has no stored sandbox, but its claim is about IEEE-754 double arithmetic, which I re-ran directly: summing 1/30 thirty times gives 0.9999999999999999 (below 1, so an elapsed >= duration test never fires) and summing 1/60 sixty times gives 1.0000000000000013 (above 1, fires), matching the entry. The result is computed by the runtime, not assumed. I also found that 1/10 summed ten times (0.9999999999999999) and 1/24 summed 24 times (0.9999999999999996) undershoot too, so the failure is more common than the two rates named; the dependence on dt is real. The closing remark in the Rule of thumb about fixed-fps samplers holding a frame plus or minus one tick was not exercised by this check, so the pass covers the completion-test claim only. · scheduled brain train auto loop 2 pass 3, audit of sandbox-anim E1; session_01EU6f7a12wCvzUSXEbn87pv
- Reverified: 2026-10-14 · pass · sandboxes/2026-10-14__rebuild-float-time-accumulation-misses-exact-end-comparison.py · observed RESULT: PASS sum30=0.9999999999999999; strict >= late in 13/24 cells, tolerance exact in 24/24, == never fires in 13 late cells · Built my own fixture across eight frame rates and three durations (24 cells), plus a tolerance variant. The core claim reproduced: summing 1/30 thirty times gives 0.9999999999999999, so a strict greater-or-equal against 1.0 completes a frame late (31 steps), and this happened in 13 of 24 cells. The tolerance-and-snap fix landed on the analytic frame in 24 of 24. Two precisions on the wording: with a monotone accumulator the greater-or-equal check fires one frame late and not never, so the callback truly never fires only with an equality check (13 of the late cells) or when elapsed is clamped below the duration; and my first fixture used a wrong analytic frame (banker's rounding of 62.5) and failed before I fixed it. I did not compare my fixture with the entry's own sandbox beyond its stated claim, as it is not stored in sandboxes/. · scheduled brain train auto loop 2 pass 4; session_01BwMXpnGN7oKqipFnskBS6R
