"""Prediction written first was that the offset copy fits best at side light; run 1 refuted it. Canvas cel-shading recipe: fill the lit tone, clip to the shape, fill an OFFSET COPY of the shape in the shadow
tone to get a hard terminator. For a sphere (a disc on screen), how close is that to the true N.L = 0 terminator,
which projects to a half-ellipse? Grid IoU between the recipe's shadow and the true shadow, best offset searched,
over light directions from frontal to grazing to backlit. Deterministic, stdlib only."""
import math
N = 161
pts = [((i + .5) / N * 2 - 1, (j + .5) / N * 2 - 1) for i in range(N) for j in range(N)]
disc = [(x, y) for x, y in pts if x * x + y * y <= 1]
def true_shadow(L):
    lx, ly, lz = L; out = set()
    for x, y in disc:
        z = math.sqrt(max(0, 1 - x * x - y * y))
        if x * lx + y * ly + z * lz < 0: out.add((x, y))
    return out
def offset_shadow(L, d):
    # shadow = the part of the disc NOT covered by a lit copy shifted toward the light by d (the usual recipe:
    # lit copy offset toward the light, everything else in the disc is shadow)
    lx, ly, _ = L; n = math.hypot(lx, ly) or 1; ox, oy = lx / n * d, ly / n * d
    return {(x, y) for x, y in disc if (x - ox) ** 2 + (y - oy) ** 2 > 1}
def iou(a, b): return len(a & b) / max(1, len(a | b))
def scaled_shadow(L, d, k):
    # variant: the lit copy is also scaled (k = radius of the copy), so its edge can be flatter or rounder
    lx, ly, _ = L; n = math.hypot(lx, ly) or 1; ox, oy = lx / n * d, ly / n * d
    return {(x, y) for x, y in disc if (x - ox) ** 2 + (y - oy) ** 2 > k * k}
def ellipse_shadow(L):
    # the exact construction: the shadow side of the disc is bounded by a half-ellipse with semi-minor |cos theta|
    lx, ly, lz = L; n = math.hypot(lx, ly) or 1; ux, uy = lx / n, ly / n; c = lz
    out = set()
    for x, y in disc:
        a, b = x * ux + y * uy, -x * uy + y * ux          # a: toward the light on screen, b: along the terminator
        e = c * math.sqrt(max(0, 1 - b * b))              # the terminator's offset from the centre at this b
        if a < -e if c >= 0 else a < -e: out.add((x, y))
    return out
print("light angle from the viewer (0 = frontal, 90 = side, 180 = behind)")
res = {}
for deg in (20, 45, 70, 90, 110, 135, 160):
    th = math.radians(deg); L = (math.sin(th), 0, math.cos(th)); T = true_shadow(L)
    plain = max(((iou(offset_shadow(L, d / 100), T), d / 100) for d in range(0, 201, 2)), key=lambda r: r[0])
    scaled = max(((iou(scaled_shadow(L, d / 100, k / 100), T), d / 100, k / 100) for d in range(0, 401, 10) for k in range(60, 401, 10)), key=lambda r: r[0])
    if plain[0] > scaled[0]: scaled = (plain[0], plain[1], 1.0)   # a scale of 1 is the plain copy (the coarse grid can miss it)
    ell = iou(ellipse_shadow(L), T)
    res[deg] = (plain[0], scaled[0], ell)
    print(f"  {deg:3d} deg: shadow {len(T) / len(disc):5.1%}; offset copy IoU {plain[0]:.3f} (d {plain[1]:.2f}); offset+scaled copy {scaled[0]:.3f} (d {scaled[1]:.2f}, r {scaled[2]:.2f}); half-ellipse {ell:.3f}")
mid = [d for d in res if 45 <= d <= 135]
worst_plain = min(r[0] for r in res.values()); mid_scaled = min(res[d][1] for d in mid); worst_ell = min(r[2] for r in res.values())
ok = worst_plain < .85 and mid_scaled > .92 and res[20][1] < .85 and worst_ell > .99
print(f"RESULT: {'PASS' if ok else 'FAIL'} a plain offset copy gets IoU {worst_plain:.3f} at worst ({res[20][0]:.3f} frontal-ish, {res[90][0]:.3f} side); letting it scale lifts 45-135 deg to at least {mid_scaled:.3f} but not the thin frontal crescent ({res[20][1]:.3f}); a half-ellipse terminator is exact at every angle ({worst_ell:.3f})")
