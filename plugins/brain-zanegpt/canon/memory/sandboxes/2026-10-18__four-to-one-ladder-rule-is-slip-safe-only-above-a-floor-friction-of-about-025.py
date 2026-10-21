# Real source: the 4-to-1 rule for portable ladders (OSHA 29 CFR 1926.1053(b)(5): base one quarter of the working
# length from the wall, angle atan(4) = 75.5 degrees). Static model: rigid ladder of weight W at mid-length, person of
# weight P at fraction f of the length, frictionless wall, floor friction mu. Torque about the foot gives the wall
# push N_w = (W/2 + P*f)*cot(theta); the floor must supply that as friction against a normal force of W+P, so the
# ladder holds only if mu >= (W/2 + P*f)/(W+P) * cot(theta).
# PREDICTION (before run): with W 120 N, P 800 N, person at the top (f 1.0) the 4:1 angle needs mu of about 0.23, so
# it is slip-safe on floors with mu >= 0.25 (dry concrete 0.6, dry wood 0.4) but slips at mu 0.2 (wet metal or
# polished tile); the minimum safe angle for mu 0.4 is under 70 degrees (a shallower ladder than 4:1 still holds);
# BREAK: a person at the bottom (f 0.1) at mu 0.2 holds at 4:1 even though the top case slips.
import math
W, P = 120.0, 800.0
def mu_needed(theta_deg, f):
    return (W / 2 + P * f) / (W + P) / math.tan(math.radians(theta_deg))
def min_angle(mu, f):
    k = (W / 2 + P * f) / (W + P)
    return math.degrees(math.atan(k / mu))
a41 = math.degrees(math.atan(4))
need_top, need_low = mu_needed(a41, 1.0), mu_needed(a41, 0.1)
floors = {"dry concrete": 0.6, "dry wood": 0.4, "damp wood": 0.25, "wet metal": 0.2}
for n, m in floors.items():
    print(f"{n:13s} mu {m}: 4:1 top holds {m >= need_top}, low holds {m >= need_low}, min angle at top {min_angle(m, 1.0):.1f} deg")
print(f"4:1 angle {a41:.1f} deg, mu needed top {need_top:.3f} low {need_low:.3f}; base offset at 4:1 = {1/4:.2f} of the working length")
ok = (a41 > 75.4 and 0.22 < need_top < 0.25 and floors["damp wood"] >= need_top and floors["wet metal"] < need_top
      and min_angle(0.4, 1.0) < 70 and floors["wet metal"] >= need_low)
print(f"RESULT: {'PASS' if ok else 'FAIL'} 4:1 ({a41:.1f} deg) needs mu {need_top:.3f} at the top and {need_low:.3f} near the bottom; holds at mu 0.25, slips at 0.2; min angle at mu 0.4 is {min_angle(0.4, 1.0):.1f} deg")
