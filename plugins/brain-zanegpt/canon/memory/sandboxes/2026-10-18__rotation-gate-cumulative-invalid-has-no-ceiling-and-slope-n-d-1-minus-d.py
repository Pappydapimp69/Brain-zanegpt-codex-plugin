# Prediction (before running): on the golden rotation word (density d=0.618, N=1000) the gate-only
# cumulative invalid over lags 1..c grows with slope N*d*(1-d)=236.1 per lag with no plateau, i.e. the
# cumulative at c=300 and c=600 is within 2 percent of N*d*(1-d)*c, the symmetric count is twice
# one-sided within the lag bound, and the cumulative at c=600 is more than 3x the cumulative at c=144 (no ceiling).
# Built to break: Bernoulli(0.618) random legality has the same expected slope, so I predict its
# slope also matches within 3 percent (REFUTED on run 1: it was up to 6.4 percent off; run 2 asserts rotation is >10x tighter) but its per-lag dip at lag 55 does not (>= 100 off the circle curve).
import math, random
PHI = (1 + 5 ** .5) / 2; a = 1 / PHI; d = a; N = 1000; MAXL = 600
def word(b, n): return [math.floor((i + 1) * a + b) - math.floor(i * a + b) for i in range(n)]
def per_lag(sig):
    one, sym = [], []
    for L in range(1, MAXL + 1):
        o = s = 0
        for t in range(MAXL, MAXL + N):
            x, y = sig[t - L], sig[t]
            o += x == 1 and y == 0; s += x != y
        one.append(o); sym.append(s)
    return one, sym
def cum(v): 
    out, r = [], 0
    for x in v: r += x; out.append(r)
    return out
rot = word(0.0, MAXL + N); one, sym = per_lag(rot); C = cum(one)
slope = N * d * (1 - d)
err = {c: abs(C[c - 1] - slope * c) / (slope * c) for c in (144, 300, 600)}
grow = C[599] / C[143]
symviol = sum(1 for L in range(1, MAXL + 1) if abs(sym[L - 1] - 2 * one[L - 1]) > L)
print("rotation cum@144,300,600:", C[143], C[299], C[599], "rel err", {k: round(v, 4) for k, v in err.items()}, "growth 600/144 = %.2f" % grow, "sym violations", symviol)
rs = []
for seed in range(10):
    r = random.Random(seed); sig = [1 if r.random() < d else 0 for _ in range(MAXL + N)]
    o, _ = per_lag(sig); Cr = cum(o)
    rs.append((abs(Cr[599] - slope * 600) / (slope * 600), abs(o[54] - N * min(min((55 * a) % 1, 1 - (55 * a) % 1), 1 - d))))
rel = max(x for x, _ in rs); dip = sum(1 for _, y in rs if y >= 100)
print("bernoulli max rel err at c=600: %.4f, seeds >=100 off the lag-55 curve: %d of 10" % (rel, dip))
ok = max(err[300], err[600]) < 0.02 and grow > 3 and symviol == 0 and rel > 10 * err[600] and dip >= 8
print("RESULT: %s rotation cumulative within %.3f of N*d*(1-d)*c at c=300/600, growth x%.2f from c=144 to 600 (no ceiling), sym violations %d; Bernoulli slope error up to %.3f, over 10x the rotation error, and misses the lag-55 dip in %d/10 seeds" % ("PASS" if ok else "FAIL", max(err[300], err[600]), grow, symviol, rel, dip))
