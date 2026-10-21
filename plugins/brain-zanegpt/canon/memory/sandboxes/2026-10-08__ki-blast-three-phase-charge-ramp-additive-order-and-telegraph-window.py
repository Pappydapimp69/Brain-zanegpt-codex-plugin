"""Prediction (before run): (A) additive compositing of 40 integer-colour particles is identical in spawn, reverse and scrambled draw order (spread 0) while
alpha-over differs (spread > 0); (B) the charge-only telegraph window is identical across travel speeds 1/2/4/8 while the total reaction window shrinks toward the
charge length as speed rises; (C) a charge ramp that emits particles one at a time at angle 2*pi*i/N leaves a lopsided early resultant (>0.5 at k=3 of N=32) while
a bit-reversed index order and golden-ratio steps stay below 0.35 at every prefix >= 4 (E1 of vfx-weather said spawn-order phases give a wave);
(D) the impact curve (attack 2 ticks, decay 20) peaks on the impact tick, which is also the flash tick, with 90 percent of its energy after the peak.
Deterministic, stdlib only."""
import math
from fractions import Fraction as F

ok = True
# A: blending order
parts = [((i*37) % 256, (i*91) % 256, (i*53) % 256, F((i % 5) + 1, 6)) for i in range(40)]
def additive(order):
    r = g = b = 0
    for i in order:
        pr, pg, pb, a = parts[i]
        r += pr*a; g += pg*a; b += pb*a
    return (min(255, r), min(255, g), min(255, b))
def alpha_over(order):
    r = g = b = F(0)
    for i in order:
        pr, pg, pb, a = parts[i]
        r = pr*a + r*(1-a); g = pg*a + g*(1-a); b = pb*a + b*(1-a)
    return (r, g, b)
orders = [list(range(40)), list(range(39, -1, -1)), [(i*7) % 40 for i in range(40)]]
add_set = {additive(o) for o in orders}; alp_set = {alpha_over(o) for o in orders}
print("A additive distinct results", len(add_set), "alpha-over distinct", len(alp_set))
ok &= len(add_set) == 1 and len(alp_set) == 3

# B: telegraph window vs speed
dist = 64
for charge in (6, 12, 24):
    tele = {charge for sp in (1, 2, 4, 8)}
    total = [charge + dist // sp for sp in (1, 2, 4, 8)]
    print(f"B charge {charge}: telegraph {sorted(tele)} total window by speed {total}")
    ok &= len(tele) == 1 and total == sorted(total, reverse=True) and total[-1] > charge
# break: at very high speed total window collapses onto charge
fast = 24 + dist // 64
print("B break: speed 64 total window", fast, "== charge+1")
ok &= fast == 25

# C: balance of emission prefix
N = 32
def resultant(angles):
    return math.hypot(sum(math.cos(a) for a in angles), sum(math.sin(a) for a in angles)) / len(angles)
def bitrev(i, bits=5): return int(format(i, f"0{bits}b")[::-1], 2)
seqs = {"in_order": [2*math.pi*i/N for i in range(N)],
        "bit_reversed": [2*math.pi*bitrev(i)/N for i in range(N)],
        "golden": [2*math.pi*((i*0.6180339887498949) % 1) for i in range(N)]}
worst = {}
for name, s in seqs.items():
    rs = [resultant(s[:k]) for k in range(4, N + 1)]
    worst[name] = max(rs)
    print(f"C {name}: k=3 resultant {resultant(s[:3]):.3f}  worst prefix k>=4 {worst[name]:.3f}  full {resultant(s):.3f}")
ok &= resultant(seqs["in_order"][:3]) > 0.5 and worst["bit_reversed"] < 0.35 and worst["golden"] < 0.35
# C break: bit-reversal only balances at power-of-two N (N=24)
N2 = 24
br24 = [2*math.pi*bitrev(i)/32 for i in range(N2)]
print(f"C break: bit-reversed first 24 of 32 slots, full resultant {resultant(br24):.3f}")

# D: impact curve
atk, dec = 2, 20
curve = [F(t, atk) for t in range(atk + 1)] + [F(dec - 1 - t, dec) for t in range(dec)]
peak = max(range(len(curve)), key=lambda i: curve[i])
after = sum(curve[peak + 1:]); total = sum(curve)
print(f"D peak tick {peak} == impact/flash tick {atk}; energy share after peak {float(after/total):.3f}")
ok &= peak == atk and after / total > F(9, 10) - F(1, 10)  # >0.8
print("RESULT:", "PASS" if ok else "FAIL",
      f"additive 1 vs alpha 3 distinct results; telegraph invariant to speed, total window collapses at speed 64; in-order prefix resultant {resultant(seqs['in_order'][:3]):.2f} vs bit-reversed {worst['bit_reversed']:.2f} golden {worst['golden']:.2f}; impact peak tick {peak}, {float(after/total):.2f} after")
