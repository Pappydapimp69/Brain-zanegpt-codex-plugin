# local/sandbox-geometry-pip — lessons

Project: local/sandbox-geometry-pip. Newest first.

---

## E2 — seed geometry boundary point classification asymmetric
- Date: 2026-07-13
- Project: local/sandbox-geometry-pip
- Tags: [algorithm][geometry][gamedev]
- What: `brain train new-domain geometry` (0 entries tagged). `local__sandbox-geometry-pip.md#E1` fixed a vertex-aligned-ray misclassification using the standard half-open interval PNPOLY convention (`(yi > y) != (yj > y)`). External research (WebSearch — direct WebFetch blocked by this session's confirmed org egress policy) against W. Randolph Franklin's own PNPOLY documentation confirms the half-open convention is correct and standard, but also flags a SEPARATE, deliberate consequence sandbox-geometry-pip#E1 doesn't record: PNPOLY treats the polygon as a "semi-open set," so a test point lying exactly ON an edge (not at a vertex) is classified by a convention that depends on WHICH edge it's on — not a symmetric "boundary points count as inside" or "outside" rule. Sandbox-confirmed: the same point-in-polygon test classifies a point on one edge of a square as inside (`True`) and the mirror-image point on the opposite edge as outside (`False`), using E1's exact fixed algorithm, unmodified.
- Why built: sandbox-geometry-pip#E1's fix and verification (two independent ground-truth derivations both saying "outside" for the vertex-ray case) never tested points lying ON an edge — a related but distinct degenerate input class from the vertex-ray case it did test.
- Design: `sandbox.py` — zero RNG, zero wall-clock. E1's exact fixed algorithm (PNPOLY half-open interval), applied unmodified to a fixed 10x10 axis-aligned square. Tested the midpoint of each of the four edges (bottom, left, top, right) — all four are symmetric positions on a square, so any asymmetry in the result is attributable only to the algorithm's boundary convention, not the input geometry.
- Got right: E1's fix is not disputed or reopened — this sandbox uses E1's exact algorithm unchanged; the vertex-ray bug it fixed stays fixed. The algorithm is also fully deterministic and gave the same boundary classification every run (no crash, no exception, no NaN) — it isn't "broken," it's a documented convention most callers don't know to expect.
- Where/why it failed: N/A — not a bug in E1's fix, a distinct degenerate-input class flagged as a gap. The bottom edge midpoint `(5,0)` and left edge midpoint `(0,5)` both classified `True` (inside); the top edge midpoint `(5,10)` and right edge midpoint `(10,5)` both classified `False` (outside) — on a perfectly symmetric square, using the identical algorithm, purely because of which two of the four edges the half-open convention favors.
- Fix: Not applied to any shipping code (seed entry). Any caller that needs to know "is a point on the polygon boundary itself" (as opposed to strictly inside) must NOT rely on point_in_polygon's True/False alone — either treat boundary membership as its own explicit check (distance-to-nearest-edge under an epsilon) or explicitly document which edges of the shape count as "inside" under this convention, since it is not the two intuitively symmetric pairs (e.g. not "top+bottom" or "left+right" as a pair — it split ONE from each pair).
- Why this fix: PNPOLY's semi-open-set convention exists specifically so tiling adjacent polygons never double-counts or drops a shared-edge point (Franklin's own stated rationale) — it's the right choice for polygon TILING, but a caller using point-in-polygon for a different purpose (e.g. "is this click exactly on the wall") would get a silently inconsistent answer without knowing the convention exists.
- Rule of thumb: A point-in-polygon test using the standard half-open-interval (PNPOLY) convention classifies boundary points asymmetrically by design — a point on one edge of an otherwise-symmetric shape can return `True` while the mirrored point on the opposite edge returns `False`, with no error and no indication anything unusual happened. Never infer "is this point ON the boundary" from a bare inside/outside test; check distance-to-edge explicitly if boundary membership itself matters.
- Provenance (verified/assumed): Verified first-hand — built `sandbox.py` (zero RNG, zero wall-clock, E1's exact unmodified algorithm, a fixed symmetric square, four symmetric edge-midpoint test points), confirmed asymmetric classification (`True, True, False, False`) across the four symmetric points. Confirmed deterministic/reproducible across two independent process invocations of `python3 sandbox.py`, output diffed byte-identical. External claim (PNPOLY's semi-open-set boundary convention, and its stated purpose for polygon tiling) verified via live WebSearch results describing W. Randolph Franklin's own PNPOLY documentation, cross-consistent across independent sources; direct WebFetch was not attempted given this session's confirmed org egress-policy block on general web hosts.
- Link: session (brain train new-domain geometry, external research); sandbox `sandbox.py`, scratchpad `gap8/` (run twice as separate process invocations, outputs diffed byte-identical); WebSearch query "PNPOLY point in polygon algorithm Franklin edge cases vertex on boundary known limitations"
- Composed: local/sandbox-geometry-pip/E1

## E1 — point in polygon vertex aligned ray misclassifies
- Date: 2026-07-20
- Project: local/sandbox-geometry-pip
- Tags: [algorithm][gamedev]
- What: The common from-scratch "point in polygon" ray-casting
  implementation — checking whether a test point's y-coordinate falls
  within an edge's y-range using an INCLUSIVE check on both endpoints
  (`min(yi,yj) <= y <= max(yi,yj)`) — misclassifies a point whose
  horizontal test ray passes exactly through a polygon VERTEX where the
  boundary genuinely crosses the ray (one adjacent edge above, one
  below), because both edges sharing that vertex get counted as
  crossings instead of exactly one. The standard, well-documented fix
  (PNPOLY, W. Randolph Franklin) uses a half-open interval instead —
  `(yi > y) != (yj > y)` — which counts a vertex-touching intersection
  only via the edge whose OTHER endpoint lies below the ray.
- Why built: `brain train new-domain`, targeting "geometry" via external
  research (`brain query` confirmed zero real coverage — the geometry-
  adjacent hits were all incidental tag matches from unrelated
  pathfinding/mesh/procgen lessons, nothing on computational-geometry
  primitives like point-in-polygon, triangulation, or hull algorithms).
  External research (Wikipedia's "Point in polygon" article) confirmed
  this exact vertex-alignment case is a well-known, named pitfall, not
  an invented edge case — quoting the source: "If the intersection
  point is a vertex of a tested polygon side, then the intersection
  counts only if the other vertex of the side lies below the ray."
- Design: `sandbox.py` — exact integer coordinates (no floating-point
  ambiguity in the vertex alignment itself). Polygon `[(0,0), (10,0),
  (10,10), (5,5), (0,3)]` — a pentagon where vertex `(5,5)` is a genuine
  PASS-THROUGH point (one adjacent vertex `(10,10)` is above y=5, the
  other adjacent vertex `(0,3)` is below y=5 — the boundary truly
  crosses the ray there, not a peak/valley that merely touches it,
  which matters: touching-vertex cases don't actually flip the final
  parity, only genuine pass-through vertices do). Test point `(1, 5)` —
  y exactly matches the vertex. Two independent ground-truth checks,
  neither relying on either algorithm under test: (1) hand-derived
  polygon-boundary interpolation at x=1 (upper boundary y=3.4 < test
  y=5, so OUTSIDE); (2) an independent rotated-ray cross-check — rotate
  both polygon and point by 7 degrees so the ray no longer passes
  through any vertex at all, then classify with the (now non-degenerate)
  standard algorithm.
- Got right: both independent ground-truth methods agree (OUTSIDE), and
  the correct PNPOLY algorithm matches both exactly — confirming the
  ground truth itself is sound before judging the naive algorithm
  against it.
- Where/why it failed: the naive inclusive-both-endpoints check reports
  `inside=True` for this test point — the WRONG answer, disagreeing with
  both independent ground-truth derivations and with the correct
  algorithm. Root cause: at the shared vertex, edge `(10,10)-(5,5)`'s
  y-range `[5,10]` inclusively contains the test y=5 (should NOT count,
  its other endpoint is above the ray) and edge `(5,5)-(0,3)`'s y-range
  `[3,5]` inclusively contains it too (correctly SHOULD count, its other
  endpoint is below) — the naive check counts BOTH (parity-flipping
  double-count), while the correct rule counts only the second, giving
  opposite final parity (naive: 3 total crossings, odd, "inside"; correct:
  2 total crossings, even, "outside").
- Fix: use the half-open interval form for the y-range membership test
  (`(yi > y) != (yj > y)`, equivalently "one endpoint's y is strictly
  greater than the test y, the other is not") instead of a symmetric
  inclusive-both-ends range check, in any from-scratch point-in-polygon
  ray-casting implementation.
- Why this fix: the half-open convention guarantees every polygon vertex
  is attributed to EXACTLY ONE of its two adjacent edges for crossing-
  counting purposes (whichever edge's far endpoint is below the ray),
  making a vertex-aligned ray behave identically to a ray offset by an
  infinitesimal epsilon — which is the property a symmetric inclusive
  check does not have (it attributes a pass-through vertex to BOTH
  adjacent edges, a peak/valley-touching vertex to zero net effect by
  coincidence, and is fundamentally inconsistent between the two cases).
- Rule of thumb: any from-scratch point-in-polygon (or general ray/
  segment-crossing-count) implementation must use a HALF-OPEN interval
  for each edge's y-range membership test, never a symmetric inclusive-
  both-ends check — the bug is invisible for the vast majority of random
  test points (any point whose ray doesn't happen to pass through a
  vertex renders identically either way) and only manifests for points
  exactly aligned with a polygon vertex on the ray axis, which is
  common in practice for grid-aligned data, snapped coordinates, or
  deliberately-placed test/click points — not a rare edge case to
  deprioritize.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  (zero RNG, zero wall-clock, exact integer coordinates), confirmed the
  naive algorithm disagrees with BOTH independently-derived ground
  truths while the correct PNPOLY-style algorithm agrees with both.
  Re-ran as two independent process invocations; output byte-identical.
  Externally sourced (not internal reasoning alone): Wikipedia, "Point
  in polygon" — https://en.wikipedia.org/wiki/Point_in_polygon.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, geometry gap); sandbox
  `scratchpad/geometry/sandbox.py`, run twice as independent process
  invocations, outputs diffed identical; source
  https://en.wikipedia.org/wiki/Point_in_polygon
- Cited-by: 2026-07-13 · projects/local__sandbox-geometry-pip.md#E2 · compatible · no sandbox · session (brain train new-domain geometry, external research); sandbox `sandbox.py`, scratchpad `gap8/` (run twice as separate process invocations, outputs diffed byte-identical); WebSearch query "PNPOLY point in polygon algorithm Franklin edge cases vertex on boundary known limitations"

- Audited: 2026-10-14 · pass · The entry's sandbox.py is not stored in canon, so I audited its design from the text and re-ran its stated fixture myself (pentagon (0,0),(10,0),(10,10),(5,5),(0,3), point (1,5)). The inclusive-endpoint ray cast returned inside (True) and the half-open PNPOLY form returned outside (False), which matches the entry's claim and its independently derived ground truth of outside. The model computes its answer from the two algorithms, so the result is not built in, and it uses exact integer coordinates. Coverage is narrow: one polygon and one point, so the general statement that a pass-through vertex is double counted rests on one case plus the cited Wikipedia and Franklin sources. That is enough for the rule of thumb as worded, since it names only the vertex-aligned pass-through case. Edge points and collinear edges are separately covered by E2, and the entry correctly says touching-vertex cases do not flip parity. · brain train auto loop 2 pass 3 (audit), session_01CwpncTDkwf6YoSaQyXUsNe
- Reverified: 2026-10-14 · pass · sandboxes/2026-10-14__rebuild-pip-inclusive-vs-half-open-vs-winding-reference.py · observed RESULT: PASS inclusive wrong 9/4/4/15, all on vertex rows; half-open wrong 0 of 714; half-integer control agrees everywhere. The local-extremum half of the prediction was not isolated. · Built my own fixture from the claim alone: four integer-grid polygons (diamond, concave arrow, L shape with horizontal edges, zigzag with pass-through vertices), every integer test point from -2 to 11 on both axes except boundary points, judged against an independent winding-number reference with exact fractions. The inclusive-both-ends test was wrong on 9, 4, 4 and 15 points, every one of them on a row that passes through a polygon vertex, while the half-open test was wrong on 0 of 714 points including the polygon with horizontal edges, and on half-integer rows that touch no vertex the two implementations agreed everywhere. This supports the claim and its rule of thumb, including that the bug hides for points off the vertex rows; I did not separately isolate local-extremum vertices, so that sub-claim is not confirmed here. My fixture differs from the original in using a winding-number oracle rather than a hand-worked expectation and in adding a horizontal-edge polygon and an off-grid control. · brain train auto scheduled run, loop 1 pass 4; session_013UbxUV5wii3FwAXCPW9kkg
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E387 · compatible · sandboxes/2026-10-08__half-open-bucketing-of-phase-offset-particles-and-pip-vertices.py · observed RESULT: PASS half-open gives one bucket/edge per boundary item (12 vs inclusive 15; PIP wrong incl 2 half 0); float edge compare mismatched exact in 18/295 cases. Inclusive was 15 not 16 (prediction partly wrong). · brain train auto pass 1 (kernel)
