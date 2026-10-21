# Prediction (before running): on the golden rotation word (density 0.618) with lag set
# S={3,21,55,89,144}, N=900: (a) validity+cutoff is lossless first at cutoff 144 (the largest lag,
# since every lag has valid presses); a cutoff of 21 (a Fibonacci "period") loses valid presses at
# lags 55,89,144; (b) gate-only invalid at cutoff c equals sum over S lags <= c of N*min(x,1-d)
# within 1.5 ticks per lag, nondecreasing in c, with its max at 144; (c) a Bernoulli(0.618) control
# misses the summed curve at lag 55 by >= 100 ticks in at least 8 of 10 seeds (built to break).
import math, random
PHI = (1 + 5 ** .5) / 2; a = 1 / PHI; N = 900; S = (3, 21, 55, 89, 144)
def word(b, n): return [math.floor((i + 1) * a + b) - math.floor(i * a + b) for i in range(n)]
def counts(sig, L):
    inv = val = 0
    for t in range(L, L + N):
        if sig[t - L] == 1 and sig[t] == 0: inv += 1
        if sig[t - L] == 1 and sig[t] == 1: val += 1
    return inv, val
def curve(L):
    fr = (L * a) % 1; x = min(fr, 1 - fr); return N * min(x, 1 - a)
ok = True
for b in (0.0, 0.31):
    sig = word(b, N + 160)
    inv = {L: counts(sig, L)[0] for L in S}; val = {L: counts(sig, L)[1] for L in S}
    lossless = min(c for c in range(0, 200) if sum(val[L] for L in S if L > c) == 0)
    lost21 = sum(val[L] for L in S if L > 21)
    cum = [sum(inv[L] for L in S if L <= c) for c in S]
    dev = max(abs(inv[L] - curve(L)) for L in S)
    mono = all(p <= q for p, q in zip(cum, cum[1:]))
    print("b", b, "lossless", lossless, "lost@21", lost21, "cum", cum, "max dev", round(dev, 2), "inv", inv)
    ok &= lossless == 144 and lost21 > 0 and dev <= 1.5 and mono and cum[-1] == max(cum)
far = 0
for seed in range(10):
    r = random.Random(seed); sig = [1 if r.random() < a else 0 for _ in range(N + 160)]
    if abs(counts(sig, 55)[0] - curve(55)) >= 100: far += 1
print("bernoulli seeds >=100 off the curve at lag 55:", far, "of 10")
ok &= far >= 8
print("RESULT: %s lossless cutoff 144 on both offsets, cutoff 21 loses valid presses, summed circle curve within 1.5 ticks per lag, Bernoulli off the curve in %d/10 seeds" % ("PASS" if ok else "FAIL", far))
