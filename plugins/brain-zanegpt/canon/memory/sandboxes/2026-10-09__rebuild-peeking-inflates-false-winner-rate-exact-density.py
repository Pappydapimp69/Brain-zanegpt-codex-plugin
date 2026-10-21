"""Prediction (written before run): exact two-sided false-positive rate for K equally spaced looks at |z|>=1.96 under the null
is ~5.0% for K=1, ~8.3% for 2, ~10.7% for 3, ~14.2% for 5, ~16.8% for 7, ~19.3% for 10; Pocock constant critical z for overall
5% is ~2.41 at K=5 and ~2.56 at K=10. Method differs from simulation: exact survival-density recursion on a grid (no RNG)."""
import math
H = 0.05
def phi(x): return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
TAP = [(j * H, phi(j * H) * H) for j in range(-120, 121)]  # +/-6 sigma kernel

def reject_prob(K, c):
    lim = 12 * math.sqrt(K)
    n = int(lim / H)
    f = {0: 1.0}  # density mass on grid index of partial sum S
    for k in range(1, K + 1):
        g = {}
        for i, m in f.items():
            if m < 1e-18: continue
            for d, w in ((j, phi(j * H) * H) for j in range(-120, 121)):
                g[i + d] = g.get(i + d, 0.0) + m * w
        thr = c * math.sqrt(k)
        f = {i: m for i, m in g.items() if abs(i * H) < thr}
    return 1 - sum(f.values())

def pocock(K, target=0.05):
    lo, hi = 1.96, 3.5
    for _ in range(18):
        mid = (lo + hi) / 2
        if reject_prob(K, mid) > target: lo = mid
        else: hi = mid
    return (lo + hi) / 2

rates = {K: reject_prob(K, 1.96) for K in (1, 2, 3, 5, 7, 10)}
for K, r in rates.items(): print("K=%d rate=%.4f" % (K, r), flush=True)
p5, p10 = pocock(5), pocock(10)
print("pocock5=%.3f pocock10=%.3f" % (p5, p10))
ok = (abs(rates[1] - .05) < .003 and abs(rates[2] - .083) < .005 and abs(rates[5] - .142) < .006
      and 0.16 < rates[7] < 0.18 and abs(rates[10] - .193) < .008 and abs(p5 - 2.41) < .03 and abs(p10 - 2.56) < .03
      and rates[3] / rates[2] > 1.0)
print("RESULT: %s K1=%.3f K2=%.3f K3=%.3f K5=%.3f K7=%.3f K10=%.3f pocock5=%.2f pocock10=%.2f" % (
    "PASS" if ok else "FAIL", rates[1], rates[2], rates[3], rates[5], rates[7], rates[10], p5, p10))
