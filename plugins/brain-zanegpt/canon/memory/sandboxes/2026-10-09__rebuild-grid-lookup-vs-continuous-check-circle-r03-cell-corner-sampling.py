"""Rebuild from the claim only. Own fixture: unit cells, ONE circular prop radius 0.3 (smaller than a cell), agent padding 0.15,
obstacle centre swept over a 20x20 lattice of sub-cell positions inside cell (5,5), path = 5 straight diagonal/horizontal
segments (slopes 0, 0.3, 0.7, 1.0, -0.5) through the neighbourhood.
G = grid lookup along the path (sampled every STEP), C = exact segment-to-centre distance < r+pad (continuous padded check).
PREDICTION (before run): (1) centre-sampled grid (blocked iff cell centre within r of the prop) sees NO blocked cell for
 1 - pi*0.3^2 = 71.7% of positions (287 +- 8 of 400); on those positions G reports 0 violations while C reports >= 1 for some
 path (misses > 0). (2) cell-square grid inflated by r+pad: with STEP 0.1 misses (C violation, G pass) = 0 on all 2000
 (position,path) pairs; (3) BREAK: same grid with STEP 2.0 misses > 0 and STEP 1.0 misses >= 0 but not greater than STEP 2.0;
 misses are monotone non-decreasing in STEP. (4) the corrected grid is conservative: G violations without C violation > 0."""
import math

R, PAD = 0.3, 0.15
CELL = 1.0

def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def sq_dist(p, cx, cy):          # distance from point to the unit square cell (cx,cy)
    dx = max(cx - p[0], 0.0, p[0] - (cx + 1)); dy = max(cy - p[1], 0.0, p[1] - (cy + 1))
    return math.hypot(dx, dy)

def blocked_centre(cell, prop):
    return math.hypot(cell[0] + 0.5 - prop[0], cell[1] + 0.5 - prop[1]) <= R

def blocked_square(cell, prop):
    return sq_dist(prop, cell[0], cell[1]) <= R + PAD

def g_violation(a, b, prop, step, blocked):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        if blocked((math.floor(x), math.floor(y)), prop): return True
    return False

def c_violation(a, b, prop):
    return seg_dist(prop, a, b) < R + PAD

PATHS = [((2.0, 5.5), (9.0, 5.5)), ((2.0, 3.5), (9.0, 5.6)), ((2.0, 2.0), (9.0, 9.0)), ((3.0, 8.0), (8.0, 2.5)), ((2.0, 7.0), (9.0, 3.5))]
PROPS = [(5 + (i + 0.5) / 20, 5 + (j + 0.5) / 20) for i in range(20) for j in range(20)]

unseen = sum(not any(blocked_centre((cx, cy), p) for cx in range(3, 8) for cy in range(3, 8)) for p in PROPS)
print("centre-sampled grid sees no blocked cell at %d of 400 positions (1-pi r^2 = %.1f)" % (unseen, 400 * (1 - math.pi * R * R)))

def misses(step, blocked, only_unseen=False):
    m = fp = 0
    for p in PROPS:
        for a, b in PATHS:
            c = c_violation(a, b, p); g = g_violation(a, b, p, step, blocked)
            m += (c and not g); fp += (g and not c)
    return m, fp

mc, _ = misses(0.1, blocked_centre)
res = {s: misses(s, blocked_square) for s in (0.1, 0.5, 1.0, 1.4, 2.0)}
print("centre-sampled grid, STEP 0.1: misses (C violation, G pass) = %d of %d" % (mc, 400 * len(PATHS)))
for s, (m, fp) in res.items():
    print("cell-square grid STEP %.1f: misses=%d  false alarms=%d" % (s, m, fp))
ms = [res[s][0] for s in (0.1, 0.5, 1.0, 1.4, 2.0)]
ok = (280 <= unseen <= 295 and mc > 0 and res[0.1][0] == 0 and res[2.0][0] > 0 and ms == sorted(ms) and res[0.1][1] > 0)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "centre grid misses %d; cell-square misses by STEP 0.1/0.5/1.0/1.4/2.0 = %s; false alarms at 0.1 = %d" % (mc, ms, res[0.1][1]))
