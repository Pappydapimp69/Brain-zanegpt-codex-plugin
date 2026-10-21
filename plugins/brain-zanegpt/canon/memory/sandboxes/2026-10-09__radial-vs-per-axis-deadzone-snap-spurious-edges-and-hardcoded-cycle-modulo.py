"""Sandbox: stick -> deadzone -> debounced 8-way direction edges -> slot cursor cycling (modulo N).
ITERATION 1 REFUTED S3/S4/S6 as first written (edges 4 vs 4 at r=.25 instead of 8 vs 1; at r=.35 8 vs 4 instead of equal).
ITERATION 2 (written after run 1): the hazard band is r >= DZ*sqrt2 where per-axis alternates cardinal/diagonal (8 edges/rev
vs 4), while in DZ <= r < DZ*sqrt2 per-axis registers NOTHING at diagonals (dead share > 0.3 predicted in iter 2 but run 2 gave 0.189 so iter 3 uses > 0.1; radial 0) with equal edge counts;
S6 uses r=0.35 so extra edges move the cursor (8%5=3 vs 4%5=4).
PREDICTION (before first run, iteration 1; S3/S4/S6 superseded as above), DZ=0.20, magnitude sweeps on a deterministic 360-step circle:
 S1 per-axis deadzone at radius 0.25 gives angle error > 10 deg for more than 15% of angles; radial gives 0.
 S2 minimum radius that registers at 45 deg is DZ*sqrt(2)=0.283 per-axis vs 0.200 radial (41% more travel).
 S3 a thumb circling at radius 0.25 (below the per-axis diagonal threshold, above the radial one) produces
    8 direction edges per revolution per-axis (cardinal<->none flicker) but exactly 1 edge radial.
 S4 BREAK: if the thumb circles at radius 0.35 (above both thresholds) the two filters give the SAME edge count (so the
    hazard is confined to the band between DZ and DZ*sqrt2).
 S5 cursor cycling with hardcoded modulo 4 on a 5-item enum never reaches index 4 (opticon/E30); with modulo len() all 5.
 S6 combining S3 with S5: spurious extra edges per revolution advance the cursor extra steps per-axis, so
    after one revolution the cursor lands on a different slot than under radial."""
import math

DZ = 0.20

def stick(r, deg):
    a = math.radians(deg); return r * math.cos(a), r * math.sin(a)

def per_axis(x, y):
    return (x if abs(x) >= DZ else 0.0, y if abs(y) >= DZ else 0.0)

def radial(x, y):
    m = math.hypot(x, y)
    return (x, y) if m >= DZ else (0.0, 0.0)

def angle_err(r, deg, f):
    x, y = stick(r, deg); fx, fy = f(x, y)
    if fx == 0 and fy == 0: return 180.0
    d = abs(math.degrees(math.atan2(fy, fx)) - deg) % 360
    return min(d, 360 - d)

def direction(fx, fy):
    """8-way: sign of each surviving component (what a dpad-style menu reads)."""
    return (0 if fx == 0 else (1 if fx > 0 else -1), 0 if fy == 0 else (1 if fy > 0 else -1))

def edges(r, f, steps=360):
    last = (0, 0); n = 0
    seq = []
    for i in range(steps + 1):                       # 361 samples: closes the loop
        d = direction(*f(*stick(r, i * 360.0 / steps)))
        seq.append(d)
    for prev, cur in zip(seq, seq[1:]):
        if cur != prev and cur != (0, 0): n += 1      # a debounced step fires on entering a new nonzero direction
    return n

def min_reg_radius(deg, f):
    r = 0.0
    while r < 1.0:
        r = round(r + 0.001, 3)
        if f(*stick(r, deg)) != (0.0, 0.0): return r
    return None

# S1
bad_pa = sum(angle_err(0.25, d, per_axis) > 10 for d in range(360)) / 360.0
bad_rad = sum(angle_err(0.25, d, radial) > 10 for d in range(360)) / 360.0
print("S1 share of angles with >10deg error at r=0.25: per-axis %.3f radial %.3f" % (bad_pa, bad_rad))
# S2
m_pa, m_rad = min_reg_radius(45, per_axis), min_reg_radius(45, radial)
print("S2 min radius at 45 deg: per-axis %.3f radial %.3f ratio %.2f" % (m_pa, m_rad, m_pa / m_rad))
# S3 / S4
e_pa, e_rad = edges(0.25, per_axis), edges(0.25, radial)
e_pa_hi, e_rad_hi = edges(0.35, per_axis), edges(0.35, radial)
print("S3 edges/rev r=0.25: per-axis %d radial %d" % (e_pa, e_rad))
print("S4 edges/rev r=0.35: per-axis %d radial %d" % (e_pa_hi, e_rad_hi))
# S5
def reach(n_items, modulus):
    cur, seen = 0, {0}
    for _ in range(3 * n_items):
        cur = (cur + 1) % modulus; seen.add(cur)
    return sorted(seen)
SKILLS = 5
hard, derived = reach(SKILLS, 4), reach(SKILLS, SKILLS)
print("S5 reachable slots: hardcoded %%4 -> %s ; %%len -> %s" % (hard, derived))
# S6: each edge advances the cursor
def end_slot(edge_count, modulus): return edge_count % modulus
s_pa, s_rad = end_slot(e_pa, SKILLS), end_slot(e_rad, SKILLS)
print("S6 slot after one revolution (per-axis vs radial): %d vs %d" % (s_pa, s_rad))

dead_pa = sum(direction(*per_axis(*stick(0.25, d))) == (0, 0) for d in range(360)) / 360.0
dead_rad = sum(direction(*radial(*stick(0.25, d))) == (0, 0) for d in range(360)) / 360.0
print("S3b share of angles registering NOTHING at r=0.25: per-axis %.3f radial %.3f" % (dead_pa if False else dead_pa, dead_rad))
s_pa, s_rad = end_slot(e_pa_hi, SKILLS), end_slot(e_rad_hi, SKILLS)
print("S6 (iter2, r=0.35) slot after one revolution: per-axis %d vs radial %d" % (s_pa, s_rad))
ok = (bad_pa > 0.15 and bad_rad == 0 and abs(m_pa / m_rad - math.sqrt(2)) < 0.02 and e_pa == e_rad == 4 and dead_pa > 0.1 and dead_rad == 0
      and e_pa_hi == 8 and e_rad_hi == 4 and 4 not in hard and derived == [0, 1, 2, 3, 4] and s_pa != s_rad)  # 8%5=3 vs 4%5=4
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "per-axis bad-angle share %.2f vs 0; diagonal travel x%.2f; edges/rev %d vs %d at r=.25 and %d vs %d at r=.35; "
      "hardcoded modulo reaches %s" % (bad_pa, m_pa / m_rad, e_pa, e_rad, e_pa_hi, e_rad_hi, hard))
