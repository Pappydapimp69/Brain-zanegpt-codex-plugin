# local/sandbox-kernel-motion-animation-loop — lessons

Project: local/sandbox-kernel-motion-animation-loop. Newest first.

---

## E1 — raf beats timers at any refresh rate but its timestamp is its own clock
- Date: 2026-09-28
- Project: local/sandbox-kernel-motion-animation-loop
- Tags: [animation][browser][timing][determinism]
- What: Applied the ideas kernel on driving animation with requestAnimationFrame instead of setTimeout/setInterval, in a deterministic display model. The kernel's claim held, and was much larger than stated on high-refresh displays; its advice to use rAF's own callback timestamp as the elapsed-time source has a boundary where the start time comes from a different clock.
- Why built: brain train gap listed this kernel as unapplied: no memory entry had built against it. seven/E8 already recorded that the rAF timestamp is the frame's scheduled time and can trail the wall clock, which bears directly on the kernel's timestamp advice.
- Design: Vsyncs at k*(1000/hz) ms for 60, 120 and 144Hz over 10 simulated seconds. A timer loop fires at fixed delays of 16 and 17 ms and each update is shown at the vsync after it runs; counted frames that show no new update (a repeated frame) and frames that receive two (a wasted update). rAF delivers one callback per vsync. For the timestamp boundary, an effect's start is captured with performance.now() in an input handler running 2.4 ms after the frame began, while the first rAF callback of that frame reports the frame-start timestamp.
- Got right: Modelling several refresh rates instead of only 60Hz, since the kernel's 16.67ms example hides the dominant case; and checking JavaScript's own Math.pow behaviour in node rather than assuming it.
- Where/why it failed: At 60Hz the timer loop is only mildly wrong: setTimeout(16) wastes an update on 25 of 600 frames and setTimeout(17) repeats 12 of 600. On a 120Hz display the same loops repeat 575 and 612 of 1200 frames, and on 144Hz 815 and 852 of 1440, so a hard-coded 60fps delay halves the motion rate on high-refresh screens. rAF repeats 0 at all three rates. The boundary: with the start from performance.now() and elapsed from the rAF timestamp, the first frame's elapsed is -2.4 ms, progress is -0.008, and an easing of Math.pow(p, 0.5) returns NaN in JavaScript, giving one frame with a NaN position.
- Fix: Drive the loop with rAF, and take the effect's start from the first rAF timestamp it sees (or clamp progress to [0, 1] before easing), so start and elapsed come from one clock.
- Why this fix: The kernel is right that rAF aligns to repaint, but using the rAF timestamp is only safe if every time in the calculation comes from the rAF timeline. seven/E8 showed the timestamp trails performance.now(); combined, the gap produces a negative elapsed exactly when the effect is triggered by input, which is the common case. Taking the start from the first callback removes the second clock instead of guarding against it.
- Rule of thumb: A fixed setTimeout delay tuned for 60fps repeats roughly half of all frames on a 120 or 144Hz display, so drive animation with requestAnimationFrame, and take the effect's start time from the first rAF timestamp rather than performance.now(), because mixing the two clocks gives a negative elapsed on the first frame and Math.pow(negative, 0.5) is NaN.
- Provenance (verified/assumed): VERIFIED first-hand in a deterministic sandbox, cognitive-updates/sandbox_train_gap_b01.py loop 1 in Pappydapimp69/Brain. Observed: setTimeout(16)/(17) repeat 0/12 of 600 frames at 60Hz, 575/612 of 1200 at 120Hz, 815/852 of 1440 at 144Hz; rAF 0 at every rate; first-frame elapsed -2.4 ms with Math.pow(-0.008, 0.5) = NaN, checked in node. Outside this sandbox: real timer jitter and browser background throttling were left unmodelled, and the 2.4 ms handler offset is a chosen value consistent with seven/E8's measurement.
- Composed: ideas:MOTION/animation-loop/requestanimationframe-over-settimeout-for-js-animation/syncs-to-repaint-and-auto-pauses-when-backgrounded, seven/E8
- Link: session 2026-09-28, brain train gap batch 1 loop 1
- Sandbox: sandboxes/2026-09-28__train-gap-b01.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

