"""Toy emulsion sandbox composing the acid-balance kernel (acid dose scales with richness, E102) with the
mayo kernel (slow oil addition lets lecithin coat droplets). Deterministic, stdlib only. ALL parameters are assumptions.
State: yolk gives lecithin capacity L (surface area units it can coat) and water W0. Acid adds water Wa.
Per step oil r is added; new area = 3*r/R0. Coating kinetics: at most K area units coated per step.
Break if (a) uncoated area carried > TOL (rate failure), (b) total area > L (lecithin ceiling), (c) oil fraction > PHI (packing ceiling)."""
R0, K, TOL, PHI = 1.0, 6.0, 1.0, 0.74
E102_DOSE = {1.2: 2.0, 2.0: 2.0, 3.0: 2.2, 4.0: 2.6}   # best acid dose by oil load, from brainwork/E102
UNIT = 0.1                                            # ASSUMED mapping: 1 dose unit = 0.1 x yolk water volume
def run(total_oil, rate, L, W0, dose):
    W = W0 + dose * UNIT * W0; oil = 0.0; area = 0.0; unc = 0.0
    while oil < total_oil - 1e-9:
        r = min(rate, total_oil - oil); oil += r; new = 3 * r / R0
        unc += new; coat = min(unc, K); unc -= coat; area += new
        if unc > TOL: return "rate"
        if area > L + 1e-9: return "lecithin"
        if oil / (oil + W) > PHI: return "packing"
    return "ok"
def ceiling(rate, L, W0, dose):  # max oil that stays ok, scanning 0.1 steps
    best = 0.0
    for i in range(1, 400):
        t = i * 0.1
        if run(t, rate, L, W0, dose) == "ok": best = t
        elif best and run(t, rate, L, W0, dose) != "ok": break
    return best
# S1 slow addition, packing-limited yolk (big lecithin capacity): acid should raise the ceiling
for oil, dose in E102_DOSE.items(): pass
c0 = ceiling(1.0, 100.0, 10.0, 0.0); c1 = ceiling(1.0, 100.0, 10.0, 2.6)
print("S1 packing-limited: ceiling no-acid", round(c0, 1), "acid(2.6)", round(c1, 1))
# S2 lecithin-limited yolk: acid should not help
d0 = ceiling(1.0, 12.0, 10.0, 0.0); d1 = ceiling(1.0, 12.0, 10.0, 2.6)
print("S2 lecithin-limited: ceiling no-acid", round(d0, 1), "acid", round(d1, 1))
# S3 BREAK: fast addition fails regardless of acid
f = [run(10.0, 4.0, 100.0, 10.0, d) for d in (0.0, 2.0, 2.6, 6.0)]
print("S3 fast rate 4.0 per step, dose 0/2/2.6/6:", f)
# S4 rate threshold: largest rate that is ok (should be K*R0/3 = 2.0), independent of acid
def max_rate(dose):
    ok = 0.0
    for i in range(1, 80):
        r = i * 0.1
        if run(5.0, r, 100.0, 10.0, dose) == "ok": ok = r
    return ok
m0, m1 = max_rate(0.0), max_rate(2.6)
print("S4 max ok rate no-acid", round(m0, 1), "acid", round(m1, 1))
ok = c1 > c0 and d1 == d0 and all(x == "rate" for x in f) and abs(m0 - m1) < 1e-9 and abs(m0 - K * R0 / 3) < 0.11
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" acid water raises oil ceiling {c0:.1f}->{c1:.1f} only when packing-limited (lecithin-limited {d0:.1f}->{d1:.1f}); max safe rate {m0:.1f} unchanged by acid")
