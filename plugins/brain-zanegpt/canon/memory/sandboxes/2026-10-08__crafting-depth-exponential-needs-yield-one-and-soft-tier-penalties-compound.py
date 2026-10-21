"""Prediction (before first run):
 A) kernel replay (4 types/tier, 3 inputs, depths 1-6): recipes 4,8,..,24; raw/top 3,9,..,729; 10-item kit trips at 12x20 = 1,1,2,4,11,31.
 B) BREAK: crafting yield y>1 per craft turns growth into (k/y)^d: y=2 -> ratio 1.5 per depth (raw at d6 ~ 11.4, 1 trip); y=3 -> raw stays 1.0 (flat, no exponential).
 C) hybrid-random-rarity: if only rarity share p of drops qualifies (expected value, zone fixes type) trips scale by exactly 1/p at every depth, per-depth ratio stays 3.0.
 D) tier gate: soft penalty (a below-tier station needs 1/e inputs, e=0.8) compounds: ratio 3/0.8=3.75 per depth, raw at d6 ~2781 vs 729; a hard gate to zero adds no per-depth growth (ratio 3.0) but blocks crafting above the gate.
Deterministic, no RNG, stdlib only."""
from fractions import Fraction as F
from math import ceil

K = 3; TYPES = 4; KIT = 10; CAP = 12 * 20

def recipes(d): return TYPES * d
def raw(d, k=K, y=1, e=1): return (F(k) / (y * e)) ** d
def trips(r, qty=KIT, cap=CAP): return ceil(r * qty / cap)

def expand(d, k=K):
    # explicit tree walk: each craft at depth d consumes k items of depth d-1; depth 0 items are raw units
    return 1 if d == 0 else sum(expand(d - 1, k) for _ in range(k))
# A
ra = [recipes(d) for d in range(1, 7)]
rw = [int(raw(d)) for d in range(1, 7)]
tr = [trips(raw(d)) for d in range(1, 7)]
okA = [expand(d) for d in range(1, 7)] == [3, 9, 27, 81, 243, 729] and ra == [4, 8, 12, 16, 20, 24] and rw == [3, 9, 27, 81, 243, 729] and tr == [1, 1, 2, 4, 11, 31]
print("A", ra, rw, tr, okA)
# B
r2 = [raw(d, y=2) for d in range(1, 7)]; r3 = [raw(d, y=3) for d in range(1, 7)]
okB = all(r2[i + 1] / r2[i] == F(3, 2) for i in range(5)) and all(x == 1 for x in r3) and trips(r2[5]) == 1
print("B y=2", [float(x) for x in r2], "y=3", [float(x) for x in r3], "trips y2 d6", trips(r2[5]), okB)
# C
p = F(1, 4)
tc = [trips(raw(d) / p) for d in range(1, 7)]
ratios = [raw(d + 1) / raw(d) for d in range(1, 6)]
okC = all(t >= 4 * tr[i] - 3 and t <= 4 * tr[i] for i, t in enumerate(tc)) and all(x == 3 for x in ratios) and tc[5] == ceil(raw(6) * KIT * 4 / CAP)
print("C trips at p=1/4", tc, "vs p=1", tr, okC)
# D
e = F(4, 5)
soft = [raw(d, e=e) for d in range(1, 7)]
okD = soft[1] / soft[0] == F(15, 4) and 2700 < soft[5] < 2800 and raw(6) == 729
gate = 3  # hard gate: stations above tier 3 simply cannot craft -> output 0, no extra inputs consumed
hard = [raw(d) if d <= gate else 0 for d in range(1, 7)]
okD = okD and hard[:3] == [3, 9, 27] and hard[3:] == [0, 0, 0]
print("D soft", [float(x) for x in soft], "hard", hard, okD)
ok = okA and okB and okC and okD
print("RESULT:", "PASS" if ok else "FAIL",
      "recipes linear 4..24, raw 3^d, trips %s; yield 2 gives ratio 1.5, yield 3 flat 1.0; rarity share 1/4 multiplies trips %s, ratio stays 3; soft tier penalty 0.8 gives ratio 3.75 (%.0f vs 729 at d6), hard gate flat zero above tier 3"
      % (tr, tc, float(soft[5])))
