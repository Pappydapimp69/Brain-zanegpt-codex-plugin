"""Cel loop 8 - where to evaluate the cel step: on N.L interpolated from the vertices
(Gouraud-style, cheap, what a per-vertex ramp coordinate does) or on the per-pixel
interpolated-and-renormalised normal. A sphere tessellated in latitude/longitude with
n segments (n/2 rings), viewed in angle space: each point's cell in (theta, phi) is
found, and the cell's 4 corner values are bilinearly interpolated (quad stand-in for two
triangles). Light 60 degrees off the view axis, so the terminator crosses the cells
obliquely. Truth = exact sphere. Deviation = max great-circle distance (in px on a
200 px radius sphere) between points shaded wrongly and the true terminator.
PREDICTION (written before running): at n = 16, vertex-N.L deviation is >= 3x the
per-pixel-normal deviation; both shrink as n grows, vertex-N.L roughly as 1/n^2 * R."""
import math
R = 200.0
L = (math.sin(math.radians(60)) * math.cos(0.3), math.sin(math.radians(60)) * math.sin(0.3), math.cos(math.radians(60)))
def sph(th, ph): return (math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th))
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
def run(n, thr=0.0):
    rings, segs = n // 2, n
    dth, dph = math.pi / rings, 2 * math.pi / segs
    worst_v = worst_p = 0.0
    for a in range(1, 400):
        th = math.pi * a / 400
        for b in range(0, 800):
            ph = 2 * math.pi * b / 800
            p = sph(th, ph); truth = dot(p, L)
            i, j = min(int(th / dth), rings - 1), int(ph / dph) % segs
            fy, fx = th / dth - i, ph / dph - int(ph / dph)
            corners = [sph(i * dth, j * dph), sph(i * dth, (j + 1) * dph), sph((i + 1) * dth, j * dph), sph((i + 1) * dth, (j + 1) * dph)]
            wts = [(1 - fx) * (1 - fy), fx * (1 - fy), (1 - fx) * fy, fx * fy]
            vndl = sum(w_ * dot(c, L) for w_, c in zip(wts, corners))                       # vertex N.L, interpolated
            nrm = [sum(w_ * c[k] for w_, c in zip(wts, corners)) for k in range(3)]
            k_ = math.sqrt(sum(x * x for x in nrm)); pndl = dot([x / k_ for x in nrm], L)   # per-pixel normal
            dist = abs(math.asin(max(-1, min(1, truth))) - math.asin(thr)) * R                                # distance to the true terminator
            if (vndl > thr) != (truth > thr): worst_v = max(worst_v, dist)
            if (pndl > thr) != (truth > thr): worst_p = max(worst_p, dist)
    return worst_v, worst_p
# Iteration 1 (threshold 0) gave IDENTICAL errors: vertex N.L = interpolated normal . L, and
# renormalising only multiplies by a positive number, so the sign test cannot differ.
# Iteration 2: thresholds away from 0, where the interpolated normal's shortened length matters.
# PREDICTION (written before iteration 2): at threshold 0.3 and n 16 the vertex version is off
# by >= 2x the per-pixel version; at threshold 0 they stay identical for every n.
res = {}
for thr in (0.0, 0.3, 0.6):
    for n in (8, 16, 32):
        res[(thr, n)] = run(n, thr)
        v, p_ = res[(thr, n)]
        print(f"threshold {thr:.1f} n {n:2d}: vertex N.L off by {v:6.2f}px, per-pixel normal {p_:6.2f}px")
same0 = all(abs(res[(0.0, n)][0] - res[(0.0, n)][1]) < 1e-9 for n in (8, 16, 32))
r = res[(0.3, 16)][0] / max(res[(0.3, 16)][1], 1e-6)
print(f"RESULT: {'PASS' if same0 and r >= 2 else 'FAIL'} threshold 0 identical at all n: {same0}; threshold 0.3 n16 vertex "
      f"{res[(0.3,16)][0]:.2f}px vs per-pixel {res[(0.3,16)][1]:.2f}px ({r:.1f}x); threshold 0.6 n16 {res[(0.6,16)][0]:.2f} vs {res[(0.6,16)][1]:.2f}px")
