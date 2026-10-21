# Ladder statics: rigid ladder length L, angle theta from ground, frictionless wall, floor friction mu.
# Person at fraction s along the ladder. Torque about the foot: H*L*sin = (Wl/2 + P*s)*L*cos.
from math import atan, degrees, tan, atan2, sin, cos, radians
def mu_req(theta_deg, s, Wl=80.0, P=800.0):
    th = radians(theta_deg); H = (Wl / 2 + P * s) * cos(th) / sin(th); N = Wl + P
    return H / N
def theta_for_height_over_base(h, d): return degrees(atan2(h, d))
th41 = theta_for_height_over_base(4, 1)            # the 4-to-1 rule: 1 unit out per 4 up
print("4:1 angle", round(th41, 2))
print("s     mu_required at 4:1 / 65deg / 80deg")
for s in (0.0, 0.25, 0.5, 0.75, 1.0):
    print(s, round(mu_req(th41, s), 3), round(mu_req(65, s), 3), round(mu_req(80, s), 3))
MU = {"dry concrete": 0.6, "wet tile": 0.3, "wet ice-like": 0.1}
fails = {k: [s for s in (0.0, 0.25, 0.5, 0.75, 1.0) if mu_req(th41, s) > v] for k, v in MU.items()}
print("slip points at 4:1 by surface", fails)
# angle needed so top-of-ladder demand equals mu: theta = atan((Wl/2+P)/((Wl+P)*mu))
need = {k: round(degrees(atan((40 + 800) / (880 * v))), 1) for k, v in MU.items()}
print("min safe angle (top climber) by surface", need)
# BREAK: heavier ladder (ext. aluminium 20x), light person -> does the demand still peak at the top?
heavy = [round(mu_req(th41, s, Wl=800.0, P=200.0), 3) for s in (0, 0.5, 1.0)]
print("heavy ladder / light climber demand at s=0,.5,1", heavy)
ok = (round(th41, 1) == 76.0 and mu_req(th41, 1.0) > mu_req(th41, 0.0)
      and fails["dry concrete"] == [] and fails["wet tile"] == [] and 1.0 in fails["wet ice-like"]
      and heavy[0] < heavy[2])
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"4:1 angle {th41:.1f} deg needs mu {mu_req(th41,1.0):.3f} at the top and {mu_req(th41,0.0):.3f} at the foot; min safe top angle {need}; slips only on ice-like (mu 0.1)")
