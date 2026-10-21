"""Dead reckoning with the aviation 1-in-60 rule. Plane geometry, deterministic.
Rule: a heading error of e degrees puts you e/60 of the distance flown off track, and correcting to a destination
d_rem further on needs an extra e_off*60/d_rem... degrees (track error angle + closing angle).
Compare with exact trigonometry; find the error where the rule stops being within 5 and 10 percent."""
import math
def off_exact(d, e): return d * math.sin(math.radians(e))
def off_rule(d, e): return d * e / 60.0
print("heading err deg | rule/exact off-track ratio (distance flown independent)")
bounds = {}
for e in (1, 2, 5, 10, 15, 20, 30, 45, 60):
    ratio = off_rule(1, e) / off_exact(1, e)
    print(f"  {e:>2} | {ratio:.4f}")
    for lim in (0.05, 0.10):
        if abs(ratio - 1) > lim and lim not in bounds: bounds[lim] = e
print("first error angle in the list where rule is off by more than 5 percent / 10 percent:", bounds.get(0.05), bounds.get(0.10))
# two-leg correction: fly d1 at heading error e, then correct to reach the destination at distance D along intended track.
def final_miss(D, d1, e, use_rule):
    ex = d1 * math.cos(math.radians(e)); ey = d1 * math.sin(math.radians(e))      # position after leg 1 (intended track = +x axis)
    rem = D - ex
    if use_rule:
        off = d1 * e / 60.0; d_rem = D - d1
        corr = off * 60.0 / d_rem          # close-the-gap angle toward destination (degrees)
        ang = -corr                          # turn back toward track
        ex2 = ex + (D - d1) * math.cos(math.radians(ang)); ey2 = off + (D - d1) * math.sin(math.radians(ang))
        return math.hypot(ex2 - D, ey2)
    ang = math.degrees(math.atan2(-ey, rem))
    ex2 = ex + (D - d1) * math.cos(math.radians(ang)); ey2 = ey + (D - d1) * math.sin(math.radians(ang))
    return math.hypot(ex2 - D, ey2)
print("destination 120 nm, error flown 40 nm: miss (nm) by heading error  rule angle vs exact-bearing angle, both flying the planned leg length (by time)")
res = []
for e in (3, 6, 12, 25, 40):
    r = final_miss(120, 40, e, True); x = final_miss(120, 40, e, False)
    res.append((e, r, x)); print(f"  e={e:>2}: rule {r:6.2f}  exact {x:6.2f}")
# BREAK: short remaining distance (d_rem small) makes the 'close the gap' angle large
print("BREAK d_rem 10 nm after 110 nm flown at 6 deg error:", round(final_miss(120, 110, 6, True), 2), "vs exact", round(final_miss(120, 110, 6, False), 2))
ok = bounds.get(0.05) and bounds.get(0.10) and res[0][1] < 0.3 and res[-1][1] > 1.0 and final_miss(120, 110, 6, True) > 1.0
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" bounds {bounds}; miss rule/exact e3 {res[0][1]:.2f}/{res[0][2]:.2f}, e40 {res[-1][1]:.2f}/{res[-1][2]:.2f}")
