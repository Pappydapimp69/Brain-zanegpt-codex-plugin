"""Cel loop 9 - toon specular. Roystan's widely copied toon shader (roystan.net/articles/
toon-shader): specularIntensity = pow(NdotH * lightIntensity, _Glossiness * _Glossiness);
specularIntensitySmooth = smoothstep(0.005, 0.01, specularIntensity).
Claims tested (exact maths on a dense grid of N.H, no RNG):
 1. with a hard step, the exponent is redundant: step(t, x^s) == step(t^(1/s), x) for x in [0,1];
 2. with the fixed smoothstep(0.005, 0.01) edge, glossiness sets highlight SIZE and EDGE
    SOFTNESS together: highlight angular radius (where intensity = 0.5) and edge width
    (angle between intensity 0 and 1) for glossiness g = 4, 8, 16, 32 (s = g^2).
PREDICTION (written before running): claim 1 holds on 100% of grid points for every (s, t);
in claim 2 the edge width falls with glossiness roughly in proportion to the radius, so
edge/radius stays within 0.5x-2x across g = 4..32 (size and softness locked together)."""
import math
xs = [i / 20000 for i in range(20001)]
ident = True
for s in (2, 8, 32, 128, 1024):
    for t in (0.01, 0.1, 0.5, 0.9):
        a = [x ** s >= t for x in xs]; b = [x >= t ** (1 / s) for x in xs]
        ident &= (a == b)
print("hard step: step(t, x^s) == step(t^(1/s), x) on every grid point:", ident)
def angle_at(level, s):          # N.H at which x^s == level  ->  angle in degrees
    return math.degrees(math.acos(level ** (1 / s)))
def smooth_profile(s):
    lo, hi = 0.005, 0.01
    r_half = angle_at((lo + hi) / 2, s)                 # smoothstep's midpoint (0.5 output) at x^s = 0.0075
    edge = angle_at(lo, s) - angle_at(hi, s)            # angular width of the soft edge
    return r_half, edge
rows = {}
for g in (4, 8, 16, 32):
    s = g * g; r, e = smooth_profile(s); rows[g] = (r, e, e / r)
    print(f"glossiness {g:2d} (power {s:4d}): highlight radius {r:6.2f} deg, soft edge {e:5.2f} deg, edge/radius {e / r:.3f}")
ratios = [v[2] for v in rows.values()]
locked = max(ratios) / min(ratios) <= 4 and all(0.05 < x < 1 for x in ratios)
ok = ident and locked
print(f"RESULT: {'PASS' if ok else 'FAIL'} hard-step exponent redundant on all grid points: {ident}; smoothstep(0.005,0.01): "
      f"radius {rows[4][0]:.1f} -> {rows[32][0]:.1f} deg as glossiness 4 -> 32, edge {rows[4][1]:.2f} -> {rows[32][1]:.2f} deg, "
      f"edge/radius {min(ratios):.3f}-{max(ratios):.3f}")
