"""Prediction (before run): for a 1000x dilution into 1000 uL final volume per step with worst-case pipetting
error e(V) = max(floor, a/V) (floor 0.5 percent, a in uL), splitting into more steps lowers the worst-case
concentration error once the smallest transfer is below a/floor, i.e. at a=0.02 uL (smallest single transfer 1 uL,
error 2 percent) the 1x1000 plan is WORSE than 3x10 (about 2.85 percent expected vs 2.5 percent -> I predict 3x10 is
slightly WORSE or equal), and at a=0.05 the 3x10 plan wins; crossover in a lies between 0.02 and 0.06 uL.
Built to break: a floor-only world (a=0) where every extra step only adds error, so one step must win.
Deterministic worst-case bounds, no RNG, stdlib only. The tolerance model is an assumption, not a vendor spec."""
FLOOR = 0.005
FINAL = 1000.0

def e(V, a): return max(FLOOR, a / V)

def plan_error(factors, a):
    tot = 0.0
    for f in factors:
        V = FINAL / f
        tot += e(V, a) + e(FINAL - V, a) * (1 - 1 / f)
    return tot

PLANS = {"1x1000": [1000], "2x(10,100)": [10, 100], "2x32": [31.6227766, 31.6227766], "3x10": [10, 10, 10], "6x(~3.16)": [10 ** 0.5] * 6}
rows = {}
for a in (0.0, 0.02, 0.05, 0.1, 0.2):
    rows[a] = {k: plan_error(v, a) for k, v in PLANS.items()}
    best = min(rows[a], key=rows[a].get)
    print("a=%.2f" % a, {k: round(v * 100, 2) for k, v in rows[a].items()}, "best", best)
# crossover a where 3x10 first beats 1x1000
a = 0.0
while plan_error(PLANS["3x10"], a) >= plan_error(PLANS["1x1000"], a) and a < 1:
    a += 0.001
cross = a
brk = min(rows[0.0], key=rows[0.0].get) == "1x1000"
ok = brk and min(rows[0.2], key=rows[0.2].get) != "1x1000" and 0.02 <= cross <= 0.06
print("RESULT: %s floor-only best=%s; crossover a=%.3f uL where 3x10 beats 1x1000; a=0.2 best=%s" %
      ("PASS" if ok else "FAIL", min(rows[0.0], key=rows[0.0].get), cross, min(rows[0.2], key=rows[0.2].get)))
