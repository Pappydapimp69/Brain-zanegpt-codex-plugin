"""Sandbox: ISO 216 A-series. A0 has area 1 m^2 and ratio sqrt(2); each size halves the one above along the long side.
Compare three ways to build the mm table against the published A0..A10 sizes:
  exact-round   : exact dimensions at each level, rounded to the nearest mm (what ISO 216 specifies; I first wrote floor from memory and was wrong, A0 is 840.9 so floor gives 840)
  chained-floor : halve the previous ROUNDED size, floor again
  chained-round : halve the previous rounded size, round to nearest
Then B series (geometric mean of A(n) and A(n-1) areas, B0 = 1000 mm wide) and the ratio drift of each ladder.
Prediction (before run, with floor as the exact-ladder rule): exact-floor reproduces all 11 published A sizes; chained-floor matches fewer than 11 and its worst
ratio error exceeds exact-floor's; B series from exact floors matches the published B0..B5 (1000x1414, 707x1000, 500x707,
353x500, 250x353, 176x250). Deterministic, stdlib only."""
import math
PUBLISHED_A = [(841, 1189), (594, 841), (420, 594), (297, 420), (210, 297), (148, 210), (105, 148), (74, 105), (52, 74), (37, 52), (26, 37)]
PUBLISHED_B = [(1000, 1414), (707, 1000), (500, 707), (353, 500), (250, 353), (176, 250)]
S2 = math.sqrt(2)

def exact_a(n):
    w = 2 ** (-(2 * n + 1) / 4)          # metres: A0 width = 2^(-1/4) m, height = 2^(1/4) m
    return w * 1000, w * S2 * 1000

def rn(x): return math.floor(x + 0.5)

def exact_floor(n):
    w, h = exact_a(n); return (math.floor(w + 1e-9), math.floor(h + 1e-9))

def exact_round(n):
    w, h = exact_a(n); return (rn(w), rn(h))

def chained(rounding):
    out = [exact_round(0)]
    for n in range(1, 11):
        w, h = out[-1]
        nw, nh = h // 2 if rounding == "floor" else rn(h / 2), w
        out.append((nw, nh))
    return out

ladders = {"exact-floor": [exact_floor(n) for n in range(11)], "exact-round": [exact_round(n) for n in range(11)], "chained-floor": chained("floor"), "chained-round": chained("round")}
def ratio_err(w, h): return abs(h / w - S2) / S2 * 100
for name, lad in ladders.items():
    match = sum(1 for a, b in zip(lad, PUBLISHED_A) if a == b)
    worst = max(ratio_err(*s) for s in lad)
    first_bad = next((i for i, (a, b) in enumerate(zip(lad, PUBLISHED_A)) if a != b), None)
    print("%-14s matches %2d/11 published A sizes, first mismatch at A%s, worst ratio error %.2f%%" % (name, match, first_bad, worst))
    ladders[name] = (lad, match, worst)
# B series: geometric mean of areas; B_n between A_n and A_(n-1); exact B0 = 1 m wide
def exact_b(n):
    w = 2 ** (-n / 2); return w * 1000, w * S2 * 1000
b_floor = [(math.floor(exact_b(n)[0] + 1e-9), math.floor(exact_b(n)[1] + 1e-9)) for n in range(6)]
b_round = [(rn(exact_b(n)[0]), rn(exact_b(n)[1])) for n in range(6)]
bm_f = sum(1 for a, b in zip(b_floor, PUBLISHED_B) if a == b); bm_r = sum(1 for a, b in zip(b_round, PUBLISHED_B) if a == b)
print("B series exact: floor matches %d/6, round matches %d/6; floor %s" % (bm_f, bm_r, b_floor))
# fold test on the published A table itself: does stacking two A(n+1) give exactly A(n)?
pub = PUBLISHED_A; fold_exact = sum(1 for n in range(10) if (pub[n + 1][1], pub[n + 1][0] * 2) == pub[n])
print("published table: two A(n+1) side by side equal A(n) exactly in %d/10 steps" % fold_exact)
ef = ladders["exact-floor"]; er = ladders["exact-round"]; cf = ladders["chained-floor"]; cr = ladders["chained-round"]
ok = cf[1] == 11 and er[1] < 11 and ef[1] < 11 and cr[1] < 11 and bm_f == 6 and bm_r < 6
print("RESULT: %s published A sizes are rounded A0 then chained floor halving (%d/11, worst ratio error %.2f%%); exact-per-level then round only %d/11, exact-per-level floor %d/11, chained round %d/11; B series exact-then-floor %d/6 vs round %d/6; published sizes fold exactly in %d/10 steps"
      % ("PASS" if ok else "FAIL", cf[1], cf[2], er[1], ef[1], cr[1], bm_f, bm_r, fold_exact))
