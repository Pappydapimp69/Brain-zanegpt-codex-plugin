"""Closed-traverse adjustment (compass/Bowditch rule): distribute misclosure over vertices in proportion to cumulative leg length.
Truth polygon known, so true vertex errors are computable. Deterministic perturbations (no RNG)."""
import math

TRUE = [(0, 0), (120, 10), (190, 90), (150, 190), (40, 200), (-30, 100)]   # closed polygon vertices (last connects to first)
n = len(TRUE)
legs = []
for i in range(n):
    a, b = TRUE[i], TRUE[(i + 1) % n]
    legs.append((math.hypot(b[0] - a[0], b[1] - a[1]), math.atan2(b[1] - a[1], b[0] - a[0])))

def traverse(dist_err, ang_err):
    pts = [TRUE[0]]; x, y = TRUE[0]
    for (d, th), de, ae in zip(legs, dist_err, ang_err):
        d2, t2 = d * (1 + de[0]) + de[1], th + ae
        x += d2 * math.cos(t2); y += d2 * math.sin(t2); pts.append((x, y))
    return pts   # n+1 points, last should return to start

def bowditch(pts):
    mx, my = pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]
    cum = [0.0]
    for i in range(n):
        cum.append(cum[-1] + math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
    tot = cum[-1]
    return [(p[0] - mx * c / tot, p[1] - my * c / tot) for p, c in zip(pts, cum)], math.hypot(mx, my)

def errs(pts):
    return [math.hypot(pts[i][0] - TRUE[i][0], pts[i][1] - TRUE[i][1]) for i in range(n)]

def report(name, de, ae):
    raw = traverse(de, ae); adj, mis = bowditch(raw)
    er, ea = errs(raw), errs(adj)
    print(f"{name:34s} misclosure {mis:6.3f} | mean vertex err raw {sum(er)/n:6.3f} adj {sum(ea)/n:6.3f} | max raw {max(er):6.3f} adj {max(ea):6.3f} | err at vertex 2: raw {er[2]:.3f} adj {ea[2]:.3f}")
    return er, ea, mis

zero = [(0, 0)] * n; zang = [0] * n
res = []
# S1 BREAK (built to break the 'closure check validates the survey' claim): every distance 0.2% long (miscalibrated tape)
er, ea, mis = report("S1 tape scale +0.2%", [(0.002, 0)] * n, zang)
print('   S1 BREAK: a pure scale error closes perfectly, so misclosure cannot see it and the adjustment cannot remove it')
res.append(mis < 1e-9 and abs(sum(ea) - sum(er)) < 1e-9 and sum(er) / n > 0.2)
# S2 small pseudo-random distance and angle noise
de = [(0, 0.05 * math.sin(7 * i + 1)) for i in range(n)]; ae = [0.0004 * math.cos(5 * i + 2) for i in range(n)]
er, ea, mis = report("S2 small mixed noise", de, ae)
res.append(sum(ea) < sum(er))
# S3 BREAK: one blunder - leg 3 distance + 2.0 m
de = [(0, 0)] * n; de[3] = (0, 2.0)
er, ea, mis = report("S3 blunder +2.0m on leg 3", de, zang)
early_raw, early_adj = sum(er[:3]), sum(ea[:3])
print(f"   S3 vertices 0-2 (before the blunder): raw total {early_raw:.3f} adj total {early_adj:.3f}")
res.append(early_adj > early_raw and early_raw == 0.0)
# S4 BREAK: angular blunder (1 degree on leg 1)
ae = [0.0] * n; ae[1] = math.radians(1)
er, ea, mis = report("S4 angle blunder 1deg on leg 1", zero, ae)
res.append(max(ea) > 0.5 * max(er) or sum(ea) > sum(er) * 0.5)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" checks={res}")
