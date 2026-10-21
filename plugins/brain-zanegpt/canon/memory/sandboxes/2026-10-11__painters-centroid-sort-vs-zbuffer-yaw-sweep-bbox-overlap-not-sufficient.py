"""PREDICTION (before first run): two triangles that truly pierce (A flat at z=0, B leaning from z=-14 to z=+14), orthographic
raster 96x96, camera yaw swept 0..170 deg in 10-deg steps. (1) the 3D bounding boxes overlap at EVERY yaw (necessary condition
holds always); (2) at yaw 0 neither draw order is correct (both wrong-pixel counts > 0) and the centroid sort picks the lesser
order; (3) at some yaws the visible overlap is empty or one order is exactly right (0 wrong), so bbox overlap is not sufficient
for a visible artifact; (4) the centroid sort is wrong (>0 px) at >= 3 yaws; (5) a control pair translated apart (no bbox
overlap) has 0 wrong pixels at every yaw for the centroid sort. Stdlib only, deterministic."""
import math
A = [(-10, -10, 0), (10, -10, 0), (0, 12, 0)]
B = [(-9, -8, -14), (9, -8, -14), (0, 9, 14)]
W = 96
def rot(p, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    x, y, z = p
    return (c * x + s * z, y, -s * x + c * z)   # yaw about the vertical axis; z toward the camera
def raster(tri, deg):
    P = [rot(p, deg) for p in tri]
    px = {}
    pts = [(48 + 2.0 * x, 48 - 2.0 * y, z) for x, y, z in P]
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = pts
    d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(d) < 1e-9: return px
    for j in range(W):
        for i in range(W):
            X, Y = i + .5, j + .5
            a = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / d
            b = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / d
            c = 1 - a - b
            if a >= 0 and b >= 0 and c >= 0: px[(i, j)] = a * z0 + b * z1 + c * z2
    return px
def centroid_z(tri, deg): return sum(rot(p, deg)[2] for p in tri) / 3
def bbox_overlap(t1, t2):
    return all(max(p[k] for p in t1) >= min(p[k] for p in t2) and max(p[k] for p in t2) >= min(p[k] for p in t1) for k in range(3))
def wrong(t1, t2, deg):
    """returns (wrong px drawing t1 then t2, t2 then t1, centroid order, overlap px count)"""
    r1, r2 = raster(t1, deg), raster(t2, deg)
    both = set(r1) & set(r2)
    truth = {k: (1 if r1[k] > r2[k] else 2) for k in both}   # larger z is nearer
    w12 = sum(1 for k in both if truth[k] != 2)   # draw t1 then t2 -> t2 visible
    w21 = sum(1 for k in both if truth[k] != 1)
    cen = w12 if centroid_z(t1, deg) <= centroid_z(t2, deg) else w21   # nearer centroid drawn last
    return w12, w21, cen, len(both)
rows = []
for deg in range(0, 180, 10):
    rows.append((deg, bbox_overlap([rot(p, deg) for p in A], [rot(p, deg) for p in B]),) + wrong(A, B, deg))
for r in rows: print("yaw %3d bbox=%s wrongAB=%4d wrongBA=%4d centroid=%4d overlap_px=%4d" % r)
Bf = [(x + 60, y, z) for x, y, z in B]
ctrl = [wrong(A, Bf, d)[2] for d in range(0, 180, 10)]
c1 = all(r[1] for r in rows)
c2 = rows[0][2] > 0 and rows[0][3] > 0 and rows[0][4] == min(rows[0][2], rows[0][3])
c3 = any(min(r[2], r[3]) == 0 or r[5] == 0 for r in rows)
c4 = sum(1 for r in rows if r[4] > 0) >= 3
c5 = all(v == 0 for v in ctrl)
print("conds", c1, c2, c3, c4, c5, "control_max", max(ctrl))
print("RESULT:", "PASS" if all([c1, c2, c3, c4, c5]) else "FAIL",
      "bbox_overlap_all=%s yaw0 wrongAB=%d wrongBA=%d centroid=%d; yaws with a zero-wrong order=%d; centroid wrong at %d/%d yaws; control max=%d"
      % (c1, rows[0][2], rows[0][3], rows[0][4], sum(1 for r in rows if min(r[2], r[3]) == 0 or r[5] == 0),
         sum(1 for r in rows if r[4] > 0), len(rows), max(ctrl)))
