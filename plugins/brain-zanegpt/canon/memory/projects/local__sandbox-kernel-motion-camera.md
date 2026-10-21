# local/sandbox-kernel-motion-camera — lessons

Project: local/sandbox-kernel-motion-camera. Newest first.

---

## E2 — an instant camera snap is only as current as the position it reads
- Date: 2026-09-28
- Project: local/sandbox-kernel-motion-camera
- Tags: [camera][animation][correctness][gamedev]
- What: Applied the ideas kernel that a third-person camera's obstacle pull-in should snap in instantly and ease out, because raw recompute flickers at an edge and a fast lerp clips geometry for several frames. All three reproduced, and the snap is only safe if the camera updates after the player moves.
- Why built: brain train gap listed the kernel as unapplied. sandbox-kernel-motion-camera already holds the batch 1 camera-clamp lesson; the pull-in had not been built.
- Design: A camera 5 units back, required to sit at 2 when the player is behind a pillar edge at x=0. Three paths of 600 frames: hovering at the edge with seeded noise of plus or minus 0.05, a clean sweep past it, and six walks into cover. Three controllers: raw recompute, lerp both ways (0.6 in, 0.08 out), and snap in with a 0.08 ease out. A clip is a frame where the camera sits farther out than that frame's required distance. The snap controller was then run with the camera reading the player's position from after and from before the player's move that frame.
- Got right: Running the update-order variant. With the camera after the player, snap-in shows 0 clips everywhere and reads as unconditionally safe.
- Where/why it failed: Hovering at the edge, raw recompute moved the camera 1.595 units per frame on average against 0.221 for snap-in, about 7x; on the clean sweep all three moved 0.010, so a sweep test hides it. Lerping both ways clipped 309 frames hovering, 23 sweeping and 138 walking in; snap-in clipped 0 in all three. With the camera reading the player's position before the move, snap-in clipped 6 frames on the walk-in path, one on each entry into cover.
- Fix: Snap in and ease out, and run the camera's obstruction check after the player's movement for the frame (or against the position about to be rendered), then test the no-clip invariant directly on walk-in and hover paths.
- Why this fix: A snap removes the lerp's transient, but it can only be as current as the position it reads; a one-frame-old position is a one-frame clip on every entry into cover.
- Rule of thumb: Snap-in, ease-out camera pull-in fixes both the edge flicker (1.595 vs 0.221 units per frame hovering) and the lerp's clipping (309 frames hovering, 138 walking in, vs 0), but only when the camera updates after the player moves; reading the pre-move position clipped once on each of 6 entries into cover.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b05.py loop 25 in Pappydapimp69/Brain, deterministic seeded noise. Observed: mean per-frame movement 1.595/0.211/0.221 hovering and 0.010 for all sweeping; clips 309/23/138 for lerp-both and 0 for snap-in; 6 clips for snap-in when reading the pre-move position. The flicker ratio here is 7x, against the kernel's 10x from a different setup.
- Composed: ideas:MOTION/camera/obstacle-pull-in-asymmetric-damping/instant-snap-in-eased-release-not-a-fast-lerp
- Link: session 2026-09-28, brain train gap batch 5 loop 25
- Sandbox: sandboxes/2026-09-28__train-gap-b05.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E1 — camera clamp must be unsmoothed and measured on both axes
- Date: 2026-09-28
- Project: local/sandbox-kernel-motion-camera
- Tags: [camera][viewport][layout][animation]
- What: Applied the kernel that a camera framing dynamically appearing content must hard-clamp its eased zoom schedule to the scale that keeps every visible item on screen. Both of its conditions, clamping at all and not smoothing the clamp, held with measured costs, and the clamp itself has an orientation boundary.
- Why built: brain train gap listed this kernel as unapplied. brain/E34 already recorded that viewport-derived projection constants must use min(W, H), and the clamp computes exactly such a constant.
- Design: 24 items spawn over 80% of a 12 s animation at fixed radii, every fifth on an outer ring (radius 1.9) that appears early. Scale eases from 2.2 to 0.45 on a cosine schedule at 60fps. Counted item-frames where an item leaves the frame for: schedule only; schedule hard-clamped to the per-frame fit; the clamp followed by exponential smoothing at 0.12 per frame; and a clamp whose fit uses frame height only. Run at 16:9 and 9:16.
- Got right: Testing both orientations, which is the kernel's own explanation of why its original bug hid: testing only at the design's base resolution.
- Where/why it failed: Schedule only: 4852 clipped item-frames at 16:9 and 5080 at 9:16. Hard clamp: 0 at both. Smoothing the clamp at 0.12 per frame brought back 172 and 273 clipped item-frames, each clip lasting the few frames the follower takes to catch a new outer-ring item. A clamp computed from height alone gave 0 at 16:9, where height is the short axis, and 958 at 9:16, where it is the long one.
- Fix: Clamp scale to the minimum over visible items of min(halfW/|x|, halfH/|y|), apply it with no smoothing, and let only the dramatic schedule ease.
- Why this fix: The clamp is a correctness bound, so any lag on it is a window of known-wrong frames; smoothing belongs to the aesthetic part. The per-axis form is brain/E34's rule applied to the clamp: a fit derived from one axis silently assumes the orientation it was tested in, and here that reintroduced 958 of the clips the clamp exists to remove.
- Rule of thumb: A content-fit clamp on a camera's zoom must be applied with zero smoothing and computed on both axes: smoothing it at 0.12 per frame re-clipped 172 to 273 item-frames, and a height-only fit was perfect in landscape but clipped 958 item-frames in portrait.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b01.py loop 2 in Pappydapimp69/Brain, deterministic, item layout from a seeded splitmix64. Observed clipped item-frames at 16:9 and 9:16: schedule-only 4852/5080, hard clamp 0/0, smoothed clamp 172/273, height-only clamp 0/958. Not swept: other smoothing rates and item layouts; the counts depend on this layout, the zeros do not.
- Composed: ideas:MOTION/camera/clamp-to-live-content-not-a-progress-schedule/a-schedule-doesnt-know-whats-actually-on-screen, brain/E34
- Link: session 2026-09-28, brain train gap batch 1 loop 2
- Sandbox: sandboxes/2026-09-28__train-gap-b01.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-presentation-layout.md#E1 · compatible · sandboxes/2026-10-09__per-screen-word-budget-is-set-by-the-shortest-viewport.py · observed RESULT: PASS 9/9 checks; budgets 319/242/141/105/235 words; 100 words fits 375x560 with 8px slack (prediction wrong there), cliff at 106; 20px body budget 68; 86 false passes at 412x900; centered gap 290px vs 0. · brain train auto pass 1 (kernel mode)
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E87 · compatible · sandboxes/2026-10-10__bbox-overlap-necessary-not-sufficient-exact-sat-grid.py · observed RESULT: PASS 6936 bars: bbox false-neg 0, false-pos 1392/3452 (40.3%); vertex-in-frame misses 1318 true overlaps; centre-fit misses 1460 and wrongly accepts 0; shared edge claimed {'incl': 2, 'excl': 0, 'half': 1} · brain train auto loop 2 pass 1 (kernel mode); session_01LphKr4r2NDaVJxz3d1yx7B
