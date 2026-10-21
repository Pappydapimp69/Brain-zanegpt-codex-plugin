import math, statistics
N, LMAX = 1000, 120
def inval(a, w, L, off=0.21):
    S = lambda t: ((off + t * a) % 1.0) < w
    return sum(1 for t in range(N) if S(t) and not S(t + L))
def valid(a, w, L, off=0.21):
    S = lambda t: ((off + t * a) % 1.0) < w
    return sum(1 for t in range(N) if S(t) and S(t + L))
def dist(x):
    x %= 1.0
    return min(x, 1 - x)
def corr(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
phi = (math.sqrt(5) - 1) / 2
slopes = {"golden": phi, "silver": math.sqrt(2) - 1, "e-2": math.e - 2, "pi-3": math.pi - 3 + 0.3, "near1/12": 1 / 12 + 0.0003}
w = 0.4
Ls = range(1, LMAX + 1)
res = {}
for name, a in slopes.items():
    inv = [inval(a, w, L) for L in Ls]
    own = corr([min(w, dist(L * a)) for L in Ls], inv)
    gold = corr([min(w, dist(L * phi)) for L in Ls], inv)
    lossless = max(L for L in Ls if valid(a, w, L) > 0)
    res[name] = (own, gold, lossless, min(inv), inv.index(min(inv)) + 1)
    print(name, "r_own %.3f r_phi %.3f lossless %d min inv %d at lag %d" % (own, gold, lossless, min(inv), inv.index(min(inv)) + 1))
ok = (all(r[0] > 0.95 for r in res.values())
      and all(res[n][1] < 0.6 for n in ("silver", "e-2", "pi-3", "near1/12"))
      and res["near1/12"][2] > 12)
print("RESULT: %s own-slope r %s, phi-distance r on other slopes %s, near-periodic slope 1/12 lossless lag %d (> period 12)"
      % ("PASS" if ok else "FAIL", {n: round(r[0], 3) for n, r in res.items()},
         {n: round(res[n][1], 2) for n in ("silver", "e-2", "pi-3", "near1/12")}, res["near1/12"][2]))
