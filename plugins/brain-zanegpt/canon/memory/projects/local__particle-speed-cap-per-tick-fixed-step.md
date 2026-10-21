# local/particle-speed-cap-per-tick-fixed-step — lessons

Project: local/particle-speed-cap-per-tick-fixed-step. Newest first.

---

## E1 — particle speed cap is per tick and only guards a fixed step
- Date: 2026-10-15
- Project: local/particle-speed-cap-per-tick-fixed-step
- Tags: [physics][simulation][testing]
- What: Composed demo-disc E1 (cap a particle's speed under one radius per tick or liquid tunnels through
  thin walls) with brain E119 (semi-implicit Euler is bounded only at a fixed dt with dt times omega
  under 2), on a particle falling onto a 4 px wall with a penalty-spring contact, under steady and
  hitching frame rates.
- Why built: Demo-disc's cap is stated per tick, but a browser game that steps once per frame has a tick as long
  as the frame; whether the cap still protects it, and whether one accumulator fixes both lessons'
  failures together, was untested.
- Design: Exact, no rng. Radius 7, gravity 2000 px/s^2, wall [96, 100], spring with omega times dt_fixed = 1
  at 1/60 s, speed cap 0.9 radius per fixed tick. Frame schedules: 60, 30 and 10 fps and 60 fps with
  one 250 ms hitch. One semi-implicit step per frame with dt = frame time, against fixed 1/60 steps
  through an accumulator capped at 15 steps per frame. Measured tunnelling and post-landing bounce
  peak.
- Got right: The fixed-step accumulator never tunnelled at any frame rate or through the hitch, and matched the
  60 fps run; one step per frame at 60 fps was also clean. Stepping with the frame time tunnelled at
  30 fps, 10 fps and on the single 250 ms hitch.
- Where/why it failed: I expected the variable step to explode as well (dt times omega 2 to 15); it never did, because the
  speed cap clamps velocity and so caps the energy a too-stiff spring can inject, but the same cap is
  in px per second, so a long frame moves the particle several radii in one step and it passes
  straight through the wall. Tunnelling, not instability, is the visible failure.
- Fix: Run the particle sim on a fixed step through an accumulator (with a max-steps clamp for hitches) and
  state the speed cap in distance per fixed step; never step once per frame with the frame time.
- Why this fix: A per-tick cap only means one radius when the tick is fixed; the accumulator makes both demo-disc's
  cap and E119's stability bound hold at every frame rate, and one hitch is enough to break a per-
  frame step.
- Rule of thumb: A particle speed cap of one radius per tick guards only a fixed step: stepping with the frame time
  tunnelled a 4 px wall at 30 fps, 10 fps and on one 250 ms hitch, while fixed 1/60 steps via an
  accumulator never did; the cap also hid the spring's instability, so watch for tunnelling, not blow-
  ups.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry on a 1-D scene; demo-disc's real particle engine
  was not run.
- Composed: pappydapimp69__demo-disc/E38, pappydapimp69__brain/E119
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__particle-speed-cap-is-per-tick-and-only-guards-a-fixed-step.py
- Prediction: fixed+accumulator never tunnels or explodes; variable dt fine at 60 fps, tunnels at 10 fps and on
  the hitch, and explodes or tunnels from 30 fps down.
- Observed: RESULT: PASS 4/4; fixed+accumulator clean at all rates; variable dt: 30fps (True, False), 10fps
  (True, False), hitch (True, False) (tunnelled, exploded) - no explosion anywhere, the cap clamps it
- Scenarios: 1) 60 fps; 2) 30 fps (dt omega 2); 3) 10 fps; 4) built to BREAK a 60 fps game: one 250 ms hitch (it
  tunnelled); each with per-frame and fixed-step integration
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 2 (edge demo-disc + brain), 2026-10-15
- Audited: 2026-10-15 · pass · Read the entry and re-ran its stored sandbox (RESULT: PASS 4/4, same numbers). The model computes the result: it integrates a semi-implicit step with a penalty spring and a px/s velocity clamp, and tunnelling falls out of the step length (30 fps, 10 fps and the 250 ms hitch end near y -1100 to -1200), nothing is assumed. The tested scenes cover the Rule of thumb, including the claim that the cap hid the spring instability (no run exceeded its start height). The rule is a generic integration pattern, not a claim about a real library, so not `modeled`. Two limits, neither a fail: each schedule ran one start phase and one hitch position, so it shows tunnelling can happen, not how often (a hitch that lands before contact or while resting can differ); and the Composed field cites pappydapimp69__demo-disc/E38, which is the step(n) clock-hook lesson, while the What describes the particle speed cap, which is pappydapimp69__demo-disc/E38, so the graph edge points at the wrong demo-disc entry. · https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC (brain train auto pass 3)
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E16 · compatible · sandboxes/2026-10-15__pin-puzzle-speed-cap-only-stops-tunneling-under-a-fixed-step-accumulator.py · observed iteration 1 RESULT: FAIL (hitch 0/100: it fell after the crossing). Iteration 2 RESULT: PASS cap holds at fixed 60 Hz (0) and under the accumulator (0, 0) but raw 30 fps tunnels 33/100 and one 1/20 s hitch 167/1000 when swept over its posi… · https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC (brain train auto pass 2)
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__speedcap-rebuild-own-fixture.py · observed RESULT: PASS fixed step tunnelled 0 times in every case: True; variable dt tunnelled at 15 fps 8/40; 10 fps 17/40; one 200 ms hitch at 60 fps (break) 34/120 · Built blind from the claim with my own fixture: radius 2.5 (original 7), wall 3 px (original 4), gravity 1500 (original 2000), omega 60 rad/s with light damping, speed cap exactly one radius per 60 Hz tick, contact only while the centre is inside the wall band, and frame rates 60/30/15/10 plus a 200 ms hitch (original 60/30/10 and 250 ms). Differs in scenarios too: a first run with one hitch at a fixed time tested nothing (the particle had not reached the wall), so iteration 2 sweeps 40 start heights per frame rate and the hitch at all 120 frames of the first 2 s, instead of single runs. Core rule reproduced: fixed 1/60 steps via an accumulator never tunnelled in any case (0 of 280), variable dt tunnelled at 15 fps (8/40), 10 fps (17/40) and on the hitch (34/120). Where they differ: in my fixture 30 fps never tunnelled (step 5 px against an 8 px band) where the original's did, so the 30 fps result depends on the band width versus cap times dt, not on the rule; and tunnelling under variable dt is phase-dependent, which single-run scenarios hide. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
