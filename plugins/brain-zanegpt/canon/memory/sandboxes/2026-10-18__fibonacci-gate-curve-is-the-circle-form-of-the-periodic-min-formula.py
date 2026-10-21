# Prediction (written before the first run): the periodic law min(L,W,P-L,P-W) has a circle form for a rotation word:
# one-sided invalid(L) ~ N * min(x, 1-rho) with x = distance of L*a to nearest integer, rho = a = 0.618 (legal density).
# Sturmian word s(n)=floor((n+1)a+b)-floor(n*a+b), a=1/phi, N=900, offsets b in {0.0, 0.31}.
# P1: max |invalid - N*min(x,1-rho)| over lags 1..144 <= 12 for both offsets.
# P2: symmetric (any change) = 2*one-sided within 144 (bound L) and the plateau 229 (=N*0.382) is hit within 12 at every lag with x >= 0.382.
# BREAK: 10 Bernoulli(0.618) seeds: the same curve is off by > 100 at lag 55 (the dip), i.e. the law needs the rotation structure.
import math, random
a = (math.sqrt(5) - 1) / 2; rho = a
N, M = 900, 150
def word(b): return [math.floor((n + 1) * a + b) - math.floor(n * a + b) for n in range(N + M)]
def one(sig, L): return sum(1 for t in range(N) if sig[t] and not sig[t + L])
def sym(sig, L): return sum(1 for t in range(N) if sig[t] != sig[t + L])
def curve(L): x = (L * a) % 1; x = min(x, 1 - x); return N * min(x, 1 - rho)
worst = {}; symbad = 0; plateau_dev = 0; nplat = 0
for b in (0.0, 0.31):
    w = word(b)
    worst[b] = max(abs(one(w, L) - curve(L)) for L in range(1, 145))
    for L in range(1, 145):
        if abs(sym(w, L) - 2 * one(w, L)) > L: symbad += 1
        x = (L * a) % 1; x = min(x, 1 - x)
        if x >= 1 - rho:
            nplat += 1; plateau_dev = max(plateau_dev, abs(one(w, L) - N * (1 - rho)))
bern = []
for seed in range(10):
    r = random.Random(seed); bsig = [1 if r.random() < rho else 0 for _ in range(N + M)]
    bern.append(abs(one(bsig, 55) - curve(55)))
print("max dev per offset", worst, "sym-bound violations", symbad, "plateau lags", nplat, "plateau max dev %.1f" % plateau_dev, "bernoulli dev at 55 min %.0f" % min(bern))
ok = all(v <= 12 for v in worst.values()) and symbad == 0 and plateau_dev <= 12 and min(bern) > 100
print("RESULT: %s circle curve N*min(x,1-rho) max dev %.1f / %.1f over lags 1..144, plateau (%d lags) max dev %.1f, sym bound violations %d, Bernoulli dev at lag 55 >= %.0f" % ("PASS" if ok else "FAIL", worst[0.0], worst[0.31], nplat, plateau_dev, symbad, min(bern)))
