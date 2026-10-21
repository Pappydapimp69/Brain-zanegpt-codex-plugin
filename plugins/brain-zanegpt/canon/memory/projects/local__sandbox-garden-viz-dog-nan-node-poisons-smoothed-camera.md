# local/sandbox-garden-viz-dog-nan-node-poisons-smoothed-camera — lessons

Project: local/sandbox-garden-viz-dog-nan-node-poisons-smoothed-camera. Newest first.

---

## E1 — sandbox garden viz dog nan node poisons smoothed camera
- Date: 2026-09-29
- Project: local/sandbox-garden-viz-dog-nan-node-poisons-smoothed-camera
- Tags: [viz][camera][state][testing]
- What: Sandbox showing a single non-finite node position, for only 10 frames, permanently poisons a smoothed live-extents camera, and that filtering the extents input or guarding the camera target each stop it.
- Why built: Untested seam garden-viz + dog: garden-viz#E1 and #E5 compute the camera from live extents every frame, and dog#E3 records a NaN silently poisoning shared state downstream.
- Design: Deterministic model, no RNG: 10 nodes drifting right, camera center and scale follow the extents target with a 0.2 lerp, node 5 has a NaN x for frames 30-39 only, 100 frames; JS min/max NaN semantics emulated; modes none, filter nodes by isFinite, guard camera target.
- Got right: Filtering nodes by isFinite before computing extents, or falling back to the previous camera on a non-finite target, gave 0 NaN camera frames of 100.
- Where/why it failed: With no guard the camera was NaN on 70 of 100 frames, from frame 30 to the end, because the lerp keeps the NaN in its own state and the data recovered at frame 40 but the camera never did.
- Fix: Compute extents only from finite positions, and also reject a non-finite camera target before it enters the smoothed state.
- Why this fix: The smoothing filter is stateful, so a one-frame bad input becomes permanent; the guard must sit before the state, not after the read.
- Rule of thumb: A live-extents camera needs an isFinite filter on its input; recovery of the data does not recover a smoothed camera, so test with a temporary bad node and count NaN frames after it clears.
- Provenance: Verified first-hand by running the Python sandbox (s5.py) and observing 70/100, 0/100 and 0/100 NaN camera frames.
- Composed: sandbox-combined-garden-viz/E1, sandbox-combined-garden-viz/E5, dog/E3
- Link: session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E47 · compatible · sandboxes/2026-10-09__duplicated-default-markup-copy-drifts-only-on-empty-prefs.py · observed RESULT: PASS drift only on empty prefs [True, False, False]; derived 0 mismatches; NaN frames (100, 0); clamp hides drift=True · session_015oqQC6i1dG4qLEBR5kXrdD
