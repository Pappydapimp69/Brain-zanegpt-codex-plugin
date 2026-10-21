"""Edge: cel-shading E6 (inverted-hull outlines: a back-face-only shell of radius r+w drawn
black behind the body) x painters-centroid-sort E1 (a centroid painter's sort vs a per-pixel
depth test; count wrong pixels at the camera you use).
An inverted hull relies on depth testing: its back faces sit BEHIND the body. Without a
depth buffer, hull triangles are ordered by centroid depth alongside everyone else.
Scenario A: two disjoint UV spheres (r=0.6, outline w=0.06) overlapping on screen (x offset
0.8), depth gap d swept. Scenario B (added after run 1 showed A is sorted exactly): one
outlined sphere hovering a fixed clearance in front of a large tilted backdrop made of two
big triangles (z = y, i.e. a floor rising away), sphere centre swept over a 5x5 grid of
screen positions. Orthographic view down -z, larger z nearer. Reference = per-pixel
z-buffer. Painters: (a) global centroid sort over all triangles, (b) per-object sort
(objects by centre z; within an object hull first, then body). Deterministic, stdlib only.

PREDICTION (written before first run): single sphere: centroid sort exact (0 wrong).
Two spheres, global centroid sort: the near sphere's outline pixels that lie over the far
sphere go wrong at a larger depth gap than its body pixels do, and at every gap the wrong
FRACTION of near-outline pixels is >= that of near-body pixels. Per-object sort: 0 wrong at
every disjoint gap; it fails once the spheres interpenetrate (break case, d=0.5).
RUN 1 refuted the two-sphere part (centroid sort was exact at every disjoint gap), so
scenario B was added. PREDICTION for B (written after run 1, before B first ran): where the
centroid sort errs, the outline's wrong fraction is >= the body's at every position, more
positions lose outline only than body only, and per-object sort is 0 wrong (the backdrop is
an object behind the sphere, so that part is close to built in)."""
import math
R, W, DX = 0.6, 0.06, 0.8
N = 128; LO, HI = -1.6, 1.6
def px(v): return (v - LO) / (HI - LO) * N
def sphere(cx, cz, rad, obj, part, lat=14, lon=28):
    tris = []
    def P(i, j):
        th = math.pi * i / lat; ph = 2 * math.pi * j / lon
        n = (math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph))  # y up, z toward camera
        return (cx + rad * n[0], rad * n[1], cz + rad * n[2]), n
    for i in range(lat):
        for j in range(lon):
            a, b, c, d = P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)
            for t in ((a, b, c), (a, c, d)):
                nz = sum(v[1][2] for v in t) / 3
                if part == "body" and nz <= 0: continue      # cull back faces of the body
                if part == "hull" and nz >= 0: continue      # cull FRONT faces of the hull
                pts = [v[0] for v in t]
                if len({(round(p[0], 9), round(p[1], 9)) for p in pts}) < 3: continue
                tris.append((pts, obj, part, cz))
    return tris
def raster(tri):
    (a, b, c) = [(px(p[0]), px(p[1]), p[2]) for p in tri]
    area = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
    if abs(area) < 1e-12: return
    x0, x1 = max(0, int(min(a[0], b[0], c[0]))), min(N - 1, int(max(a[0], b[0], c[0])) + 1)
    y0, y1 = max(0, int(min(a[1], b[1], c[1]))), min(N - 1, int(max(a[1], b[1], c[1])) + 1)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            sx, sy = x + 0.5, y + 0.5
            w0 = ((b[0] - sx) * (c[1] - sy) - (c[0] - sx) * (b[1] - sy)) / area
            w1 = ((c[0] - sx) * (a[1] - sy) - (a[0] - sx) * (c[1] - sy)) / area
            w2 = 1 - w0 - w1
            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                yield x, y, w0 * a[2] + w1 * b[2] + w2 * c[2]
def scene(dgap, two=True):
    t = sphere(DX / 2, dgap, R, "N", "body") + sphere(DX / 2, dgap, R + W, "N", "hull")
    if two: t += sphere(-DX / 2, 0.0, R, "F", "body") + sphere(-DX / 2, 0.0, R + W, "F", "hull")
    return t
def zbuf(tris):
    img = {}; dep = {}
    for tr in tris:
        lab = (tr[1], tr[2])
        for x, y, z in raster(tr[0]):
            if z > dep.get((x, y), -1e9): dep[(x, y)] = z; img[(x, y)] = lab
    return img
def paint(tris, key):
    img = {}
    for tr in sorted(tris, key=key):
        lab = (tr[1], tr[2])
        for x, y, z in raster(tr[0]): img[(x, y)] = lab
    return img
centroid = lambda tr: sum(p[2] for p in tr[0]) / 3
per_object = lambda tr: (tr[3], 0 if tr[2] == "hull" else 1, centroid(tr))
def score(ref, img):
    wrong = sum(1 for k in ref if img.get(k) != ref[k])
    def frac(lab):
        ks = [k for k in ref if ref[k] == lab]
        return sum(img.get(k) != lab for k in ks), len(ks)
    return wrong, frac(("N", "hull")), frac(("N", "body"))


def backdrop():
    L = 1.6; z = lambda x, y: y            # tilted plane z = y
    q = [(-L, -L), (L, -L), (L, L), (-L, L)]
    P = [(x, y, z(x, y)) for x, y in q]
    return [([P[0], P[1], P[2]], "G", "body", -99.0), ([P[0], P[2], P[3]], "G", "body", -99.0)]
CLEAR = 1.0                                 # centre-to-plane offset along z; hull (0.66) clears the plane
single = scene(1.0, two=False); r1 = zbuf(single)
s_wrong = score(r1, paint(single, centroid))[0]
print(f"single sphere: centroid-sort wrong px {s_wrong} of {len(r1)}")
rows = []
for dgap in (0.5, 0.9, 1.2, 1.6, 2.5):
    tris = scene(dgap); ref = zbuf(tris)
    wc, (oh, on), (bh, bn) = score(ref, paint(tris, centroid))
    wp = score(ref, paint(tris, per_object))[0]
    rows.append((dgap, math.hypot(DX, dgap) > 2 * R, wc, wp))
    print(f"A gap {dgap:3.1f} disjoint={rows[-1][1]!s:5} centroid wrong {wc:3d} px (outline {oh}/{on}, body {bh}/{bn}); per-object wrong {wp}")
A_ok = all(r[2] == 0 for r in rows if r[1])
B = []
for ys in (-1.0, -0.5, 0.0, 0.5, 1.0):
    for xs in (-1.0, -0.5, 0.0, 0.5, 1.0):
        zc = ys + CLEAR
        tris = sphere(xs, zc, R, "N", "body") + sphere(xs, zc, R + W, "N", "hull") + backdrop()
        tris = [((tuple((p[0], p[1] + ys, p[2]) for p in t[0]) if t[1] == "N" else t[0]), t[1], t[2], t[3]) for t in tris]
        ref = zbuf(tris)
        wc, (oh, on), (bh, bn) = score(ref, paint(tris, centroid))
        wp = score(ref, paint(tris, per_object))[0]
        B.append((xs, ys, oh, on, bh, bn, wp))
for ys in (1.0, 0.5, 0.0, -0.5, -1.0):
    print(f"B y={ys:+.1f} " + "  ".join(f"x{r[0]:+.1f}: out {r[2]:3d}/{r[3]} body {r[4]:4d}/{r[5]}" for r in B if r[1] == ys))
out_only = sum(1 for r in B if r[2] > 0 and r[4] == 0)
body_only = sum(1 for r in B if r[4] > 0 and r[2] == 0)
both = sum(1 for r in B if r[2] > 0 and r[4] > 0)
clean = sum(1 for r in B if r[2] == 0 and r[4] == 0)
frac_ok = all(r[2] / r[3] >= r[4] / r[5] for r in B if r[2] + r[4] > 0)
po = max(r[6] for r in B)
out_tot = sum(r[2] for r in B) / sum(r[3] for r in B); body_tot = sum(r[4] for r in B) / sum(r[5] for r in B)
ok = s_wrong == 0 and out_only > body_only and frac_ok and po == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} A (two disjoint spheres): centroid exact at all disjoint gaps={A_ok}; "
      f"B (sphere over tilted backdrop, 25 positions): outline-only erased {out_only}, body-only {body_only}, both {both}, clean {clean}; "
      f"pooled wrong outline {out_tot:.1%} vs body {body_tot:.1%}; outline frac>=body at every failing position {frac_ok}; per-object max wrong {po}")
