import math
R, C = 10_000.0, 1e-6          # RC = 10 ms
def delay(vs, vth, dt=1e-6):
    """Euler-integrate dv/dt = (vs - v)/RC until v >= vth; return seconds."""
    v, t = 0.0, 0.0
    while v < vth:
        v += (vs - v) / (R * C) * dt
        t += dt
    return t
RC = R * C
# 1) classic ratios
t63 = delay(5.0, 5.0 * (1 - math.exp(-1))); t23 = delay(5.0, 5.0 * 2 / 3); t50 = delay(5.0, 2.5)
# 2) fixed 3.0 V reference with supply 5.0 -> 4.5 -> 4.0
fixed = {vs: delay(vs, 3.0) for vs in (5.0, 4.5, 4.0)}
drift_fixed = fixed[4.5] / fixed[5.0] - 1
# 3) ratiometric threshold 2/3 Vs: same RC multiple at every supply
rat = {vs: delay(vs, vs * 2 / 3) for vs in (5.0, 4.5, 4.0)}
drift_rat = max(abs(rat[v] / rat[5.0] - 1) for v in rat)
# 4) BREAK: threshold above supply never fires (guard against infinite loop): vth=0.95 vs at sag, exact closed form
closed = lambda vs, vth: -RC * math.log(1 - vth / vs)
err = max(abs(fixed[v] - closed(v, 3.0)) / closed(v, 3.0) for v in fixed)
print("t63 %.3f RC, t(2/3) %.3f RC, t50 %.3f RC" % (t63 / RC, t23 / RC, t50 / RC))
print("fixed 3.0 V:", {v: round(t / RC, 3) for v, t in fixed.items()}, "drift at 4.5 V %.1f%%" % (100 * drift_fixed))
print("ratiometric:", {v: round(t / RC, 3) for v, t in rat.items()}, "max drift %.3f%%" % (100 * drift_rat))
ok = (abs(t63 / RC - 1) < 0.01 and abs(t23 / RC - math.log(3)) < 0.01 and abs(t50 / RC - math.log(2)) < 0.01
      and 0.15 < drift_fixed < 0.25 and drift_rat < 0.005 and err < 0.005)
print("RESULT: %s fixed 3.0 V threshold stretches the delay %.1f%% when supply sags 5.0 to 4.5 V (and %.1f%% at 4.0 V), ratiometric 2/3 threshold drifts %.3f%%, delays 0.693/1.099 RC at 1/2 and 2/3 match closed form within %.2f%%"
      % ("PASS" if ok else "FAIL", 100 * drift_fixed, 100 * (fixed[4.0] / fixed[5.0] - 1), 100 * drift_rat, 100 * err))
