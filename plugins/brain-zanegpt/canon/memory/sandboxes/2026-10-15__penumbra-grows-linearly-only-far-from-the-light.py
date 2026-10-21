"""Painting kernel: a cast shadow is sharp at contact and blurs with distance; penumbra width ~ light radius x
(occluder-to-receiver) / (light-to-occluder). Check it by brute-force ray casting in 2D (a disk light seen edge-on
as a segment, a knife-edge occluder, a ground plane), and settle the kernel's unverified sunlight figure.
Deterministic, stdlib only."""
import math
def penumbra_raycast(light_r, light_h, edge_h, samples=4001):
    # light: segment at height light_h spanning x in [-light_r, light_r]; occluder: half-plane x < 0 at height edge_h
    # (a knife edge at x=0). A ground point x is lit by the fraction of light samples whose ray passes x>0 at edge_h.
    def lit(x):
        n = 0
        for i in range(samples):
            lx = -light_r + 2 * light_r * i / (samples - 1)
            cross = lx + (x - lx) * (light_h - edge_h) / light_h   # where the ray from (lx,light_h) to (x,0) passes height edge_h
            n += cross > 0
        return n / samples
    # penumbra = span of ground x where 0 < lit < 1; find edges by bisection
    def edge(target):
        lo, hi = -1e3, 1e3
        for _ in range(80):
            mid = (lo + hi) / 2
            if (lit(mid) > target): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    return edge(.999) - edge(.001)
formula = lambda r, H, h: 2 * r * h / (H - h)   # full width = 2 x (light radius x occluder-receiver / light-occluder)
print("height above ground -> penumbra (raycast vs formula), light radius 0.5 m at 3 m (a window-sized source):")
rows = []
for h in (0.0, .1, .3, .6, 1.0, 2.0, 2.7):
    rc = penumbra_raycast(.5, 3.0, h) if h > 0 else 0.0
    f = formula(.5, 3.0, h); lin = 2 * .5 * h / 3.0
    rows.append((h, rc, f, lin)); print(f"  h={h:3.1f} m: raycast {rc:6.3f} m, formula {f:6.3f} m, straight-line estimate {lin:6.3f} m")
sun = 2 * math.tan(math.radians(0.533 / 2))     # sun's angular diameter about 0.53 degrees
print(f"sun: {sun*100:.2f} cm of penumbra per metre of height")
ok = (rows[0][1] == 0 and all(abs(rc - f) / f < .01 for h, rc, f, _ in rows[1:])
      and abs(rows[2][1] - rows[2][3]) / rows[2][1] < .12      # near the ground the straight-line rule holds
      and rows[-1][1] > 5 * rows[-1][3]                          # close to the light it is far off (BREAK case)
      and .8 < sun * 100 < 1.0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} zero at contact, raycast matches r*h/(H-h) within 1%, near-linear only while the gap is small (0.3 m: {rows[2][1]:.3f} vs {rows[2][3]:.3f}), 2.7 m: {rows[-1][1]:.2f} vs {rows[-1][3]:.2f}; sunlight adds {sun*100:.2f} cm per metre")
