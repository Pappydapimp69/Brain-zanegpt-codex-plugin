"""Sandbox: SOURDOUGH dough hydration with a starter. Convention (baker's percentage, e.g. Hamelman, Bread): hydration = total water / total flour,
where a starter of hydration h contributes flour s/(1+h) and water s*h/(1+h).
Naive recipe hydration = added water / added flour. PREDICTION (before run): 500 g flour, 350 g water, 100 g starter at 100%: naive 70.00%, true 72.73%;
same with a 50% stiff starter: true 67.65% (error -2.35 points); the error sign equals the sign of (starter hydration - dough hydration) on every grid cell,
and is exactly 0 when the starter hydration equals the naive dough hydration (the BREAK case); error grows with starter amount."""
from fractions import Fraction as Fr

def naive(F, W): return Fr(W, F)
def true(F, W, s, h):
    return (Fr(W) + Fr(s) * h / (1 + h)) / (Fr(F) + Fr(s) / (1 + h))

F, W = 500, 350
cases = {"100": true(F, W, 100, Fr(1)), "50": true(F, W, 100, Fr(1, 2))}
print("naive", float(naive(F, W) * 100), "true@100%", round(float(cases["100"]) * 100, 2), "true@50%", round(float(cases["50"]) * 100, 2))
sign_ok = cells = zero_ok = 0
mono = True
for h in (Fr(1, 2), Fr(7, 10), Fr(1), Fr(5, 3)):
    prev = None
    for s in (50, 100, 150, 200):
        for W2 in (300, 350, 400):
            cells += 1
            err = true(F, W2, s, h) - naive(F, W2)
            dough = naive(F, W2)
            expected_sign = (h > dough) - (h < dough)
            actual_sign = (err > 0) - (err < 0)
            sign_ok += expected_sign == actual_sign
            if h == dough: zero_ok += err == 0
        e = abs(true(F, 350, s, h) - naive(F, 350))
        if prev is not None and e < prev: mono = False
        prev = e
print("sign matches", sign_ok, "of", cells, "zero when equal", zero_ok, "monotone in starter amount", mono)
ok = (round(float(cases["100"]) * 100, 2) == 72.73 and round(float(cases["50"]) * 100, 2) == 67.65 and sign_ok == cells and zero_ok > 0 and mono)
print("RESULT: %s 100%% starter 72.73 vs naive 70.00, 50%% starter 67.65, sign rule on %d/%d cells, exact zero at equal hydration (%d cells), error grows with starter amount=%s" % (
    "PASS" if ok else "FAIL", sign_ok, cells, zero_ok, mono))
