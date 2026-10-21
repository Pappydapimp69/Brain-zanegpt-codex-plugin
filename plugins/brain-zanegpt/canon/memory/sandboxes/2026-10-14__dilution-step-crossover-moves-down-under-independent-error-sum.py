"""Prediction (before run): the 1000x dilution crossover (a above which 3x10 beats 1x1000, worst-case-sum model 0.024 uL)
moves LOWER, into 0.008-0.020 uL, when the per-step bounds are combined as independent errors (root-sum-square) instead of
a straight worst-case sum, because 3 steps cost sqrt(3) not 3 times one step. Built to break: a=0, where one step must still win.
Deterministic, stdlib only, tolerance model is an assumption (not a vendor spec)."""
import math
FLOOR = 0.005; FINAL = 1000.0
def e(V, a): return max(FLOOR, a / V)
def step_terms(f, a):
    V = FINAL / f
    return e(V, a), e(FINAL - V, a) * (1 - 1 / f)
def worst(factors, a): return sum(sum(step_terms(f, a)) for f in factors)
def rss(factors, a): return math.sqrt(sum(x * x for f in factors for x in step_terms(f, a)))
PLANS = {"1x1000": [1000], "2x32": [31.6227766] * 2, "3x10": [10] * 3, "6x3.16": [10 ** 0.5] * 6}
def cross(fn):
    a = 0.0
    while fn(PLANS["3x10"], a) >= fn(PLANS["1x1000"], a) and a < 1: a += 0.0005
    return a
for name, fn in (("worst-sum", worst), ("rss", rss)):
    for a in (0.0, 0.02, 0.05, 0.2):
        r = {k: round(fn(v, a) * 100, 2) for k, v in PLANS.items()}
        print(name, "a=%.2f" % a, r, "best", min(r, key=r.get))
cw, cr = cross(worst), cross(rss)
print("crossover worst-sum %.4f  rss %.4f" % (cw, cr))
best0 = min(PLANS, key=lambda k: rss(PLANS[k], 0.0))
ok = 0.008 <= cr <= 0.020 and cr < cw and best0 == "1x1000" and 0.02 <= cw <= 0.03
print("RESULT: %s crossover worst-sum %.4f uL, rss %.4f uL, a=0 best %s" % ("PASS" if ok else "FAIL", cw, cr, best0))
