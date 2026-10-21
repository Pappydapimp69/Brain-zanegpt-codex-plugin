"""Kernel sandbox: ideas:GARDEN/drip-irrigation-efficiency-plus-design-specs (0.5-1.0 gph inline emitters at 12-18 in) against soil
texture from 2026-10-09__home-soil-jar-test-stokes-timing-and-leaf-triage-order/E1 (40/40/20 loam, sandy, clayey jar-test classes) and
the mulch need factor 0.58 from the zoning entry (brainwork/E112 neighbourhood; mulch kernel ideas:GARDEN/mulch-benefits-and-stem-clearance-rule).
Model: wetted bulb = half ellipsoid, horizontal radius a, depth a/lam; volume V = Q*t = (2/3) pi a^2 (a/lam) theta  -> a = (3 V lam /(2 pi theta))^(1/3).
Assumed soil constants (not measured): theta (usable storage cm3/cm3) sand 0.08 loam 0.17 clay 0.18; lam (lateral/vertical spread) sand 0.6 loam 1.0 clay 1.4.
Prediction (before run): (1) 0.5 gph at 18 in spacing for 1 h leaves a dry gap (a < 9 in) in all three soils; (2) 1.0 gph for 2 h at 12 in spacing
bridges (a >= 6 in) in all three; (3) sand loses a larger share of the bulb below a 12 in root zone than loam or clay at 1 gph 2 h (more than 40% vs under 25%);
(4) the hours needed to bridge 18 in at 1 gph are longest for loam among the three (loam has neither sand's deep spread nor clay's wide spread... but
with these constants sand and clay are close), and are within 15% of each other across soils; (5) BREAK: with mulch (needed volume x0.58) the bridge time
for 18 in at 1 gph shortens by about 42% in every soil."""
import math
SOIL = {"sand": (0.08, 0.6), "loam": (0.17, 1.0), "clay": (0.18, 1.4)}
GPH_CM3 = 3785.41
IN = 2.54
def radius_in(soil, gph, hours):
    th, lam = SOIL[soil]
    V = gph * GPH_CM3 * hours
    return (3 * V * lam / (2 * math.pi * th)) ** (1 / 3) / IN
def deep_share(soil, gph, hours, root_in=12.0):
    a = radius_in(soil, gph, hours); b = a / SOIL[soil][1]
    if b <= root_in: return 0.0
    # share of half-ellipsoid volume deeper than root_in: V(z>root)/V = (1 - 1.5 u + 0.5 u^3) with u = root/b... for z measured from surface
    u = root_in / b
    below = 1 - (1.5 * u - 0.5 * u ** 3)
    return below
def bridge_hours(soil, gph, spacing_in, need=1.0):
    lo, hi = 0.01, 48.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if radius_in(soil, gph, mid * need) >= spacing_in / 2: hi = mid
        else: lo = mid
    return hi
for s in SOIL:
    print(f"{s:5s} a(0.5gph,1h)={radius_in(s,0.5,1):.1f}in a(1gph,2h)={radius_in(s,1,2):.1f}in deep share(1gph,2h)={deep_share(s,1,2)*100:.0f}% bridge18@1gph={bridge_hours(s,1,18):.2f}h bridge12@0.5gph={bridge_hours(s,0.5,12):.2f}h")
p1 = all(radius_in(s, 0.5, 1) < 9 for s in SOIL)
p2 = all(radius_in(s, 1, 2) >= 6 for s in SOIL)
p3 = deep_share("sand", 1, 2) > 0.40 and max(deep_share("loam", 1, 2), deep_share("clay", 1, 2)) < 0.25
bh = {s: bridge_hours(s, 1, 18) for s in SOIL}
spread = (max(bh.values()) - min(bh.values())) / min(bh.values())
p4 = max(bh, key=bh.get) == "loam" and spread < 0.15
bm = {s: bridge_hours(s, 1, 18, need=0.58) for s in SOIL}
cut = {s: 1 - bm[s] / bh[s] for s in SOIL}
print("mulch bridge-time cut: " + " ".join(f"{s}={v*100:.0f}%" for s, v in cut.items()) + f"; bridge spread across soils {spread*100:.0f}%")
p5 = all(0.38 < v < 0.46 for v in cut.values())
held = [p1, p2, p3, p4, p5]
print("== POST-HOC (excluded from RESULT; written after P5 failed) ==")
print("P5 premise was wrong: need=0.58 multiplies the run time, so the bridge time grew (x1/0.58 = +72%) instead of shrinking; the bulb radius depends only on the applied volume, so mulch cannot change bridging, it only stretches the interval between runs.")
print("interval stretch from mulch at the same bulb: x%.2f" % (1/0.58))
dd = max(deep_share(s, 1, 6) for s in SOIL)
print("deep share at 1 gph 6 h: " + " ".join(f"{s}={deep_share(s,1,6)*100:.0f}%" for s in SOIL))
print("held:", held)
print(f"RESULT: {'PASS' if all(held) else 'FAIL'} {sum(held)}/5 predictions held")
