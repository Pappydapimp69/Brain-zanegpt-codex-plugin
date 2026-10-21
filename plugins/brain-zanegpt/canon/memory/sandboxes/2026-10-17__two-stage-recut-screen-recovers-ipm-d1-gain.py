# Sandbox: 8 recuts of a winner's cold open; delivery 0.4. Compare rank-by-IPMxD1 at one budget vs a two-stage screen.
# Stage 1: all 8 at n1 impressions ranked on IPM; stage 2: top K re-tested at n2 on IPM*D1. Cost = total impressions.
import random
DELIV = 0.4
def ipm_t(p): return 0.02 + 0.06 * p
def d1_t(p): return 1 - 0.8 * max(0.0, p - DELIV)
def measure(r, p, n):
    inst = sum(r.random() < ipm_t(p) for _ in range(n))
    ret = sum(r.random() < d1_t(p) for _ in range(max(inst, 1))) / max(inst, 1)
    return inst, ret
P = [i / 7 for i in range(8)]
def one_stage(seed, n):
    r = random.Random(seed)
    m = {p: measure(r, p, n) for p in P}
    return max(P, key=lambda p: m[p][0] * m[p][1]), 8 * n
def two_stage(seed, n1, n2, k):
    r = random.Random(seed)
    s1 = {p: measure(r, p, n1)[0] for p in P}
    top = sorted(P, key=lambda p: -s1[p])[:k]
    m = {p: measure(r, p, n2) for p in top}
    return max(top, key=lambda p: m[p][0] * m[p][1]), 8 * n1 + k * n2
def val(p): return ipm_t(p) * d1_t(p)
def run(fn, seeds=300):
    vs = [fn(s) for s in range(seeds)]
    return sum(val(p) for p, _ in vs) / seeds, vs[0][1]
a = run(lambda s: one_stage(s, 300)); b = run(lambda s: one_stage(s, 3000))
c = run(lambda s: two_stage(s, 300, 3000, 2)); d = run(lambda s: two_stage(s, 300, 3000, 4))
best = max(val(p) for p in P)
for name, (v, cost) in (("one-stage n=300", a), ("one-stage n=3000", b), ("two-stage 300 then top2 at 3000", c), ("two-stage 300 then top4 at 3000", d)):
    print("%s: retained installs/imp %.5f (%.0f%% of best) cost %d impressions" % (name, v, 100 * v / best, cost))
ok = c[0] > a[0] and c[1] < b[1] and c[0] >= 0.95 * b[0]
print("RESULT: %s two-stage (top2) reaches %.0f%% of best at %d impressions vs one-stage 3000 %.0f%% at %d" % ("PASS" if ok else "FAIL", 100 * c[0] / best, c[1], 100 * b[0] / best, b[1]))
