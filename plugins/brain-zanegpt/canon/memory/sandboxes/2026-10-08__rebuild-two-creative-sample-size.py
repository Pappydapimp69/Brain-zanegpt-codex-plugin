# Own fixture: pooled two-sided z-test (alpha .05), exact power by enumerating both binomials.
# Prediction (before run): n ~7,750 per creative (7,600..8,000) for 1.0% vs 1.5%; size ~0.05 (0.04..0.06);
# power at n=1000 < 0.2; halved baseline 0.5% vs 0.75% needs 1.9x..2.1x; conversion 2% vs 3% needs ~3,830 clicks (3,600..4,100).
from math import lgamma, log, exp, sqrt
Z = 1.959964
def pmf(n, p, lo, hi):
    return {k: exp(lgamma(n+1)-lgamma(k+1)-lgamma(n-k+1)+k*log(p)+(n-k)*log(1-p)) for k in range(lo, hi+1)}
def window(n, p): s = sqrt(n*p*(1-p)); return max(0, int(n*p-9*s)), min(n, int(n*p+9*s)+1)
def reject(k1, k2, n):
    pb = (k1+k2)/(2*n)
    if pb in (0, 1): return False
    se = sqrt(pb*(1-pb)*2/n)
    return abs(k1/n-k2/n)/se > Z
def rej_prob(n, pa, pb_):
    a = pmf(n, pa, *window(n, pa)); b = pmf(n, pb_, *window(n, pb_))
    return sum(x*y for k1, x in a.items() for k2, y in b.items() if reject(k1, k2, n))
def power(n, p1, p2): return rej_prob(n, p1, p2)
def size(n, p): return rej_prob(n, p, p)
def need(p1, p2, start, step=10):
    n = start
    while power(n, p1, p2) < 0.8: n += step
    # first n where 8 consecutive larger n all stay >= .8 (power is sawtooth in n)
    while any(power(n+j, p1, p2) < 0.8 for j in range(1, 9)): n += step
    return n
lo = need(0.01, 0.015, 6000, 50)
n1 = need(0.01, 0.015, lo-100, 5)
print("n per creative 1.0 vs 1.5:", n1, "power", round(power(n1, .01, .015), 3), "size", round(size(n1, .0125), 3))
p1k = power(1000, .01, .015); print("power at n=1000:", round(p1k, 3))
n2 = need(0.005, 0.0075, int(n1*1.7), 10); ratio = n2/n1; print("halved baseline n:", n2, "ratio", round(ratio, 2))
c = need(0.02, 0.03, 3000, 5); print("conversion clicks per creative:", c, "impressions at 1% CTR:", c*100)
ok = 7600 <= n1 <= 8000 and 0.04 <= size(n1, .0125) <= 0.06 and p1k < 0.2 and 1.9 <= ratio <= 2.1 and 3600 <= c <= 4100
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"n={n1} power1000={p1k:.2f} halved={n2} ({ratio:.2f}x) conv clicks={c} imps={c*100}")
