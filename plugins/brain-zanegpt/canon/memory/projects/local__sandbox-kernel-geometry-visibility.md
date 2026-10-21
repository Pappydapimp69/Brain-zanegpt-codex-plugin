# local/sandbox-kernel-geometry-visibility — lessons

Project: local/sandbox-kernel-geometry-visibility. Newest first.

---

## E1 — piercing faces need a split or a depth buffer with near plane precision
- Date: 2026-09-28
- Project: local/sandbox-kernel-geometry-visibility
- Tags: [rendering][geometry][correctness][precision]
- What: Applied the ideas kernel that for mutually piercing geometry no whole-face draw order is correct, so a depth buffer is a correctness choice rather than a speed trade. It reproduced on a different pair of triangles, and the depth buffer's own correctness turned out to depend on depth precision and the near plane.
- Why built: brain train gap listed the kernel as unapplied, and memory had no entry on painter's sorting or depth buffers.
- Design: A 64x64 rasteriser with barycentric depth over pixel centres: triangle A flat at z=50, triangle B leaning from z=86 to z=16 through it, smaller z nearer. Ground truth is an exact per-pixel depth comparison. Compared both draw orders, the centroid far-to-near sort, and B split at the plane z=50 with its far part drawn before A and near part after. Then a quantised perspective depth buffer at 16 and 24 bits, far plane 10000, near plane 1, 0.1, 0.01 and 0.001.
- Got right: Testing the depth buffer against exact depth instead of treating it as ground truth, as the kernel's own sandbox did.
- Where/why it failed: Of 1790 covered pixels, drawing A then B got 682 wrong (38.1%) and B then A got 150 wrong (8.4%); the centroid sort chose B then A, the less bad order, and no order was correct. Splitting B at the intersection gave 0 wrong. The 24-bit depth buffer was exact at every near plane tested; the 16-bit one was exact at near 1 and 0.1 but got 18 of 832 overlapping pixels wrong at near 0.01 and 64 at 0.001, all along the intersection line.
- Fix: For piercing geometry, use a depth buffer or split faces at the intersection, never a better sort key. With a depth buffer, keep the near plane as far out as the scene allows or use more depth bits, because perspective depth spends its precision close to the near plane.
- Why this fix: No face order exists when each face is nearer on part of the overlap. A quantised depth buffer reintroduces the same error along the intersection once its step size exceeds the depth gap there.
- Rule of thumb: For piercing faces no draw order is correct (682 and 150 of 1790 pixels wrong; the centroid sort picks the lesser) while a split at the intersection is exact, and a depth buffer is only exact while its precision covers the depth gap at the intersection: 16-bit perspective depth got 18 and 64 of 832 overlapping pixels wrong with the near plane at 0.01 and 0.001, 24-bit none.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b04.py loop 16 in Pappydapimp69/Brain, deterministic. Observed: 682 and 150 wrong for the two orders, 0 for the split; 16-bit depth 0/0/18/64 wrong at near 1/0.1/0.01/0.001, 24-bit 0 throughout. The triangles differ from the kernel's own sandbox, so the counts differ from its 380 and 114; the structure matches.
- Composed: ideas:GEOMETRY/visibility/a-depth-buffer-is-a-correctness-choice-not-a-faster-painters-sort/for-piercing-geometry-no-face-ordering-exists-at-all
- Link: session 2026-09-28, brain train gap batch 4 loop 16
- Sandbox: sandboxes/2026-09-28__train-gap-b04.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-11 · projects/local__painters-centroid-sort-vs-zbuffer-yaw-sweep-bbox-overlap-not-sufficient.md#E1 · compatible · sandboxes/2026-10-11__painters-centroid-sort-vs-zbuffer-yaw-sweep-bbox-overlap-not-sufficient.py · observed RESULT: PASS bbox_overlap_all=True yaw0 wrongAB=460 wrongBA=154 centroid=154; yaws with a zero-wrong order=1; centroid wrong at 17/18 yaws; control max=0 · scheduled brain train loop 1 pass 5 gap; session_015bpfiyHog3CaYStqh5GY3K
