"""A personal-data 'lag slider' picks the best of 8 lags between two daily series. Kernel
DATA-TOY/finance-viz/statistically-gate-a-fitted-trend... says gate the readout with a significance test and
default to 'no clear relationship'. Test: does a per-lag p<0.05 gate do that when the tool also SEARCHES lags?
Deterministic hash-based noise (seeded, no RNG module), stdlib only.

PREDICTION (before first run), n=14 days, lags 0..7, 400 noise pairs:
 P1 no gate: the slider reports a relationship in 400/400 noise pairs (100%).
 P2 naive gate (best lag, p<0.05 unadjusted): false-positive rate between 25% and 45%.
 P3 Bonferroni gate (p < 0.05/8): false-positive rate <= 8%.
 P4 planted effect at lag 3: power with Bonferroni at r=0.8 is >= 80% and at r=0.4 is <= 25% (the gate costs sensitivity).
 P5 BREAK: AR(1) noise with phi=0.8 inflates the Bonferroni false-positive rate above 10%.
"""
import math

def u(seed, i):                       # deterministic uniform in (0,1) from an integer hash
    x = (seed * 1000003 + i * 7919 + 12345) & 0xFFFFFFFF
    x ^= x >> 16; x = (x * 0x45d9f3b) & 0xFFFFFFFF; x ^= x >> 16; x = (x * 0x45d9f3b) & 0xFFFFFFFF; x ^= x >> 16
    return (x + 0.5) / 4294967296.0

def normal(seed, n):
    out = []
    for k in range(n):
        a, b = u(seed, 2 * k), u(seed, 2 * k + 1)
        out.append(math.sqrt(-2 * math.log(a)) * math.cos(2 * math.pi * b))
    return out

def ar1(seed, n, phi):
    z = normal(seed, n); x = [z[0]]
    for k in range(1, n): x.append(phi * x[-1] + z[k])
    return x

def corr(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

def t_pdf(t, df):
    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    return c * (1 + t * t / df) ** (-(df + 1) / 2)
def p_two(t, df):                     # two-sided p by Simpson integration of the tail
    hi = 200.0; m = 20000; h = (hi - abs(t)) / m
    s = t_pdf(abs(t), df) + t_pdf(hi, df)
    for i in range(1, m): s += t_pdf(abs(t) + i * h, df) * (4 if i % 2 else 2)
    return min(1.0, 2 * s * h / 3)
def p_from_r(r, n):
    df = n - 2; t = r * math.sqrt(df / max(1e-12, 1 - r * r)); return p_two(t, df)
_crit = {}
def r_crit(n, alpha):                 # smallest |r| with p < alpha, by bisection
    key = (n, alpha)
    if key not in _crit:
        lo, hi = 0.0, 0.9999
        for _ in range(40):
            mid = (lo + hi) / 2
            if p_from_r(mid, n) < alpha: hi = mid
            else: lo = mid
        _crit[key] = hi
    return _crit[key]

LAGS = range(8)
def best_lag_r(x, y, n):
    best = 0.0
    for L in LAGS:
        r = corr(x[: len(x) - L][-n:], y[L:][-n:]) if L else corr(x[-n:], y[-n:])
        if abs(r) > abs(best): best = r
    return best

def rate(make_pair, n, alpha, trials=400):
    c = r_crit(n, alpha) if alpha else 0.0
    hits = 0
    for s in range(trials):
        x, y = make_pair(s)
        if abs(best_lag_r(x, y, n)) > c: hits += 1
    return hits / trials

N = 14; TOT = N + 7
white = lambda s: (normal(2 * s + 1, TOT), normal(2 * s + 2, TOT))
def planted(r_eff, lag=3):
    def mk(s):
        x = normal(2 * s + 1, TOT); e = normal(2 * s + 2, TOT)
        k = r_eff / math.sqrt(1 - r_eff ** 2)
        y = [0.0] * TOT
        for i in range(TOT): y[i] = (k * x[i - lag] if i >= lag else 0.0) + e[i]
        return x, y
    return mk
red = lambda s: (ar1(2 * s + 1, TOT, 0.8), ar1(2 * s + 2, TOT, 0.8))

r1 = rate(white, N, None)
r2 = rate(white, N, 0.05)
r3 = rate(white, N, 0.05 / 8)
w8 = rate(planted(0.8), N, 0.05 / 8); w4 = rate(planted(0.4), N, 0.05 / 8)
w8n = rate(planted(0.8), N, 0.05)
r5 = rate(red, N, 0.05 / 8)
r5n = rate(red, N, 0.05)
print("critical |r| n=14: p<.05 %.3f, p<.05/8 %.3f" % (r_crit(N, 0.05), r_crit(N, 0.05 / 8)))
print("white noise: no gate %.3f | naive gate %.3f | bonferroni %.3f" % (r1, r2, r3))
print("planted lag 3: power bonferroni r=.8 %.3f r=.4 %.3f | naive r=.8 %.3f" % (w8, w4, w8n))
print("AR(1)=0.8 noise: bonferroni %.3f naive %.3f" % (r5, r5n))
p = [r1 == 1.0, 0.25 <= r2 <= 0.45, r3 <= 0.08, w8 >= 0.8 and w4 <= 0.25, r5 > 0.10]
print("PREDICTIONS held:", p)
print("RESULT: %s false-positive no-gate/naive/bonf=%.2f/%.2f/%.2f; power bonf r.8/r.4=%.2f/%.2f; AR1 bonf=%.2f (held %d/5)" % (
    "PASS" if all(p) else "FAIL", r1, r2, r3, w8, w4, r5, sum(p)))
