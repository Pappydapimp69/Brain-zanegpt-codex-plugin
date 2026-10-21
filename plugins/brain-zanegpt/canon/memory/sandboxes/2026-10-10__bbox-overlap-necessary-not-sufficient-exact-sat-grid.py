"""Prediction (before run), frame = square [-1,1]^2, bars = rotated rectangles (exact Fractions, SAT as ground truth):
 (1) bbox-overlap has ZERO false negatives (necessary) but many false positives on diagonal bars (not sufficient), > 10% of bbox hits;
 (2) 'any bar vertex inside frame' has false negatives (long bars that pierce the frame with all 4 corners outside) > 0;
 (3) a centre-only fit test (the min(halfW/|x|, halfH/|y|) form, applied to the bar centre) misses long bars both ways;
     ITERATION 1: this was wrong - a centre inside the frame is inside the bar polygon too, so centre-fit has 0 false positives
     and only false negatives; the asserts below keep the corrected claim (one-sided: sufficient, not necessary).
 (4) BREAK: tiling two frames [-1,1] and [1,3]: a point on the shared edge x=1 is claimed by 2 tiles inclusive, 0 exclusive,
     exactly 1 with half-open [lo,hi) - the point-in-polygon edge rule, applied to which tile 'owns' a bar vertex."""
from fractions import Fraction as F
from itertools import product

DIRS = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (1, 2), (3, 1), (1, 3)]
def corners(c, d, a, b):
    dx, dy = d; px, py = -dy, dx
    return [(c[0] + sa * a * dx + sb * b * px, c[1] + sa * a * dy + sb * b * py) for sa, sb in ((1, 1), (1, -1), (-1, -1), (-1, 1))]

def bbox_overlap(P):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return max(xs) >= -1 and min(xs) <= 1 and max(ys) >= -1 and min(ys) <= 1

def sat_overlap(P):  # exact convex overlap with the frame square (closed)
    if not bbox_overlap(P): return False
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for i in range(4):
        ex, ey = P[(i + 1) % 4][0] - P[i][0], P[(i + 1) % 4][1] - P[i][1]
        nx, ny = -ey, ex
        pp = [nx * p[0] + ny * p[1] for p in P]; ss = [nx * q[0] + ny * q[1] for q in sq]
        if max(pp) < min(ss) or max(ss) < min(pp): return False
    return True

def vertex_inside(P): return any(-1 <= p[0] <= 1 and -1 <= p[1] <= 1 for p in P)
def centre_fit(c): return abs(c[0]) <= 1 and abs(c[1]) <= 1

cases = []
for cx, cy in product([F(k, 2) for k in range(-8, 9)], repeat=2):
    for d in DIRS:
        for a, b in ((F(1, 2), F(1, 8)), (F(3, 2), F(1, 8)), (F(4), F(1, 8))):
            cases.append(((cx, cy), d, a, b))
st = dict(n=len(cases), truth=0, bbox_fn=0, bbox_fp=0, bbox_hit=0, vert_fn=0, vert_fp=0, cen_fn=0, cen_fp=0)
for c, d, a, b in cases:
    P = corners(c, d, a, b); t = sat_overlap(P); bb = bbox_overlap(P); v = vertex_inside(P); cf = centre_fit(c)
    st["truth"] += t; st["bbox_hit"] += bb
    st["bbox_fn"] += (t and not bb); st["bbox_fp"] += (bb and not t)
    st["vert_fn"] += (t and not v); st["vert_fp"] += (v and not t)
    st["cen_fn"] += (t and not cf); st["cen_fp"] += (cf and not t)
print(st)

tiles = [(-1, 1), (1, 3)]
def claims(x, mode):
    n = 0
    for lo, hi in tiles:
        n += {"incl": lo <= x <= hi, "excl": lo < x < hi, "half": lo <= x < hi}[mode]
    return n
edge = {m: claims(1, m) for m in ("incl", "excl", "half")}
interior = {m: sorted({claims(F(k, 4), m) for k in range(-3, 12) if F(k, 4) != 1}) for m in ("incl", "excl", "half")}
print("shared-edge claims", edge, "interior claim counts", interior)

frac = st["bbox_fp"] / st["bbox_hit"]
ok = (st["bbox_fn"] == 0 and frac > 0.10 and st["vert_fn"] > 0 and st["cen_fn"] > 0 and st["cen_fp"] == 0
      and edge == {"incl": 2, "excl": 0, "half": 1} and interior["half"] == [1] and interior["incl"] == [1] and interior["excl"] == [1])
print("RESULT:", "PASS" if ok else "FAIL",
      f"{st['n']} bars: bbox false-neg {st['bbox_fn']}, false-pos {st['bbox_fp']}/{st['bbox_hit']} ({frac:.1%}); vertex-in-frame misses {st['vert_fn']} true overlaps; "
      f"centre-fit misses {st['cen_fn']} and wrongly accepts {st['cen_fp']}; shared edge claimed {edge}")
