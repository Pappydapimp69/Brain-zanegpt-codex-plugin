"""Prediction (written before the first run), my own fixture: modulus 15, role set B_w = {t : (m*t) mod 15 < w} for w=1..14 (contiguous m=1;
scrambled = average over all 8 units m coprime to 15), always-on fallback (a press at tick t lands legally if t is outside B, or if t and t+L are both in B),
lag sets = 3-subsets of lags 1..8, shadowed = largest legal lag differs from the first-cover cutoff lag.
 (a) the contiguous rate is exactly periodic: rate(T+15)==rate(T) for every T in 600..614;
 (b) the contiguous rate is NOT constant over residues and is 0 at some residues, while the scrambled rate varies by under half the contiguous range;
 (c) the period-averaged contiguous rate is above the period-averaged scrambled rate (the claimed 0.048 vs 0.032 direction)."""
from itertools import combinations
from math import gcd
P = 15; LAGS = range(1, 9); SETS = list(combinations(LAGS, 3))
def rate(T, units):
    sh = tot = 0
    for m in units:
        for w in range(1, P):
            inB = [(m * t) % P < w for t in range(T + 10)]
            land = {}
            for L in LAGS:
                land[L] = {t + L for t in range(T) if (not inB[t]) or inB[t + L]}
            for lags in SETS:
                cov = set(); cut = 0
                for L in lags:
                    if land[L] - cov: cut = L
                    cov |= land[L]
                lg = max((L for L in lags if land[L]), default=0)
                tot += 1; sh += lg != cut
    return sh / tot
SCR = [m for m in range(2, P) if gcd(m, P) == 1]
c = {T: rate(T, [1]) for T in range(600, 630)}
s = {T: rate(T, SCR) for T in range(600, 615)}
print("contig", {T: round(v, 4) for T, v in c.items() if T < 615})
print("scram ", {T: round(v, 4) for T, v in s.items()})
periodic = all(abs(c[T] - c[T + 15]) < 1e-12 for T in range(600, 615))
cr = max(c[T] for T in range(600, 615)) - min(c[T] for T in range(600, 615))
sr = max(s.values()) - min(s.values())
avg_c = sum(c[T] for T in range(600, 615)) / 15; avg_s = sum(s.values()) / 15
zero = [T for T in range(600, 615) if c[T] == 0]
print(f"periodic={periodic} contig range {cr:.4f} scram range {sr:.4f} zero residues {len(zero)} avg contig {avg_c:.4f} scram {avg_s:.4f}")
ok = periodic and cr > 0 and zero and sr < cr / 2 and avg_c > avg_s
print("RESULT:", "PASS" if ok else "FAIL", f"periodic={periodic}; contig range {cr:.3f} (zero at {len(zero)} residues) vs scrambled range {sr:.3f}; period avg contig {avg_c:.4f} vs scram {avg_s:.4f}")
