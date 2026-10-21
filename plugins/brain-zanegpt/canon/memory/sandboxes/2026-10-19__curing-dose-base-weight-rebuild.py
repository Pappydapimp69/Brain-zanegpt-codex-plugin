# Own fixture: grams-level dosing of Cure #1 (6.25% NaNO2 by mass) with different meat weights and ratios than the entry.
# Prediction (before run): ppm_on_meat = dose_g * 0.0625 / meat_g * 1e6, so a 0.25% dose on meat is 156.25 ppm for ANY meat weight;
# on meat+water it is 156.25*(1+r) at any r (r=0.1 -> 171.9, 0.6 -> 250.0, 1.5 -> 390.6);
# weighing errors go BOTH ways: trimming after weighing or weighing wet overdoses, tare-too-heavy underdoses.
NITRITE = 0.0625
def ppm(dose_g, meat_g): return dose_g * NITRITE / meat_g * 1e6
def dose_for(pct, base_g): return pct / 100 * base_g
ok = True
for meat in (800.0, 1350.0, 3000.0):
    d = dose_for(0.25, meat); p = ppm(d, meat); ok &= abs(p - 156.25) < 1e-6
    for r in (0.1, 0.6, 1.5):
        base = meat * (1 + r); p2 = ppm(dose_for(0.25, base), meat); ok &= abs(p2 - 156.25 * (1 + r)) < 1e-6
        print("meat", meat, "r", r, "ppm base=meat", round(p, 2), "base=total", round(p2, 2))
# weighing-stage errors, 1350 g true meat after trim
true = 1350.0
errs = {"trim 10% after weighing": true / 0.9, "weighed wet +4% surface water": true * 1.04, "tare too heavy -50 g": true - 50.0}
dirs = {}
for k, w in errs.items():
    p = ppm(dose_for(0.25, w), true); dirs[k] = p - 156.25; print(k, round(p, 2), "ppm", "over" if p > 156.25 else "under")
both = any(v > 0 for v in dirs.values()) and any(v < 0 for v in dirs.values())
print("RESULT:", "PASS" if ok and both else "FAIL",
      f"base=meat gives 156.25 ppm at all 3 meat weights; total base gives 156.25*(1+r) at 9/9 cells; weighing errors go both ways ({', '.join(f'{v:+.1f}' for v in dirs.values())} ppm)")
