"""Blind rebuild of seven#E73 (voice budget from published masking data).
Own fixture: a LOGISTIC psychometric function (and a linear one as a second
shape) calibrated so one equal mono talker gives 0.60; slopes 5, 10, 15 %/dB
at the calibration point; 1.5 dB per doubling of talkers; spatial release
6/9/12 dB for 1-3 maskers and half that beyond (3-6 dB); mono gets none.
Budgets are uncapped (up to 64 others). Budget = voices in the scene including
the must-land line."""
import math
def p_of(x, slope, shape):
    if shape == "linear":
        return max(0.0, min(1.0, 0.60 + slope * x))
    k = 4 * slope  # logistic slope at its midpoint; calibrate P(0)=0.60
    x0 = math.log(0.6 / 0.4) / k
    return 1 / (1 + math.exp(-k * (x + x0)))
def adv(n, duck, rel):
    r = 0.0 if rel == 0 else (rel if n <= 3 else rel / 2)
    return duck + r - 1.5 * math.log2(n)
def budget(target, duck, rel, slope, shape):
    best = 0
    for n in range(1, 65):
        if p_of(adv(n, duck, rel), slope, shape) >= target - 1e-12: best = n
    return best + 1
def duck_needed(voices, target, slope, shape):
    d = 0.0
    while budget(target, d, 0, slope, shape) < voices: d += 0.25
    return d
rows = []
for shape in ("logistic", "linear"):
    for s in (0.05, 0.10, 0.15):
        m0 = budget(0.8, 0, 0, s, shape)
        hp = [budget(0.8, 0, r, s, shape) for r in (6, 9, 12)]
        m6 = budget(0.8, 6, 0, s, shape)
        dn = duck_needed(6, 0.8, s, shape)
        rows.append((shape, s, m0, hp, m6, dn))
        print(f"{shape:8} slope {int(s*100):2d}%/dB: mono80 {m0}  headphones80 rel6/9/12 {hp}  mono80+6dB {m6}  duck for 6 voices {dn} dB")
claims = {
 "mono no duck at 80% = 1 (no competing voice)": all(r[2] == 1 for r in rows),
 "headphones about 4 at 80% (3..5) every slope/release": all(3 <= h <= 5 for r in rows for h in r[3]),
 "6 dB duck -> mono at least 3 at 80% every slope": all(r[4] >= 3 for r in rows),
 "6 dB duck -> mono about 6 (5..7) every slope": all(5 <= r[4] <= 7 for r in rows),
 "'about 6 dB' suffices for 6 voices (needed <= 7.5) every slope": all(r[5] <= 7.5 for r in rows),
}
for k, v in claims.items(): print(("held  " if v else "BROKE ") + k)
held = sum(claims.values())
lo = [r for r in rows if r[1] == 0.05]
print(f"RESULT: {'PASS' if held == len(claims) else 'FAIL'} {held}/{len(claims)} held; at 5%/dB mono+6dB carries {[r[4] for r in lo]} (log/lin), "
      f"headphones {[r[3] for r in lo]}, duck for 6 voices {[r[5] for r in lo]} dB")
