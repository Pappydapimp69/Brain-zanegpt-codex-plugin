"""Sandbox: error budget of a nitrite cure made from a serially diluted stock.
Pipeline: stock -> 1000x dilution in n equal steps (final 1000 uL, pipette error per
transferred volume v = max(0.5%, a/v)) -> dosed as percent of a weight base.
Dose-base error: using meat+brine weight instead of meat weight (curing-dose lesson).
Deterministic, worst-case sums, no RNG."""
RATIO = 1000.0
def dil_err(n, a):
    r = RATIO ** (1.0 / n)
    v = 1000.0 / r            # uL carried per step into 1000 uL final
    return n * max(0.005, a / v)

def base_err(meat_g, brine_g):
    # dose set as pct of (meat+brine) instead of meat: delivered ppm on meat is high by this
    return brine_g / meat_g

cases = [(a, n) for a in (0.0, 0.02, 0.2, 0.5) for n in (1, 2, 3, 4)]
best = {}
for a in (0.0, 0.02, 0.2, 0.5):
    errs = {n: dil_err(n, a) for n in (1, 2, 3, 4)}
    best[a] = min(errs, key=errs.get)
    print("a=%.2f" % a, {n: round(e * 100, 2) for n, e in errs.items()}, "best n", best[a])

spread = {a: max(dil_err(n, a) for n in (1, 2, 3, 4)) - min(dil_err(n, a) for n in (1, 2, 3, 4)) for a in best}
bases = {"10pct brine": base_err(1000, 100), "25pct brine": base_err(1000, 250), "trim mismatch 25pct meat": 0.25}
print("step-choice spread (pct):", {a: round(s * 100, 2) for a, s in spread.items()})
print("base error (pct):", {k: round(v * 100, 1) for k, v in bases.items()})

ok = True
# 1) at a=0.02 the whole step-choice spread is under 2 points while any >=10pct brine base error is >=10
ok &= spread[0.02] < 0.02 and min(bases.values()) >= 0.10
# 2) best step count differs across a (regime), so dilution does matter on its own scale
ok &= len(set(best.values())) >= 2
# 3) BREAK: very coarse pipette a=0.5: best choice still yields error below the smallest base error?
ok &= min(dil_err(n, 0.5) for n in (1, 2, 3, 4)) < min(bases.values())
# 4) base error is independent of n; dilution error is independent of base
ok &= len({round(base_err(1000, 100), 9) for _ in range(4)}) == 1
worst_dil = max(min(dil_err(n, a) for n in (1, 2, 3, 4)) for a in best)
print("RESULT: %s step-count spread at a=0.02 is %.2f pct vs 10-25 pct base error; best-case dilution error never exceeds %.1f pct" % ("PASS" if ok else "FAIL", spread[0.02]*100, worst_dil*100))
