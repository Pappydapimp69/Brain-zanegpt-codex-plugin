# Sandbox: cure-stock dose = wrong-base error + serial-dilution worst-case error. Which dominates, by pipette constant a?
# Prediction (before first run): with a 25% wrong-base error, the best dilution plan is <=13% of the combined error
# at every a in 0..0.2 uL, while a single 1000x step at a=0.2 is >=40% of it; with the base fixed to 2% the
# best-plan share at a=0.2 rises above 60% only for the single step (break: base error small).
FLOOR, FINAL = 0.005, 1000.0
def e(V, a): return max(FLOOR, a / V)
def plan_error(factors, a):
    t = 0.0
    for f in factors:
        V = FINAL / f
        t += e(V, a) + e(FINAL - V, a) * (1 - 1 / f)
    return t
PLANS = {"1x1000": [1000], "2x(10,100)": [10, 100], "2x32": [31.6227766] * 2, "3x10": [10] * 3}
def best(a): return min(PLANS.items(), key=lambda kv: plan_error(kv[1], a))
BASE_WRONG = (1000.0 + 250.0) / 1000.0 - 1
rows = {}
for a in (0.0, 0.02, 0.05, 0.1, 0.2):
    nm, pl = best(a); eb = plan_error(pl, a); es = plan_error(PLANS["1x1000"], a)
    rows[a] = (nm, eb, es, eb / (eb + BASE_WRONG), es / (es + BASE_WRONG), eb / (eb + 0.02), es / (es + 0.02))
    print("a=%.2f best %s %.2f%% single %.2f%% | base 25%%: best share %.1f%% single share %.1f%% | base 2%%: best %.1f%% single %.1f%%" % (
        a, nm, eb*100, es*100, *(x*100 for x in rows[a][3:])))
best_share_max = max(r[3] for r in rows.values())
s02 = rows[0.2][4]; fixed_best = rows[0.2][5]; fixed_single = rows[0.2][6]
print("S1 best-plan max share with wrong base %.1f%%; S2 single step at a=0.2 share %.1f%%" % (best_share_max*100, s02*100))
print("S3 (break) base fixed to 2%%: best plan share at a=0.2 %.1f%%, single step %.1f%%" % (fixed_best*100, fixed_single*100))
print("original prediction held:", best_share_max <= 0.13 and s02 >= 0.40 and fixed_single > 0.6 and fixed_best <= 0.6)
ok = best_share_max <= 0.13 and s02 >= 0.40 and fixed_single > fixed_best
print("RESULT: %s with a 25%% wrong base the best dilution plan is at most %.0f%% of the error (single step %.0f%% at a=0.2); with the base fixed the single step is %.0f%% vs best plan %.0f%%" % ("PASS" if ok else "FAIL", best_share_max*100, s02*100, fixed_single*100, fixed_best*100))
