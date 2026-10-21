# local/sandbox-step-transition — lessons

Project: local/sandbox-step-transition. Newest first.

---

## E1 — step transition direction survives rapid nav only if retargeted
- Date: 2026-10-08
- Project: local/sandbox-step-transition
- Tags: [ux][animation][accessibility][state][testing]
- What: A deterministic simulated-clock model of a click-through stepper (slide transition, ease-out, keyboard/next/back input, live-region announce, forward-blocked rule, reduced-motion switch) used to test whether the step-transition kernel's "short, directional, instant under reduced motion" rule survives rapid input.
- Why built: The kernel states the rule for a single clean step change, but real users hold the arrow key or reverse mid-slide; the untested question was whether "directional" still holds then.
- Design: Time is a simulated clock (60 and 30 fps), motion is elapsed/duration eased, never a per-frame factor. Two variants: retarget (new transition starts from the current visual position) and naive restart (new transition starts from the old rest slot). Metrics: frames moving against nav direction, position teleport at each input, settle time, announce list, lag after the final press.
- Got right: Single forward step at 250ms is monotone in the nav direction at both frame rates (0 bad-direction frames) and settles at 250ms (60fps) and 267ms (30fps), unlike a fixed per-frame factor which takes 733ms vs 1467ms. Reduced motion yields 0 intermediate frames with the announce intact. Forward-blocked/back-free produced announces [1,2,0] for an attempted +5 jump. One announce per swap on a fwd,fwd,back burst gave [1,2,1].
- Where/why it failed: The BREAK case, fwd then fwd then back at 100ms spacing, failed for naive restart: each reversal teleports the slide (0.296 and 0.216 step-units in one frame, versus 0.000 for retarget), so the motion briefly points the wrong way and the direction cue the kernel relies on is lost. Separately, a 600ms duration leaves 613ms of visual lag after the last of five key-repeat presses vs 263ms at 250ms, matching the kernel's cost warning.
- Fix: Start every new transition from the current interpolated position (retarget) and keep the duration in the 200-300ms band; announce once per state change, not per animation.
- Why this fix: Retargeting makes the displacement continuous at the input frame (0 teleport), so direction is always the sign of the latest input; the 250ms cap bounds lag to about one duration however fast keys repeat.
- Rule of thumb: "Directional, 200-300ms, instant when reduced" is necessary but not sufficient: the transition must also be interruptible by retargeting from the current position, otherwise the first rapid reversal teleports the slide and the direction cue inverts (0.296 vs 0.000 in this model).
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox (RESULT PASS, 5 scenarios, 2 frame rates). Tolerances are for one simulated frame; real browser rendering and the vestibular-risk claim itself were not tested here.
- Composed: ideas:UX/step-navigation/step-transition-directional-not-decorative, ideas:UX/accessibility/step-content-keyboard-and-live-region, ideas:UX/step-navigation/back-free-forward-blocked, sandbox-anim/E3, sandbox-combined-brain-viz-growth/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-08__step-transition-direction-survives-rapid-nav-only-if-retargeted.py
- Prediction: Before the first run: naive restart would show a teleport above 0.05 units on reversal while retarget stays at 0; single steps would be monotone and settle within one frame of 250ms; per-frame factor settle time would differ by more than 1.8x between 60 and 30 fps.
- Observed: RESULT: PASS 5 scenarios; teleport at input: retarget 0.000 vs naive 0.296. First run had two harness errors of mine (settle threshold 0.01 settled early; max-jump metric dominated by normal easing speed), fixed to measure exact settle and teleport-at-input; claim unchanged.
- Scenarios: 1) single forward step at 60 and 30 fps; 2) per-frame-factor contrast; 3) BREAK: fwd,fwd,back burst at 100ms, retarget vs naive; 4) reduced motion; 5) forward-blocked jump attempt; 6) key-repeat burst at 250ms vs 600ms duration.
- Link: brain train auto pass 1 (kernel mode)
- Audited: 2026-10-12 · modeled · Read the entry and re-ran its stored sandbox (it ends in a PASS line). The model computes its numbers on a simulated clock, and the retarget-versus-naive contrast is real arithmetic. But the 0.296 teleport is built in: the naive variant is defined as restarting from the old rest slot, so a jump on reversal follows by definition rather than being discovered. The claim is about real stepper UIs (browser animation, key-repeat, screen-reader live regions) and only a hand-written model of them was tested, so I rate it modeled, not audited. The rule is sound as design guidance but no real browser or announce behaviour was exercised. · brain train auto audit session 2026-10-12 loop 2; session_01QoYzipjYSp8DTBoAoj5Bdh
