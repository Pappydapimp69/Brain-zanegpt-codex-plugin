# local/sandbox-brain-loop2-frameacc-loopseam — lessons

Project: local/sandbox-brain-loop2-frameacc-loopseam. Newest first.

---

## E1 — loop2 frame accumulator drain loop fixes event undercounting too
- Date: 2026-07-13
- Project: local/sandbox-brain-loop2-frameacc-loopseam
- Tags: [animation][dsp][testing]
- Composed: local__sandbox-combined-game-loop/E2, local__sandbox-anim/E5
- What: `frame-accumulator-must-while-drain-and-subtract-the-remainder` was
  previously only verified against replay-determinism (identical tick
  counts across frame schedules). Re-verified it against
  `loop-seam-is-a-value-and-slope-discontinuity` instead (a genuinely new
  partner for both) and found the SAME drain-while-loop prescription is
  also required for a different reason: correctly counting discrete
  threshold-crossing events, not just avoiding numeric drift. Checking a
  loop-seam crossing once per frame off the frame's summed advance
  undercounts the true crossing count by up to N-1 when a lag spike drains
  N sub-steps in one frame (measured: 3 true crossings, only 1 detected, at
  a 10-tick spike) — even though the final playback POSITION is identical
  either way.
- Why built: Both kernels were single-source. Pairing them tests whether the
  frame-accumulator kernel's existing "drain in a while loop, step() per
  sub-step" fix generalizes beyond the numeric-drift problem it was
  originally verified for, using a real discrete-event scenario (an
  audio loop-seam click-mitigation trigger) it had never been checked
  against.
- Design: A deterministic sandbox with a fixed loop length (8 position
  units) and fixed per-tick playback advance (3 units). Compared three
  counters across several drained-tick counts (1, 2, 3, 4, 6, 8, 10): (a) a
  naive frame-level check — sum the frame's total advance, then test once
  whether the summed position wrapped; (b) a per-tick check — advance and
  test the wrap condition once per sub-step inside the drain loop, matching
  this kernel's own prescribed shape; (c) an independent ground-truth
  crossing counter computed directly from `floor(pos/L)` deltas per tick.
- Got right: All three methods agree exactly on the final playback
  POSITION after the frame (verified identical `finalPos` in every test
  case) — the bug is purely in the event COUNT, not in the underlying
  state, which is easy to miss if you only check position correctness.
- Where/why it failed: A frame-level check collapses "how many times did we
  cross the seam" into a single yes/no ("did the summed advance exceed one
  loop length") regardless of how many multiples of the loop length were
  actually traversed. At 6 drained ticks the true crossing count is 2 but
  the naive check reports 1; at 10 ticks the true count is 3 but the naive
  check still reports 1 — the naive check structurally cannot report more
  than 1 regardless of how large the lag spike gets, because it only asks
  "did we wrap" rather than "how many times."
- Fix: Detect and count the threshold-crossing event INSIDE the drain
  loop, once per sub-step — exactly the loop shape the frame-accumulator
  kernel already prescribes for numeric-drift reasons
  (`while (acc >= step) { acc -= step; ... }`), just also using that same
  per-iteration boundary to fire/count discrete events. Verified the
  per-tick method matched the independent ground-truth crossing count
  exactly across every tested spike size (1 through 10 ticks).
- Why this fix: The frame-accumulator kernel already establishes that a
  frame can represent multiple sub-steps and that per-step processing is
  required for correctness — this shows that requirement extends to ANY
  discrete event derived from the stepped quantity (a loop-seam crossing,
  and by the same structure a collision or achievement trigger), not only
  to the continuous position/velocity state the kernel was originally
  verified against.
- Rule of thumb: When a fixed-timestep accumulator drains multiple
  sub-steps in one frame (a lag spike), any discrete threshold-crossing
  event tied to the stepped quantity must be detected and counted per
  sub-step inside the drain loop — never once per frame off the frame's
  aggregate advance. The final continuous state can be completely correct
  while the discrete event count is silently wrong by up to N-1 for N
  drained sub-steps, so a test that only checks final position/state will
  not catch this; test event COUNT under an explicit multi-tick lag spike.
  This generalizes the accumulator kernel's existing drain-while-loop fix
  to cover discrete-event counting, not just continuous-state drift — a
  reinforcing relationship, not a conflict, between the two source
  kernels.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox
  across 7 drained-tick counts (1, 2, 3, 4, 6, 8, 10); recorded exact
  disagreement between the naive frame-level event count and the
  independently-computed ground-truth crossing count (0 missed at 1-4
  ticks where at most one true crossing occurs, 1 missed at 6 ticks, 2
  missed at 8 and 10 ticks), while final position matched across all
  methods in every case.
- Link: session (dog-game-continue-oc3xqh); scratchpad
  loop2-frameacc-loopseam.mjs.
- Cited-by: 2026-07-26 · projects/local__sandbox-anim.md#E6 · compatible · no sandbox · projects/local__sandbox-anim.md, projects/local__sandbox-brain-loop2-frameacc-loopseam.md
- Cited-by: 2026-07-26 · projects/local__sandbox-combined-game-loop.md#E4 · compatible · no sandbox · projects/local__sandbox-combined-game-loop.md, projects/local__sandbox-brain-loop2-frameacc-loopseam.md
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E15 · compatible · no sandbox · August-10 sandboxes/loop01_drain_cap_vs_event_count.py
