"""Rebuild of seven E73 (published masking data: mono can't share an 80%-must-land line with even one
equal voice; headphones carry ~4; a 6 dB duck lets mono carry 6). Own fixture: a LOGISTIC psychometric
function (E73: linear 10 points/dB) with slope at midpoint 5/10/15 %/dB, calibrated so one equal masker
in mono lands 0.60 (as E73); per-doubling talker penalty c = 1.5 (E73's value), 2.5 and 3.2 dB (the
cited 4-5 dB per tripling = 4/log2(3)..5/log2(3) per doubling); spatial release at the LOW published
end (6 dB for 2-3 maskers, 3 dB beyond); duck 0 or 6 dB. Budget = most voices (line + maskers) with
the line landing >= 0.80, capped at 30.
Predictions written before running:
 P1 mono with no duck: budget 1 at 80% in every cell (0.60 < 0.80).
 P2 headphones beat mono at the same duck in every cell.
 P3 'a 6 dB duck lets mono carry 6' fails at the cited 2.5-3.2 dB per doubling: budget <= 3 there.
 P4 E73's own c = 1.5 with a 10%/dB logistic gives a mono-duck budget within 1 of E73's 6.
"""
import math

def logistic_p(x, slope):           # slope = d p/d dB at the 50% point
    k = 4 * slope
    return 1 / (1 + math.exp(-k * x))

def inv(p, slope):
    return math.log(p / (1 - p)) / (4 * slope)

def landing(voices, mode, duck, c, slope):
    m = voices - 1
    if m == 0: return 1.0
    x0 = inv(0.60, slope)                     # one masker, mono, no duck -> 0.60
    pen = c * math.log2(m)
    rel = 0.0 if mode == "mono" else (6.0 if m <= 3 else 3.0)
    return logistic_p(x0 + duck + rel - pen, slope)

def budget(mode, duck, c, slope, need=0.80):
    b = 1
    for v in range(2, 31):
        if landing(v, mode, duck, c, slope) >= need: b = v
        else: break
    return b

cells = [(c, s) for c in (1.5, 2.5, 3.2) for s in (0.05, 0.10, 0.15)]
R = {}
for c, s in cells:
    R[(c, s)] = {(mo, d): budget(mo, d, c, s) for mo in ("mono", "hp") for d in (0, 6)}
    r = R[(c, s)]
    print(f"c={c} dB/doubling slope={int(s*100)}%/dB: mono {r[('mono',0)]}/{r[('mono',6)]}  headphones {r[('hp',0)]}/{r[('hp',6)]}  (no duck / 6 dB duck)")
p1 = all(R[k][("mono", 0)] == 1 for k in cells)
p2 = all(R[k][("hp", d)] > R[k][("mono", d)] for k in cells for d in (0, 6))
p3 = all(R[(c, s)][("mono", 6)] <= 3 for c, s in cells if c >= 2.5)
p4 = abs(R[(1.5, 0.10)][("mono", 6)] - 6) <= 1
checks = [("P1 mono no duck budget 1", p1), ("P2 headphones beat mono", p2), ("P3 cited penalty: mono+duck <= 3", p3), ("P4 E73 constants reproduce ~6", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; mono+6dB budget at c1.5/2.5/3.2 (slope 10%) "
      f"{R[(1.5,0.10)][('mono',6)]}/{R[(2.5,0.10)][('mono',6)]}/{R[(3.2,0.10)][('mono',6)]}; slope 5% "
      f"{R[(1.5,0.05)][('mono',6)]}/{R[(2.5,0.05)][('mono',6)]}/{R[(3.2,0.05)][('mono',6)]}; headphones no duck c2.5 slope10 {R[(2.5,0.10)][('hp',0)]}")
