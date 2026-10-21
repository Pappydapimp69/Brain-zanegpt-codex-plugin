# local/sandbox-combined-audio-realtime — lessons

Project: local/sandbox-combined-audio-realtime. Newest first.

---

## E3 — audio resume queue budget
- Date: 2026-07-13
- Project: local/sandbox-combined-audio-realtime
- Tags: [audio][dsp][determinism][realtime][state][testing]
- What: Persisting a generator's live internal state fixes deterministic audio resume, but it does not make the resume path real-time-safe by itself. If the resume path also emits a large repair burst into a callback-side queue, an unbounded "drain until empty" consumer can still blow the callback budget. The callback needs a per-tick drain cap with carryover.
- Why built: Brain training asked to re-verify the single-source edge between `sandbox-combined-audio-realtime` and `sandbox-combined-bloom-audio` from a new angle. The combined claim was that deterministic resume correctness and callback budget correctness interact in the same recovery path.
- Design: Built `scripts/brain-training-audio-queue.mjs`, a deterministic Node sandbox with no wall-clock timing or RNG. It models a small LFSR noise generator paused after 12 samples, then compares default-seed reload against persisted-live-register reload. The same resume event produces a 2048-message repair burst. The sandbox compares unbounded callback draining against a 64-message cap with a fixed 9us/message cost and a 2800us callback budget.
- Got right: The sandbox reproduced both source lessons in one path: - Default-seed reload mismatched the baseline tail by 13/20 samples. - Persisted-live-register reload mismatched by 0/20 samples. - Unbounded drain processed the full repair burst in one callback, costing 18432us and exceeding the 2800us budget. - Capped drain cost 576us worst-case per callback, stayed inside budget, and cleared the burst over 32 callbacks.
- Where/why it failed: The naive combined fix would persist the live generator state and then treat resume as solved. That fixes audible continuity but ignores the real-time queue dimension: a correct resume can still become unsafe if all repair messages are drained in the next audio callback.
- Fix: Persist live generator state for deterministic continuity, and independently cap callback-side repair-message drain work. Carry remaining messages over to later callbacks.
- Why this fix: The two constraints are orthogonal. Live-state persistence controls sample identity after reload. Drain caps control callback iteration count. The sandbox only passes when both are present: live-state reload for 0 mismatches and capped drain for sub-budget callback cost.
- Rule of thumb: For audio resume paths, verify continuity and callback budget separately. "State resumes correctly" is not evidence that the resume repair queue is real-time-safe.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-training-audio-queue.mjs` on 2026-07-13. Observed output: `resumeMismatchDefaultSeed: 13`, `resumeMismatchLiveState: 0`, `unboundedWorstCallbackUs: 18432`, `cappedWorstCallbackUs: 576`, `cappedCallbacksToClear: 32`.
- Composed: sandbox-combined-audio-realtime/E1, sandbox-combined-bloom-audio/E3
- Link: `scripts/brain-training-audio-queue.mjs`
- Cited-by: 2026-07-26 · projects/local__sandbox-voice-pool-reset.md#E1 · compatible · no sandbox · projects/local__sandbox-anim.md, projects/local__sandbox-combined-audio-realtime.md
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E2 · incompatible · sandboxes/2026-10-15__capped-drain-delays-lfsr-restore-into-permanent-phase-slip.py · observed RESULT: PASS capped FIFO applies the live-register restore on callback 32 and stays wrong after it (14.2% of later samples, 14.8% overall) with peak 1.000 = ref, dft delta 404.9, crc differs; priority slot 0% at 585 us worst; uncapped 0% a… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 2

## E2 — combined audio subnormal decay stuck nonzero
- Date: 2026-07-13
- Project: local/sandbox-combined-audio-realtime
- Tags: [dsp][state][testing]
- What: Combined a denormal flush-to-zero rule with a feedback/IIR decay
  (`y *= 0.9` per sample) in one system. Confirmed `0.9 * Number.MIN_VALUE
  === Number.MIN_VALUE` is exactly true in IEEE-754 double precision — a
  real decay trajectory hit this fixed point and got permanently stuck at a
  small nonzero subnormal after thousands of iterations, never converging
  to exact `0`, unless every sample was flushed unconditionally regardless
  of whether it "should" have reached zero by then.
- Why built: Flush-to-zero is normally filed as a CPU-performance fix
  (subnormal arithmetic is slow on most FPUs) — this combined test stacked
  it against a real decaying feedback loop specifically to check whether
  the two rules interact, since a decay loop implicitly assumes it
  eventually reaches exact zero.
- Design: Ran a `y *= 0.9` decay loop for thousands of iterations without
  flush-to-zero and logged whether `y` ever reached exact `0`; separately
  confirmed the specific rounding fixed point `0.9 * Number.MIN_VALUE ===
  Number.MIN_VALUE` directly in the REPL.
- Got right: Flush-to-zero as a performance optimization (skip slow
  subnormal arithmetic) is completely correct and was never in question —
  the gap is that it's ALSO silently load-bearing for a correctness
  property (termination) that nothing about the "it's just a perf
  optimization" framing would suggest needs it.
- Where/why it failed: A decay multiplier less than 1 applied repeatedly to
  a float doesn't necessarily converge to exact 0 — IEEE-754 rounding can
  land on a subnormal value that the multiplier's rounding behavior can
  never step below (verified: `0.9 * Number.MIN_VALUE` rounds back to
  `Number.MIN_VALUE` itself, a stable fixed point). "It'll eventually reach
  zero" is an assumption about real-number arithmetic that doesn't hold for
  floating point at the subnormal boundary, and it fails silently — no
  NaN, no crash, no obviously wrong output, just a decay that never
  actually finishes.
- Fix: Flush to zero unconditionally every sample (below a small threshold,
  not waiting for exact convergence), rather than relying on the decay
  itself to reach `0`. Re-ran the same trajectory with unconditional flush
  and confirmed it reaches and stays at exact `0`.
- Why this fix: It stops treating "reaches zero" as an emergent property of
  the multiply and makes it an explicit, guaranteed step — which is
  necessary regardless of decay rate, since different rates hit different
  (but equally real) subnormal fixed points.
- Rule of thumb: Any decay/feedback loop that assumes it eventually reaches
  exact zero through repeated multiplication by a constant < 1 is making an
  assumption that's false for some decay rates in IEEE-754 floating point —
  rounding can produce a stable nonzero subnormal fixed point that the
  multiplier never steps below. Treat unconditional flush-to-zero (or an
  explicit threshold cutover) as a TERMINATION correctness requirement for
  any decay loop, not merely a CPU-performance optimization for subnormal
  arithmetic — the two framings look identical in code but only one of
  them is optional.
- Provenance (verified/assumed): Verified first-hand — confirmed
  `0.9 * Number.MIN_VALUE === Number.MIN_VALUE` directly; reproduced a real
  decay trajectory getting permanently stuck at a small nonzero subnormal
  without flush-to-zero, and confirmed unconditional per-sample flush
  resolves it, in a combined real-time-audio sandbox stacking denormal
  handling with a feedback/IIR decay.
- Link: session (dog-game-continue-oc3xqh); combined-audio-realtime
  sandbox, pass2.js/pass3.js (denormal + feedback-decay stack).
- Cited-by: 2026-07-13 · projects/local__sandbox-brain-loop1-denormal-swept.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); scratchpad loop1-denormal-swept-bounce.mjs.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E5 · compatible · no sandbox · session (query brain for "keep training as you were"), sandbox script loop_fm_subnormal2.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-genesis-fm.md#E3 · compatible · no sandbox · Sandbox: `sandbox-genesis-fm-realtime-idle.js`
- Cited-by: 2026-07-20 · projects/local__sandbox-phantom-voice-eats-budget.md#E1 · compatible · no sandbox · session (this conversation, "continue training" — re-verifying the denormal-swept + audio-realtime single-source edge from an unexplored angle); scratchpad `sandbox_phantom_voice_eats_budget.mjs`.

## E1 — combined audio drain count unbounded under burst
- Date: 2026-07-13
- Project: local/sandbox-combined-audio-realtime
- Tags: [dsp][realtime][testing]
- What: Combined a lock-free SPSC ring buffer (already verified real-time
  safe in isolation) with a bursty cross-thread producer. The audio
  callback's "drain the queue until empty" consumer loop is O(1)-per-
  message and allocation-free, yet blew the callback budget by roughly
  1300x when the producer thread queued a 200k-message burst in one
  control-thread tick, versus a version with a hard per-callback drain cap.
- Why built: Isolation testing of the ring buffer only ever fed it a
  steady, modest message rate. This combined test specifically stacked it
  against a producer capable of bursting, to check whether "each operation
  is real-time-safe" implies "the whole loop is real-time-safe."
- Design: Built a 48kHz/128-sample timing harness with a 2,666,667ns
  budget per callback; drove the ring buffer with a steady low rate first
  (fine), then a single 200k-message burst enqueued between two callbacks,
  comparing an uncapped "drain until empty" consumer against a consumer
  capped at a fixed max-messages-per-callback with carryover.
- Got right: Every individual dequeue operation was correctly real-time-
  safe (no malloc, no lock, no blocking syscall) — the ring buffer
  implementation itself had no bug. The failure is entirely in the LOOP
  BOUND, not in what happens inside each iteration.
- Where/why it failed: "Drain until empty" makes the number of loop
  iterations equal to however many messages the OTHER thread happened to
  enqueue — a quantity the callback doesn't control and can't bound by
  making its own per-iteration code cheaper. A burst-capable producer
  (parameter-automation dump, MIDI scrub, network event flood) can hand the
  callback tens or hundreds of thousands of iterations in one call, and
  "each iteration is O(1) and allocation-free" says nothing about the
  COUNT, which is the actual budget-relevant variable here.
- Fix: Cap drained messages per callback to a fixed budget sized to the
  worst burst the system needs to absorb before falling behind, and carry
  any remainder over to the next callback instead of insisting on full
  drain. Re-ran the 200k-message burst with the cap in place and confirmed
  callback duration stayed within budget across the burst, at the cost of
  the queue staying partially full for a few extra callbacks.
- Why this fix: It converts an unbounded, producer-controlled quantity
  (total queued messages) into a bounded, consumer-controlled one (max
  processed per call), which is the same "cap it, don't trust the caller"
  shape as every other real-time-safety fix, just applied to iteration
  count instead of allocation or locking.
- Rule of thumb: A lock-free consumer loop that drains "until empty" is
  only real-time-safe if the producer's burst size is bounded — and a
  cross-thread producer's burst size is usually NOT something the consumer
  controls or can assume about. Every real-time consumer loop needs an
  explicit per-callback iteration cap with carryover, treated as a first-
  class part of the real-time-safety contract, separate from (and in
  addition to) per-message cost being bounded — the two are independent
  budget dimensions and a system can pass every per-message-cost check
  while still failing on iteration count alone.
- Provenance (verified/assumed): Verified first-hand — measured actual
  callback duration under a 200k-message burst both with and without a
  drain cap in a 48kHz/128-sample timing harness (~1300x budget overrun
  uncapped vs. within-budget capped), in a combined real-time-audio
  sandbox stacking the ring buffer with a bursty producer.
- Link: session (dog-game-continue-oc3xqh); combined-audio-realtime
  sandbox, pass1.js/lib/ringbuffer.js/lib/timing.js.
- Cited-by: 2026-07-26 · projects/local__sandbox-anim.md#E6 · compatible · no sandbox · projects/local__sandbox-anim.md, projects/local__sandbox-brain-loop2-frameacc-loopseam.md
- Cited-by: 2026-07-26 · projects/local__sandbox-collision.md#E2 · compatible · no sandbox · projects/local__sandbox-collision.md, projects/local__sandbox-combined-audio-realtime.md
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-audio-realtime.md#E3 · compatible · no sandbox · `scripts/brain-training-audio-queue.mjs`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E8 · compatible · no sandbox · Sandbox: `sandbox-bloom-realtime-drain.js`
- Cited-by: 2026-07-20 · projects/local__sandbox-phantom-voice-eats-budget.md#E1 · compatible · no sandbox · session (this conversation, "continue training" — re-verifying the denormal-swept + audio-realtime single-source edge from an unexplored angle); scratchpad `sandbox_phantom_voice_eats_budget.mjs`.
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E15 · compatible · no sandbox · August-10 sandboxes/loop01_drain_cap_vs_event_count.py
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E2 · incompatible · sandboxes/2026-10-15__capped-drain-delays-lfsr-restore-into-permanent-phase-slip.py · observed RESULT: PASS capped FIFO applies the live-register restore on callback 32 and stays wrong after it (14.2% of later samples, 14.8% overall) with peak 1.000 = ref, dft delta 404.9, crc differs; priority slot 0% at 585 us worst; uncapped 0% a… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 2
