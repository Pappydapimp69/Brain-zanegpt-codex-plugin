"""Prediction (before run): at a=0.02 uL the worst-case plan errors are about 1x1000 2.5, 2x31.6 1.97, 3x10 2.85, 6x3.16 5.05 percent.
A readout that rounds concentration to a step q hides those differences: at q=0.05 (5 percent) I predict 1x1000, 2x31.6 and 3x10
all read exactly 1.00 in 100 percent of their error corners (indistinguishable although their true bounds differ by up to 0.9 points) and only
the 6-step plan shows up (some corners read 1.05); at q=0.01 the plans separate (max deviation readings 0.02, 0.02, 0.03, 0.05). At a=0.2 (20.5 vs 2.2 percent)
q=0.05 does separate 1x1000 from 2x31.6. Corners = every +/- combination of per-transfer error bounds, first-order product. Deterministic."""
from itertools import product
FLOOR = 0.005; FINAL = 1000.0
def e(V, a): return max(FLOOR, a / V)
def terms(factors, a):
    t = []
    for f in factors:
        V = FINAL / f
        t.append(e(V, a)); t.append(e(FINAL - V, a) * (1 - 1 / f))
    return t
def corners(factors, a):
    ts = terms(factors, a); out = []
    for signs in product((-1, 1), repeat=len(ts)):
        c = 1.0
        for s, x in zip(signs, ts): c *= 1 + s * x
        out.append(c)
    return out
def reading(c, q): return round(round(c / q) * q, 6)
PLANS = {"1x1000": [1000], "2x31.6": [31.6227766] * 2, "3x10": [10] * 3, "6x3.16": [10 ** 0.5] * 6}
table = {}
for a in (0.02, 0.2):
    for q in (0.01, 0.05):
        for name, f in PLANS.items():
            cs = corners(f, a); rd = [reading(c, q) for c in cs]
            exact = sum(1 for r in rd if r == 1.0) / len(rd)
            worst = max(abs(c - 1) for c in cs)
            table[(a, q, name)] = (worst, exact, max(abs(r - 1) for r in rd))
            print("a=%.2f q=%.2f %-7s true worst %.2f%%  corners reading exactly 1.00: %5.1f%%  max reading deviation %.2f" % (a, q, name, worst * 100, exact * 100, table[(a, q, name)][2]))
ex = {n: table[(0.02, 0.05, n)][1] for n in PLANS}
wv = {n: table[(0.02, 0.05, n)][0] for n in PLANS}
dev1 = {n: round(table[(0.02, 0.01, n)][2], 2) for n in PLANS}
big = (round(table[(0.2, 0.05, "1x1000")][2], 2), round(table[(0.2, 0.05, "2x31.6")][2], 2))
# observed-claim checks: (1) the readout ranking by share-of-corners-exact INVERTS the true-worst ranking for 1x1000 vs 6x3.16
inverted = ex["6x3.16"] > ex["1x1000"] and wv["6x3.16"] > wv["1x1000"]
# (2) at q=0.01 max reading deviation ties 1x1000 and 3x10 although true worst bounds differ
tie = dev1["1x1000"] == dev1["3x10"] and wv["3x10"] > wv["1x1000"]
# (3) a large pipette error is visible even at q=0.05
visible = big[0] >= 0.20 and big[1] == 0.0
ok = inverted and tie and visible
print("RESULT: %s at a=0.02 q=0.05 share of corners reading 1.00 is 1x1000 %.0f%%, 2x31.6 %.0f%%, 3x10 %.0f%%, 6x3.16 %.0f%% (true worst %.2f/%.2f/%.2f/%.2f%%), so the 6-step plan looks better than 1 step; q=0.01 max deviation ties 1x1000 and 3x10 at %.2f; a=0.2 q=0.05 shows 1x1000 %.2f vs 2x31.6 %.2f" %
      ("PASS" if ok else "FAIL", *(ex[n] * 100 for n in PLANS), *(wv[n] * 100 for n in PLANS), dev1["1x1000"], *big))
