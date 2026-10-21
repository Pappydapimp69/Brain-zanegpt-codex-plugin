"""Compose two Brain lessons:
 - origami E1: a single vertex folds from a flat sheet only if its sector angles close (sum 360)
   and, to fold FLAT, the alternating sums are each 180 (Kawasaki; reflection composition = identity).
 - roofing E1: sloped area = plan area x pitch multiplier sqrt(1+(p/12)^2), exact for gable and hip.
Question: does the per-face exactness of the multiplier mean a roof is a folded flat sheet, i.e. do the
sloped sector angles around each roof vertex still sum to 360 like the plan angles do?
Pure stdlib, deterministic.
"""
import math

def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def ang(u, v): return math.degrees(math.acos(max(-1.0, min(1.0, dot(u, v) / (norm(u) * norm(v))))))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def sectors(vertex, rays):
    """rays: neighbour points in cyclic order around the vertex; returns sector angles on the surface."""
    d = [sub(r, vertex) for r in rays]
    return [ang(d[i], d[(i + 1) % len(d)]) for i in range(len(d))]

def plan(v): return (v[0], v[1], 0.0)

def poly_area(pts):
    s = (0.0, 0.0, 0.0)
    for i in range(len(pts)):
        s = tuple(a + b for a, b in zip(s, cross(pts[i], pts[(i + 1) % len(pts)])))
    return 0.5 * norm(s)

def kawasaki(sec):
    if len(sec) % 2: return False
    return abs(sum(sec[0::2]) - 180) < 1e-9 and abs(sum(sec[1::2]) - 180) < 1e-9

PITCHES = [4, 6, 9, 12]
rows = []
for p in PITCHES:
    s = p / 12.0
    m = math.sqrt(1 + s * s)
    # Hip roof on a 30 x 40 house (x 0..40, y 0..30), common pitch: ridge from (15,15) to (25,15), height 15*s
    H = 15 * s
    r1, r2 = (15.0, 15.0, H), (25.0, 15.0, H)
    c = [(0.0, 0.0, 0.0), (40.0, 0.0, 0.0), (40.0, 30.0, 0.0), (0.0, 30.0, 0.0)]
    # around ridge end r1: other ridge end, hip to (0,30), hip to (0,0)  (cyclic: ridge -> NW hip -> SW hip)
    hip = sectors(r1, [r2, c[3], c[0]])
    hip_plan = sectors(plan(r1), [plan(r2), plan(c[3]), plan(c[0])])
    # gable ridge midpoint, same house as gable: ridge along x at y=15, interior point (20,15,H)
    g = (20.0, 15.0, H)
    gab = sectors(g, [(40.0, 15.0, H), (20.0, 30.0, 0.0), (0.0, 15.0, H), (20.0, 0.0, 0.0)])
    # L/T junction: main gable (ridge along x, y in -15..15) meets a wing gable of equal width and pitch
    # running toward -y with ridge along y at x=0; both ridges at height H; valleys run to (-15,-15,0),(15,-15,0)
    j = (0.0, 0.0, H)
    tj = sectors(j, [(10.0, 0.0, H), (0.0, 15.0, 0.0), (-10.0, 0.0, H), (-15.0, -15.0, 0.0),
                     (0.0, -10.0, H), (15.0, -15.0, 0.0)])
    tj_plan = sectors(plan(j), [(10.0, 0.0, 0), (0.0, 15.0, 0.0), (-10.0, 0.0, 0), (-15.0, -15.0, 0.0),
                                (0.0, -10.0, 0), (15.0, -15.0, 0.0)])
    # area check on hip faces: sum of 3D faces vs plan x multiplier
    faces = [[c[0], c[1], r2, r1], [c[1], c[2], r2], [c[2], c[3], r1, r2], [c[3], c[0], r1]]
    area3d = sum(poly_area(f) for f in faces)
    area_rule = 40 * 30 * m
    rows.append((p, sum(hip), sum(hip_plan), sum(gab), kawasaki(gab), sum(tj), sum(tj_plan), area3d, area_rule, hip))
    print(f"pitch {p}/12: hip apex sloped sum {sum(hip):.3f} (plan {sum(hip_plan):.1f}, deficit {360-sum(hip):.3f}) "
          f"sectors {[round(x,2) for x in hip]}; gable ridge sum {sum(gab):.3f} kawasaki {kawasaki(gab)}; "
          f"valley junction sum {sum(tj):.3f} (plan {sum(tj_plan):.1f}, excess {sum(tj)-360:.3f}); "
          f"hip area 3D {area3d:.4f} vs plan*mult {area_rule:.4f}")

area_ok = all(abs(r[7] - r[8]) < 1e-6 for r in rows)
plans_close = all(abs(r[2] - 360) < 1e-9 and abs(r[6] - 360) < 1e-9 for r in rows)
gable_ok = all(abs(r[3] - 360) < 1e-9 and r[4] for r in rows)
hip_gap = all(360 - r[1] > 0.5 for r in rows) and all(rows[i][1] > rows[i + 1][1] for i in range(len(rows) - 1))
valley_over = all(r[5] - 360 > 0.5 for r in rows)
# Break test: hidden assumption "every exact-area face set unfolds into one flat sheet" -> hip apex odd degree, sum < 360
print(f"checks: area exact {area_ok}; plan angles close at every vertex {plans_close}; gable ridge flat-foldable {gable_ok}; "
      f"hip apex leaves a gap growing with pitch {hip_gap}; valley junction overlaps {valley_over}")
ok = area_ok and plans_close and gable_ok and hip_gap and valley_over
print(f"RESULT: {'PASS' if ok else 'FAIL'} area = plan x multiplier exact at all 4 pitches, but sloped angles do not close: "
      f"hip apex gap {360-rows[0][1]:.2f} deg at 4/12 to {360-rows[-1][1]:.2f} at 12/12, valley junction overlap "
      f"{rows[0][5]-360:.2f} to {rows[-1][5]-360:.2f} deg; only the gable ridge (360, Kawasaki true) unfolds flat")
