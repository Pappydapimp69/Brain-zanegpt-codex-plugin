# local/sandbox-kernel-vfx-weather — lessons

Project: local/sandbox-kernel-vfx-weather. Newest first.

---

## E1 — evenly spaced phases in spawn order make a travelling wave
- Date: 2026-09-28
- Project: local/sandbox-kernel-vfx-weather
- Tags: [vfx][animation][particles][rendering]
- What: Applied the ideas kernel that a shared-clock wind sway makes every particle breathe in sync and that a per-particle phase of 2*pi*i/N fixes it without randomness. Global sync dropped to zero as claimed, but when particle index follows spawn position the same phases make neighbours move together as a travelling wave.
- Why built: brain train gap listed the kernel as unapplied. sandbox-weather-vfx/E1 covers the rendering approach, not the sway.
- Design: 200 particles spawned left to right, so index order is x order, swaying as sin(1.3t + phase) over 400 frames. Four phase assignments: all 0, 2*pi*i/N by index, 2*pi*i/N over a shuffled index, and 2*pi times the fractional part of i x 0.618. Measured global sync (the mean absolute share of particles on the same side) and the correlation between the offsets of particles adjacent in x.
- Got right: Measuring neighbour correlation, not only the kernel's global sync score, which cannot see spatial structure.
- Where/why it failed: A shared phase gave global sync 1.000 and neighbour correlation +1.000. Evenly spaced phases by index gave global sync 0.000 but neighbour correlation still +1.000, because phase then rises steadily with x and the field sways as one travelling wave. The same phases over a shuffled index gave 0.000 and +0.001. Golden-ratio spacing gave 0.005 and -0.737, neighbours moving in opposite directions, a regular zig-zag.
- Fix: Assign phases from a scrambled index (a fixed permutation or a hash of the particle id), so phase is uncorrelated with position; keep it deterministic.
- Why this fix: Visible synchrony is about what neighbours on screen do. Evenly spaced phases remove global synchrony, but if spawn order follows position they create spatial coherence instead.
- Rule of thumb: Per-particle phase 2*pi*i/N removes global sway sync (1.000 to 0.000) but, when index follows spawn position, neighbours stay fully correlated (+1.000) as a travelling wave; scramble the index (neighbour correlation +0.001), and avoid golden-ratio steps, which gave a regular zig-zag (-0.737).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b07.py loop 31 in Pappydapimp69/Brain, deterministic. Observed: global sync 1.000/0.000/0.000/0.005 and neighbour correlation +1.000/+1.000/+0.001/-0.737 for shared, index-ordered, shuffled and golden-ratio phases. How visible each pattern is to a viewer was not measured.
- Composed: ideas:VFX/weather/per-particle-phase-offset-decorrelates-shared-wind-drift/breaks-the-synchronized-wave-artifact
- Link: session 2026-09-28, brain train gap batch 7 loop 31
- Sandbox: sandboxes/2026-09-28__train-gap-b07.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E387 · compatible · sandboxes/2026-10-08__half-open-bucketing-of-phase-offset-particles-and-pip-vertices.py · observed RESULT: PASS half-open gives one bucket/edge per boundary item (12 vs inclusive 15; PIP wrong incl 2 half 0); float edge compare mismatched exact in 18/295 cases. Inclusive was 15 not 16 (prediction partly wrong). · brain train auto pass 1 (kernel)
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E388 · compatible · sandboxes/2026-10-08__ki-blast-three-phase-charge-ramp-additive-order-and-telegraph-window.py · observed RESULT: PASS additive 1 vs alpha 3 distinct results; telegraph invariant to speed, total window collapses at speed 64; in-order prefix resultant 0.99 vs bit-reversed 0.20 golden 0.27; impact peak tick 2, 0.86 after · brain train auto pass 5 (gap)
