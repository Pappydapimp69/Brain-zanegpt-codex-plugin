# local/sandbox-collision — lessons

Project: local/sandbox-collision. Newest first.

---

## E2 — substep burst vs drain cap
- Date: 2026-07-26
- Project: local/sandbox-collision
- Tags: [physics][dsp][realtime][gamedev][testing][state]
- What: Two recorded lessons, composed: - `sandbox-collision/E1` — discrete
  overlap checks tunnel once per-frame travel exceeds obstacle thickness; fix
  with swept or sub-stepped collision. - `sandbox-combined-audio-realtime/E1`
  — a drain-until-empty SPSC consumer is real-time-safe only if the producer's
  burst is bounded; cap messages drained per callback with carryover. The
  claim tested: sub-stepping (fix #1) turns collision into a per-sub-step
  producer, so applying it can violate the bounded-burst precondition fix #2
  depends on.
- Why built: Two recorded lessons were composed: sandbox-collision#E1
  (discrete overlap checks tunnel once per-frame travel exceeds obstacle
  thickness; fix with sub-stepped collision) and
  sandbox-combined-audio-realtime#E1 (a drain-until-empty consumer is
  real-time-safe only if the producer's burst is bounded). The claim tested:
  does applying the sub-stepping fix silently violate the bounded-burst
  precondition the audio fix depends on?
- Design: A deterministic sandbox (`sb-collision-audio.mjs`, fixed dt=1/60, no
  RNG) swept collision speed as the sole varied parameter and counted sub-step
  count against collision events emitted, for both a pass-through crossing and
  a sustained sliding contact.
- Got right: The intuitive worry — fast object, many sub-steps, many redundant
  sounds — does NOT happen for pass-through collisions: an object crossing a
  thin band spends a bounded number of sub-steps inside it by construction
  (sub-step size is chosen relative to that same thickness), so events emitted
  stay flat (2, 3, 3, 3) even as sub-step count scales hugely with speed (3 at
  v=33, 80 at v=1200, 400 at v=6000).
- Where/why it failed: Half the claim was refuted, and the refutation is the
  useful part. **Pass-through collisions are NOT speed-proportional.**
  Sub-step COUNT scales with speed (3 steps at v=33, 80 at v=1200, 400 at
  v=6000) but events emitted do not: 2, 3, 3, 3. An object crossing a thin
  band spends a bounded number of sub-steps inside it by construction, because
  sub-step size is chosen relative to that same thickness. The obvious worry —
  "fast object, many sub-steps, many sounds" — does not happen. **Sustained
  contact IS speed-proportional.** An object sliding ALONG a wall face is
  inside the overlap band for *every* sub-step of every frame, so the
  per-frame burst equals the sub-step count: worst frame 2 at v=30, 20 at
  v=300, 200 at v=3000. Against a cap of 8 that is a 25x single-frame overrun,
  from one continuous physical contact producing zero new collisions. So the
  burst bound is a function of contact DURATION times sub-step count, not of
  how many distinct collisions occur. Reasoning about "how many things hit
  this frame" — the natural way to bound it — measures the wrong quantity.
  **And the cap does not save you; it relocates the failure.** Capping drains
  with carryover bounds CPU per callback but not the queue. At 4/frame and
  8/frame against a cap of 8 the queue drains. At 12/frame it diverges: 2400
  messages backlogged after 10 simulated seconds, which at 8 drained per frame
  is 5.0 seconds of queued audio latency. At 40/frame, 19200. A sound effect
  fires five seconds after its collision — arguably worse than the dropout the
  cap was added to prevent, and it presents as a memory leak, not an audio
  bug.
- Fix: Deduplicate at the PRODUCER, per contact rather than per sub-step: emit
  on the enter transition (not-touching -> touching) and suppress while the
  contact persists. That restores a bound tied to distinct contacts, which is
  what the consumer's burst assumption actually meant. Keep the drain cap as a
  backstop, but treat sustained carryover > 0 as an alarm, not a working
  state.
- Why this fix: Capping is a consumer-side mitigation for a producer-side
  defect. Once the producer's rate can exceed the cap indefinitely, no
  consumer-side policy is sufficient — the choices are drop, diverge, or fix
  the rate. Enter-transition emission is also what the domain means: one bump,
  one sound.
- Rule of thumb: When a fix converts a per-frame operation into a per-sub-step
  one, audit every CONSUMER downstream of it — the fix silently multiplies the
  event rate of anything it feeds, and the multiplier is whatever made
  sub-stepping adaptive. Bound event bursts by contact *duration* x step
  count, not by collision count; sustained contact, not high speed, is the
  pathological case, and it is the one nobody writes a test for because no new
  collision is occurring. Any "cap it with carryover" mitigation needs a
  stated maximum producer rate to be a fix at all. Below the cap it works;
  above it, it converts a CPU spike into unbounded latency and memory growth —
  a different failure wearing a fix's clothes. Assert the queue returns to
  empty, not merely that the callback stayed under budget.
- Provenance (verified/assumed): Verified first-hand — deterministic sandbox
  (`sb-collision-audio.mjs`, fixed dt=1/60, no RNG, speed as the swept
  parameter), numbers below are observed output.
- Composed: sandbox-collision/E1, sandbox-combined-audio-realtime/E1
- Link: projects/local__sandbox-collision.md,
  projects/local__sandbox-combined-audio-realtime.md
- Cited-by: 2026-09-25 · projects/local__sandbox-hitbox-window.md#E2 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E1 — discrete collision tunneling at high speed
- Date: 2026-07-05
- Project: local/sandbox-collision
- Tags: [physics][gamedev][state]
- What: A per-frame "does my current position overlap this obstacle?" collision check silently fails for fast-moving objects: once an object's per-frame travel distance exceeds the obstacle's thickness, there exists no single frame where the object's position is actually inside the obstacle — it's on one side before the step and past it after, with the "inside" moment falling entirely between frames. The object tunnels through with zero collision events.
- Why built: A breakout/pong-style ball-vs-paddle sandbox, to verify how much speed it takes before a naive discrete check fails.
- Design: Compare a naive check (`is new_position inside obstacle bounds?`) against a swept check (`does the segment from old_position to new_position cross the obstacle's span?`) at two speeds against a fixed-thickness paddle.
- Got right: At a "normal" speed (per-frame travel well under the obstacle's thickness), both checks agree — the bug is invisible during ordinary testing, which is exactly why it survives into shipped games/physics engines undetected until someone or something moves fast enough.
- Where/why it failed: The naive check only ever asks "where am I now," never "where did I come from and did I cross anything on the way here." Above the speed/thickness threshold, that question structurally cannot see the collision.
- Fix: Swept/continuous collision — check the traveled segment (or a ray/capsule along the motion) against the obstacle each frame, not just the endpoint. A cheaper partial fix: sub-step a fast frame into N smaller pieces so no single piece's travel exceeds the thinnest obstacle in the scene.
- Why this fix: Swept collision directly asks the right question ("did my path cross this obstacle") instead of an endpoint snapshot that can straddle the obstacle on both sides without ever landing inside it.
- Rule of thumb: Any collision system will silently tunnel for objects whose `speed * dt` can exceed the thinnest obstacle in the scene (bullets, fast balls/projectiles, a game that lets frame-rate or speed scale up) — don't wait to discover this from a bug report. Deliberately test at the exact boundary speed (`speed * dt ≈ thickness` and a bit above) and confirm your collision check still fires; a discrete/endpoint-only check will not.
- Provenance (verified/assumed): Verified first-hand — same paddle (3-unit thickness) and dt (1/60s) tested at two ball speeds. At 60 units/s (1 unit/frame, well under thickness) naive and swept both correctly detected the hit. At 400 units/s (~6.7 units/frame, over 2x the thickness) the naive endpoint check reported no collision at all while the swept segment check still correctly detected it (segment [96.67, 103.33] crossing paddle span [98.5, 101.5]).
- Link: session https://claude.ai/code/session_01WRnetMwso7jF8ERtXN88zT ; sandbox sim8_tunneling.mjs
- Cited-by: 2026-07-13 · projects/local__sandbox-brain-loop1-denormal-swept.md#E1 · compatible · no sandbox · session (dog-game-continue-oc3xqh); scratchpad loop1-denormal-swept-bounce.mjs.
- Cited-by: 2026-07-18 · projects/local__sandbox-brain-loop1-denormal-swept.md#E2 · compatible · no sandbox · session (this conversation, "brain train zen groups" → clarified to bare `brain train`); scratchpad `sandbox_denormal_swept.mjs`.
- Cited-by: 2026-07-26 · projects/local__sandbox-collision.md#E2 · compatible · no sandbox · projects/local__sandbox-collision.md, projects/local__sandbox-combined-audio-realtime.md
- Cited-by: 2026-09-25 · projects/local__sandbox-hitbox-window.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-25 · projects/local__sandbox-hitbox-window.md#E2 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E36 · compatible · sandboxes/2026-10-09__semi-implicit-euler-stability-bound-and-fps-dependence.py · observed RESULT: PASS explicit=6.91e+56 semi=1.0553; semi bounded but 200x at w*dt=1.99, 1.6e71 at 2.01, inf at 2.5; fps drift 0.019; tunnel=True (first run FAIL on thresholds 1.05/0.05/bound<2, corrected to what was measured). · brain train auto pass 1 (loop 1); session_01QXDSckzV3bvegjZqBF6sPy
- Audited: 2026-10-13 · pass · The entry has no stored sandbox, so I audited its recorded provenance numbers by recomputation: 400 units/s at dt 1/60 is 6.67 units per frame, over twice the 3 unit paddle, so a one-point endpoint check can straddle it, and the quoted segment [96.67, 103.33] does overlap the span [98.5, 101.5] while 60 units/s (1 unit per frame) stays under the thickness. The claim follows from geometry rather than an assumed answer, and the two speeds computed different outcomes for the naive and swept checks. The weakness is scope: the Rule of thumb asks for a test at the exact boundary speed (speed*dt about equal to thickness), but only two speeds far from it were run, and the word any collision system is asserted from one hand-written 1D model, not an engine. The narrow geometric claim holds; the boundary and real-engine parts are untested. · scheduled brain train session, loop 1 pass 3 audit; session_01DiPNzPzfsHcE8oDezvZY3n
- Reverified: 2026-10-13 · pass · sandboxes/2026-10-13__rebuild-tunneling-boundary-speed-dt-vs-thickness.py · observed RESULT: PASS endpoint misses at ratios 0.25/0.5/1.0/1.01/1.5/3/7 = [0, 0, 0, 1, 17, 37, 50]; swept misses all 0; 2D diagonal endpoint-inside=False swept=True · Built my own sandbox from the claim alone: a 1D point against a wall of thickness 2 swept over 7 step-to-thickness ratios and 50 start phases each, plus a 2D diagonal path against a thin box using a segment-versus-box swept test. Endpoint-only checks missed 0/50 at ratios 0.25, 0.5 and 1.0, 1/50 at 1.01, 17/50 at 1.5, 37/50 at 3 and 50/50 at 7, while the swept check missed 0 everywhere, and the 2D diagonal had no endpoint inside the box yet the swept test hit it. The rule holds, with one refinement: at exactly speed times dt equal to thickness an inclusive endpoint check still never missed, so the failure starts just above the boundary and grows with phase, rather than every case above it failing. The entry's own sandbox (sim8_tunneling.mjs) is not stored in sandboxes/, so I could not compare fixtures; mine differs by using a 1D point with phase sweeps and a 2D segment test, and it did not use that file. · scheduled brain train session, 2026-10-13, rebuild pass; session_01KgwUVJ8YiFpBjfevwrK7fS
