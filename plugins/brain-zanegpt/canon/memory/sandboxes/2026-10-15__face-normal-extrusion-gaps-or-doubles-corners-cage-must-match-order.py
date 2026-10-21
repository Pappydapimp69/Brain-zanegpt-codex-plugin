"""2D high-to-low normal bake: rays cast from the low poly inward to the sculpt.

Low poly: square, half-size 1, four hard-edged faces (split normals), 256
texels per face. High-poly sculpts (star-shaped implicit r(theta)):
  S1 rounded: r = 1.12 + 0.03 sin(12 theta)  (inside the low poly's corners,
     outside its mid-faces)
  S2 boxy: superellipse n=20, a=1.10, times (1 + 0.01 sin(12 theta))
     (outside the low poly everywhere, including past its corners)
Ray setups:
  none      origin on the low poly, face normal, max distance 0.5
  extrude   origin pushed 0.3 along the FACE normal (split), max distance 0.6
  cage      explicit cage: low-poly corners scaled by (1+c), same vertex order;
            origin = lerp on cage edge, direction = toward the matching low-poly
            point (averaged at corners), max = |P-O| + 0.3
  cage-rot  BREAK: same cage but its vertex list rotated by one (face order
            differs from the low poly)
Hit = first outside->inside crossing of the sculpt, refined by bisection.
Metrics: hit rate; largest angular gap between consecutive hit angles on the
sculpt; overlap/gap between adjacent faces' hit-angle intervals (doubling or
missing detail at the hard edge); wrong hits (> 0.5 from the texel); max skew
of the ray from the face normal.
"""
import math

N_TEX = 256
LOW = [(1.0, -1.0), (1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0)]
NORMALS = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]


def r_s1(th):
    return 1.12 + 0.03 * math.sin(12 * th)


def r_s2(th):
    c, s = abs(math.cos(th)), abs(math.sin(th))
    n, a = 20.0, 1.10
    return a / (c ** n + s ** n) ** (1 / n) * (1 + 0.01 * math.sin(12 * th))


def inside(rfun, x, y):
    return math.hypot(x, y) < rfun(math.atan2(y, x))


def cast(rfun, ox, oy, dx, dy, tmax, step=0.002):
    if inside(rfun, ox, oy):
        return None  # ray starts inside the sculpt: no front-face hit
    t = 0.0
    while t < tmax:
        t2 = min(t + step, tmax)
        if inside(rfun, ox + dx * t2, oy + dy * t2):
            lo, hi = t, t2
            for _ in range(30):
                mid = (lo + hi) / 2
                if inside(rfun, ox + dx * mid, oy + dy * mid):
                    hi = mid
                else:
                    lo = mid
            return (ox + dx * hi, oy + dy * hi)
        t = t2
    return None


def texels():
    for f in range(4):
        (x0, y0), (x1, y1) = LOW[f], LOW[(f + 1) % 4]
        for k in range(N_TEX):
            u = (k + 0.5) / N_TEX
            yield f, u, (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)


def bake(rfun, mode, c=0.3, rot=0, ext_tmax=0.6):
    hits = []  # (face, P, hit, skew)
    cage = [((1 + c) * x, (1 + c) * y) for (x, y) in LOW]
    cage = cage[rot:] + cage[:rot]
    for f, u, (px, py) in texels():
        nx, ny = NORMALS[f]
        if mode == "none":
            o, d, tmax = (px, py), (-nx, -ny), 0.5
        elif mode == "extrude":
            o, d, tmax = (px + 0.3 * nx, py + 0.3 * ny), (-nx, -ny), ext_tmax
        else:
            (cx0, cy0), (cx1, cy1) = cage[f], cage[(f + 1) % 4]
            o = (cx0 + (cx1 - cx0) * u, cy0 + (cy1 - cy0) * u)
            vx, vy = px - o[0], py - o[1]
            L = math.hypot(vx, vy)
            d, tmax = (vx / L, vy / L), L + 0.3
        h = cast(rfun, o[0], o[1], d[0], d[1], tmax)
        skew = math.degrees(math.acos(max(-1, min(1, -(d[0] * nx + d[1] * ny)))))
        hits.append((f, (px, py), h, skew))
    return hits


def metrics(hits):
    got = [x for x in hits if x[2] is not None]
    rate = len(got) / len(hits)
    angs = sorted(math.degrees(math.atan2(h[1], h[0])) % 360 for _, _, h, _ in got)
    gap = 0.0
    if angs:
        for a, b in zip(angs, angs[1:] + [angs[0] + 360]):
            gap = max(gap, b - a)
    # per-face angular interval, unwrapped around the face's own centre angle
    centre = [0.0, 90.0, 180.0, 270.0]
    iv = {}
    for f, _, h, _ in got:
        a = math.degrees(math.atan2(h[1], h[0]))
        a = (a - centre[f] + 180) % 360 - 180 + centre[f]
        lo, hi = iv.get(f, (a, a))
        iv[f] = (min(lo, a), max(hi, a))
    seams = []
    for f in range(4):
        g = (f + 1) % 4
        if f in iv and g in iv:
            hi_f = iv[f][1]
            lo_g = iv[g][0] + (360 if g == 0 else 0)
            seams.append(hi_f - lo_g)  # >0 overlap (doubled detail), <0 gap (missed)
    wrong = sum(1 for _, p, h, _ in got if math.hypot(h[0] - p[0], h[1] - p[1]) > 0.5) / len(hits)
    skew = max(s for *_, s in hits)
    return {"rate": rate, "gap": gap, "seam_min": min(seams) if seams else float("nan"),
            "seam_max": max(seams) if seams else float("nan"), "wrong": wrong, "skew": skew}


def show(name, m):
    print(f"{name:22s} hits {m['rate'] * 100:5.1f}%  max angular gap {m['gap']:6.2f} deg  "
          f"seam overlap(+)/gap(-) {m['seam_min']:7.2f}..{m['seam_max']:7.2f} deg  "
          f"wrong {m['wrong'] * 100:5.1f}%  skew max {m['skew']:5.1f} deg")


def main():
    ok = True
    R = {}
    for sname, rf in (("S1", r_s1), ("S2", r_s2)):
        for mode in ("none", "extrude", "cage"):
            m = metrics(bake(rf, mode))
            R[(sname, mode)] = m
            show(f"{sname} {mode}", m)
        m = metrics(bake(rf, "cage", rot=1))
        R[(sname, "cagerot")] = m
        show(f"{sname} cage-rot (BREAK)", m)
    for c in (0.02, 0.05, 0.08, 0.12):
        m = metrics(bake(r_s2, "cage", c=c))
        R[("S2", "cage", c)] = m
        show(f"S2 cage c={c}", m)

    # added after run 1 (criteria below unchanged): longer max ray distance for the extrusion
    for sname, rf in (("S1", r_s1), ("S2", r_s2)):
        m = metrics(bake(rf, "extrude", ext_tmax=1.0))
        R[(sname, "extrude1")] = m
        show(f"{sname} extrude max 1.0", m)

    ok &= 0.35 <= R[("S1", "none")]["rate"] <= 0.65
    ok &= R[("S1", "extrude")]["rate"] > 0.99 and R[("S2", "extrude")]["rate"] > 0.99
    ok &= R[("S1", "extrude")]["seam_min"] > 0  # doubled detail at every corner
    ok &= R[("S2", "extrude")]["seam_max"] < -5.0  # missed wedge > 5 deg at every corner
    for s in ("S1", "S2"):
        ok &= R[(s, "cage")]["rate"] > 0.99 and R[(s, "cage")]["gap"] < 1.0
    ok &= R[("S1", "cagerot")]["wrong"] > 0.5 and R[("S2", "cagerot")]["wrong"] > 0.5
    ok &= R[("S2", "cage", 0.02)]["rate"] < 1.0
    s2c = R[("S2", "cage")]
    print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
          f"none S1 {R[('S1', 'none')]['rate'] * 100:.1f}% hits; face-normal extrude S1 corners doubled "
          f"{R[('S1', 'extrude')]['seam_min']:.1f}..{R[('S1', 'extrude')]['seam_max']:.1f} deg, S2 corners missed "
          f"{-R[('S2', 'extrude')]['seam_max']:.1f}..{-R[('S2', 'extrude')]['seam_min']:.1f} deg "
          f"(max gap {R[('S2', 'extrude')]['gap']:.2f}); S1 extrude hits {R[('S1', 'extrude')]['rate'] * 100:.1f}% at max 0.6, "
          f"{R[('S1', 'extrude1')]['rate'] * 100:.1f}% at max 1.0 with corners doubled {R[('S1', 'extrude1')]['seam_min']:.1f} deg; matched cage S1/S2 max gap "
          f"{R[('S1', 'cage')]['gap']:.2f}/{s2c['gap']:.2f} deg at skew {s2c['skew']:.1f} deg; "
          f"rotated cage wrong {R[('S1', 'cagerot')]['wrong'] * 100:.0f}%/{R[('S2', 'cagerot')]['wrong'] * 100:.0f}%; "
          f"S2 cage c=0.02/0.05/0.08/0.12 hits "
          + "/".join(f"{R[('S2', 'cage', c)]['rate'] * 100:.1f}" for c in (0.02, 0.05, 0.08, 0.12)) + "%")


if __name__ == "__main__":
    main()
