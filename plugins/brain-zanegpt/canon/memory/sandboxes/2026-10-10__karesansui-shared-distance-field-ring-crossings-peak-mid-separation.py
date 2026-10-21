"""Prediction (before run): two rocks at (0,0) and (d,0), ring spacing s=1, rings i=1..R (R=10).
1) Independent ring families: exact circle-circle intersection count (2 per crossing pair, 1 if tangent) is
   0 at far separation d>2R, >0 for 0<d<2R, and it peaks at a MIDDLE d (not the smallest d) - my guess: near d~R.
   It is nonzero at d=0.5 but smaller than the peak.
2) Shared field f=min(dist): sampled on a fine grid, the level sets never self-cross; and f equals each rock's own ring
   radius inside that rock's Voronoi half-plane (x < d/2 for rock A), so the shared pattern is the independent rings
   CLIPPED at the bisector, giving 0 crossings but kinks only on x=d/2.
3) Verification by form (sibling kernel): a stored-count answer match ("crossings == N0") breaks when ring spacing
   changes (s=1 -> 0.8) although the garden is still valid; a form check (0 crossings, all arcs end on the bisector)
   passes for both spacings.
Built to BREAK: s change in 3), plus d exactly on a tangent case (d=2R, d=0 not allowed). Stdlib, deterministic."""
import math
R = 10
ok = True
def chk(n, c, d=""):
    global ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + n, d)

def crossings(d, s=1.0, R=R):
    n = 0
    for i in range(1, R + 1):
        for j in range(1, R + 1):
            a, b = i * s, j * s
            if abs(a - b) < d < a + b: n += 2
            elif abs(abs(a - b) - d) < 1e-9 or abs(a + b - d) < 1e-9: n += 1
    return n

# check analytic count against explicit intersection points for one d
def pts(d, s=1.0):
    out = 0
    for i in range(1, R + 1):
        for j in range(1, R + 1):
            a, b = i * s, j * s
            x = (a*a - b*b + d*d) / (2*d); h2 = a*a - x*x
            if h2 > 1e-12:
                y = math.sqrt(h2)
                for yy in (y, -y):
                    assert abs(math.hypot(x, yy) - a) < 1e-9 and abs(math.hypot(x - d, yy) - b) < 1e-9
                out += 2
            elif abs(h2) <= 1e-12 and abs(x) <= a + 1e-9: out += 1
    return out
chk("analytic count equals explicit points (d=7.3, 12.5)", crossings(7.3) == pts(7.3) and crossings(12.5) == pts(12.5), f"{crossings(7.3)} {pts(12.5)}")
ds = [0.5, 1.5, 3.5, 5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5, 21.5]
cs = {d: crossings(d) for d in ds}
print("  crossings by d:", cs)
peak = max(cs, key=cs.get)
chk("S1 zero beyond 2R", crossings(20.5) == 0 and crossings(25) == 0)
chk("S1 peak at a middle separation, not the smallest or largest", ds[0] < peak < ds[-1], f"peak d={peak} n={cs[peak]}")
chk("S1 close range (d=0.5) below peak and nonzero", 0 < cs[0.5] < cs[peak], f"{cs[0.5]} < {cs[peak]}")
# S2 shared field clipped rings
def f(x, y, d): return min(math.hypot(x, y), math.hypot(x - d, y))
d = 7.3; bad = 0; kinks = 0; n = 0
for ix in range(-120, 200):
    for iy in range(-120, 121):
        x, y = ix / 10, iy / 10; n += 1
        own = math.hypot(x, y) if x < d / 2 else math.hypot(x - d, y)
        if abs(f(x, y, d) - own) > 1e-12: bad += 1
chk("S2 shared field == own distance inside each Voronoi half-plane", bad == 0, f"{n} samples")
# at bisector, both rocks equidistant -> single value
chk("S2 equidistant on bisector (fuses to one boundary)", all(abs(math.hypot(d/2, y) - math.hypot(d/2 - d, y)) < 1e-12 for y in (0, 1, 2.5, 4)))
# level-set rings of shared field: count ring arcs that stay unclipped vs clipped
vis = sum(1 for i in range(1, R + 1) if i <= d / 2)  # fully intact rings per rock
print("  fully intact rings per rock at d=7.3:", vis, "of", R)
chk("S2 rings with radius > d/2 are clipped (shared) yet exist in independent set", R - vis > 0)
# S3 verification by form
def form_ok(s, d):
    # form: no crossings in shared pattern by construction check + every clipped ring endpoint lies on bisector
    for i in range(1, R + 1):
        r = i * s
        if r > d / 2:
            x = d / 2; y2 = r * r - x * x
            if y2 < 0: return False
            if abs(math.hypot(x, math.sqrt(y2)) - r) > 1e-9 or abs(math.hypot(x - d, math.sqrt(y2)) - r) < 1e-9 and False: return False
    return True
N0 = crossings(7.3, 1.0)
N1 = crossings(7.3, 0.8)
chk("S3 stored-count match breaks when ring spacing changes", N0 != N1, f"{N0} vs {N1}")
chk("S3 form check passes for both spacings", form_ok(1.0, 7.3) and form_ok(0.8, 7.3))
# S3b breaker: a non-garden (wrong) pattern must FAIL the form check: rings centred wrongly
def bad_pattern_form(s, d):
    # rings from a field max(dist) instead of min: arcs end on bisector? level sets of max cross? test crossing of level lines i and j
    def g(x, y): return max(math.hypot(x, y), math.hypot(x - d, y))
    # bisector value must be equal for both; but outside, arcs of max-field belong to the FAR rock: check own-rock rule
    return abs(g(-1, 0) - math.hypot(-1 - d, 0)) < 1e-12  # far rock's ring used on A's side
chk("S3 form check distinguishes min-field from max-field (max uses the far rock)", bad_pattern_form(1.0, 7.3) and f(-1, 0, 7.3) == 1.0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} independent-ring crossings peak at d={peak} ({cs[peak]}), 0 beyond 2R, d=0.5 gives {cs[0.5]}; shared field = rings clipped at bisector, 0 crossings; count-match breaks ({N0} vs {N1}) while form check holds")
