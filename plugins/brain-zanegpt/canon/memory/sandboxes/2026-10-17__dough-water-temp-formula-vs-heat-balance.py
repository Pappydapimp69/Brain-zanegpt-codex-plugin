# Sandbox: the baker's three-factor water temperature rule versus a heat balance on the same dough.
# Rule (Hamelman, Bread): water = 3*DDT - flour - room - friction_factor, friction_factor = 3 x real mixer temperature rise.
# Heat balance: thermal masses relative to water: flour 0.40 (assumed), water 1.0, preferment 0.70 (assumed) at room temperature.
# dough = (mf*cf*Tf + mp*cp*Tr + mw*Tw) / (mf*cf + mp*cp + mw) + rise.   Flour mass 1.0, hydration = water mass.
CF, CP = 0.40, 0.70
def dough(tf, tr, tw, hyd, pre, rise):
    a, b = CF, pre * CP
    return (a * tf + b * tr + hyd * tw) / (a + b + hyd) + rise
def rule(ddt, tf, tr, rise): return 3 * ddt - tf - tr - 3 * rise
def exact(ddt, tf, tr, hyd, pre, rise):
    a, b = CF, pre * CP
    return ((ddt - rise) * (a + b + hyd) - a * tf - b * tr) / hyd
DDT, RISE = 24.0, 6.0
errs = {}
for pre in (0.0, 0.5, 1.0):
    for hyd in (0.55, 0.75, 0.85):
        e = []
        for tf, tr in ((20, 20), (14, 24), (30, 30), (10, 18)):
            e.append(dough(tf, tr, rule(DDT, tf, tr, RISE), hyd, pre, RISE) - DDT)
        errs[(pre, hyd)] = e
        print("preferment %.1f hydration %.2f  error by (flour,room) [(20,20),(14,24),(30,30),(10,18)]: %s" % (pre, hyd, ["%+.1f" % x for x in e]))
worst = max(abs(x) for v in errs.values() for x in v)
ex = max(abs(dough(tf, tr, exact(DDT, tf, tr, h, p, RISE), h, p, RISE) - DDT)
         for p in (0.0, 0.5, 1.0) for h in (0.55, 0.75, 0.85) for tf, tr in ((20, 20), (14, 24), (30, 30), (10, 18)))
neg = rule(DDT, 30, 30, RISE)          # BREAK: hot kitchen
# error smallest where the three thermal masses are closest (pre=1.0, hyd 0.55 -> masses 0.40/0.70/0.55)
near = max(abs(x) for x in errs[(1.0, 0.55)])
far = max(abs(x) for x in errs[(0.0, 0.85)])
ok = worst > 3 and ex < 1e-9 and neg < 0 and near < far
print("RESULT: %s rule misses the dough temperature by up to %.1f C (%.1f C at near-equal thermal masses, %.1f C with no preferment at 85%% hydration); heat-balance water hits it exactly (%.0e); hot-kitchen rule asks for %.0f C water" % ("PASS" if ok else "FAIL", worst, near, far, ex, neg))
