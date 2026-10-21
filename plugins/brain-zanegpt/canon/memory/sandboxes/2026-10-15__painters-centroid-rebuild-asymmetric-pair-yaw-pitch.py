"""Rebuild of painters-centroid-sort-vs-zbuffer-yaw-sweep-bbox-overlap-not-sufficient E1 with my own fixture.
Fixture: big tilted triangle A (plane z = 0.3 x) and a SMALL asymmetric triangle B piercing it off-centre;
128x128 orthographic raster over [-50,50]^2, pixel-centre sampling; rotations: yaw sweep 0..345 step 15 AND
a pitch sweep 0..345 step 15. Larger camera z = nearer. Truth = per-pixel depth test.
Controls: (C1) B lifted so it no longer pierces but 3D boxes still overlap -> some whole order must be exact;
(C2) B moved 90 units away (separated).
PREDICTION (written before running): boxes overlap in every view for the piercing pair; the centroid sort is
wrong on >0 pixels in every view whose screen overlap is >= 5 px, and 0 only where overlap is ~0 (edge-on);
unlike E1's symmetric pair, the centroid picks the WORSE of the two orders in at least 1 view; C1 has an
exact order in every view (0 wrong) and the centroid still gets C1 wrong in at least 1 view.
"""
import math

N = 128
LO, HI = -50.0, 50.0


def plane_tri(xy):
    return [(x, y, 0.3 * x) for x, y in xy]


A = plane_tri([(-34, -26), (36, -22), (2, 38)])
B = [(6.0, -4.0, -14.0), (16.0, 9.0, 13.0), (-7.0, 7.0, 11.0)]
B_lift = [(x, y, z + 30.0) for x, y, z in B]  # check below that it no longer straddles A's plane
B_far = [(x + 90.0, y, z) for x, y, z in B]


def rot(p, yaw, pitch):
    x, y, z = p
    cy, sy = math.cos(yaw), math.sin(yaw)
    x, z = cy * x + sy * z, -sy * x + cy * z
    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = cp * y - sp * z, sp * y + cp * z
    return (x, y, z)


def raster(tri):
    """dict pixel -> depth"""
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    out = {}
    if abs(den) < 1e-9:
        return out
    step = (HI - LO) / N
    for j in range(N):
        py = LO + (j + 0.5) * step
        for i in range(N):
            px = LO + (i + 0.5) * step
            a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            c = 1 - a - b
            if a >= 0 and b >= 0 and c >= 0:
                out[(i, j)] = a * z0 + b * z1 + c * z2
    return out


def bbox_overlap(t1, t2):
    for k in range(3):
        if max(p[k] for p in t1) < min(p[k] for p in t2) or max(p[k] for p in t2) < min(p[k] for p in t1):
            return False
    return True


def view(t1, t2, yaw, pitch):
    r1 = [rot(p, yaw, pitch) for p in t1]
    r2 = [rot(p, yaw, pitch) for p in t2]
    d1, d2 = raster(r1), raster(r2)
    ov = d1.keys() & d2.keys()
    t1_near = sum(1 for k in ov if d1[k] > d2[k])  # pixels where t1 should be on top
    t2_near = len(ov) - t1_near
    wrong_t1_last = t2_near  # draw t2 then t1: t1 on top everywhere -> wrong where t2 is nearer
    wrong_t2_last = t1_near
    c1 = sum(p[2] for p in r1) / 3
    c2 = sum(p[2] for p in r2) / 3
    centroid = wrong_t1_last if c1 > c2 else wrong_t2_last  # nearer centroid drawn last
    return len(ov), wrong_t1_last, wrong_t2_last, centroid


def side(tri, p):  # sign relative to A's plane z - 0.3x
    return p[2] - 0.3 * p[0]


straddle = [side(A, p) for p in B]
straddle_lift = [side(A, p) for p in B_lift]
print("B signed dist to A plane:", [round(s, 1) for s in straddle], " lifted:", [round(s, 1) for s in straddle_lift])
pierces = min(straddle) < 0 < max(straddle)
lift_clear = min(straddle_lift) > 0

angles = [math.radians(15 * k) for k in range(24)]
views = [("yaw", a, 0.0) for a in angles] + [("pitch", 0.0, a) for a in angles]

ok = pierces and lift_clear
stats = dict(n=0, bbox=0, ovviews=0, cent_wrong_on_ov=0, worse=0, zero_with_ov=0, minwrong=None)
rows = []
for kind, yw, pt in views:
    ra = [rot(p, yw, pt) for p in A]
    rb = [rot(p, yw, pt) for p in B]
    ov, w1, w2, cw = view(A, B, yw, pt)
    stats["n"] += 1
    stats["bbox"] += bbox_overlap(ra, rb)
    if ov >= 5:
        stats["ovviews"] += 1
        stats["cent_wrong_on_ov"] += cw > 0
        if min(w1, w2) == 0:
            stats["zero_with_ov"] += 1
        if stats["minwrong"] is None or cw < stats["minwrong"][0]:
            stats["minwrong"] = (cw, ov, kind, round(math.degrees(yw + pt)))
    if ov < 5:
        print(f"  low-overlap view {kind} {round(math.degrees(yw + pt))}: overlap {ov}, centroid wrong {cw}")
    if cw > min(w1, w2):
        stats["worse"] += 1
        rows.append((kind, round(math.degrees(yw + pt)), ov, w1, w2, cw))
    if kind == "yaw" and round(math.degrees(yw)) in (0, 45, 90, 135):
        print(f"  yaw {round(math.degrees(yw)):3d}: overlap {ov:4d}  A-last wrong {w1:4d}  B-last wrong {w2:4d}  centroid {cw:4d}")

print("piercing pair:", stats)
print("views where centroid picked the WORSE order:", rows)

# controls
c1_exact = c1_cent_wrong = c1_ovviews = 0
c2_wrong = c2_ov = 0
for kind, yw, pt in views:
    ov, w1, w2, cw = view(A, B_lift, yw, pt)
    if ov >= 5:
        c1_ovviews += 1
        c1_exact += min(w1, w2) == 0
        c1_cent_wrong += cw > 0
    ov2, _, _, cw2 = view(A, B_far, yw, pt)
    c2_ov += ov2 > 0
    c2_wrong += cw2
c1_bbox = sum(bbox_overlap([rot(p, y, q) for p in A], [rot(p, y, q) for p in B_lift]) for _, y, q in views)
print(f"C1 lifted (non-piercing): bbox overlap {c1_bbox}/{len(views)}, views with overlap>=5: {c1_ovviews}, "
      f"an exact order exists in {c1_exact}, centroid wrong in {c1_cent_wrong}")
print(f"C2 separated: views with any screen overlap {c2_ov}, total centroid wrong {c2_wrong}")

c_all_wrong = stats["cent_wrong_on_ov"] == stats["ovviews"]
ok &= stats["bbox"] == stats["n"] and c_all_wrong and stats["zero_with_ov"] == 0 and c1_exact == c1_ovviews
print(f"RESULT: {'PASS' if ok else 'FAIL'} piercing pair: bbox overlap {stats['bbox']}/{stats['n']} views; centroid wrong "
      f"in {stats['cent_wrong_on_ov']}/{stats['ovviews']} views with overlap>=5 px (min {stats['minwrong']}); centroid "
      f"picked the worse order in {stats['worse']} views; non-piercing control has an exact order in {c1_exact}/{c1_ovviews} "
      f"but centroid wrong in {c1_cent_wrong}; separated control overlaps on screen in {c2_ov}/{len(views)}")
