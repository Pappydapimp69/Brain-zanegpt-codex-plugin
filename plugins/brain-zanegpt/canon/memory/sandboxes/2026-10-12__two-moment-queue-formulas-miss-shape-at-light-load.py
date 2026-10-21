"""Deeper follow-up to brain's queueing seed lesson (Kingman ~25% LOW at load 0.5 with cv 2 gamma traffic).
Question: is that a fixable formula error, or do two-moment formulas fail because the distribution SHAPE
matters at the same cv? Seeded G/G/1 (Lindley, 300000 customers, 3 seeds averaged) with arrivals and service
at cv 2 drawn from three shapes with the same mean and cv: gamma, balanced 2-phase hyperexponential (H2),
lognormal. Compared with Kingman and with the Kraemer & Langenbach-Belz (1976) correction (as implemented
in the LINE solver): g = exp(-(1-rho)(ca^2-1)/(ca^2+4cs^2)) for ca > 1.
Predictions written before running:
 P1 at load 0.5 the three shapes' simulated waits differ by more than 20% (max/min).
 P2 KLB is NOT closer than Kingman to the gamma case at load 0.5 (it lowers an estimate that was already low).
 P3 at load 0.9 the shapes differ by less than at 0.5 (heavy traffic washes shape out).
"""
import math, random

def draw(rng, mean, cv, shape):
    if shape == "gamma":
        k = 1 / cv ** 2; return rng.gammavariate(k, mean / k)
    if shape == "h2":                       # balanced-means H2
        c2 = cv * cv; p = 0.5 * (1 + math.sqrt((c2 - 1) / (c2 + 1)))
        return rng.expovariate(2 * p / mean) if rng.random() < p else rng.expovariate(2 * (1 - p) / mean)
    if shape == "lognorm":
        s2 = math.log(1 + cv * cv); return rng.lognormvariate(math.log(mean) - s2 / 2, math.sqrt(s2))

def gg1(rho, shape, seed, n=300000, warm=20000):
    ra, rs = random.Random(seed), random.Random(seed + 77)
    w = tot = 0.0
    for i in range(n):
        if i >= warm: tot += w
        w = max(0.0, w + draw(rs, 1.0, 2.0, shape) - draw(ra, 1 / rho, 2.0, shape))
    return tot / (n - warm)

def kingman(rho, ca=2, cs=2): return rho / (1 - rho) * (ca * ca + cs * cs) / 2
def klb(rho, ca=2, cs=2):
    g = math.exp(-(1 - rho) * (ca * ca - 1) / (ca * ca + 4 * cs * cs)) if ca > 1 else \
        math.exp(-2 * (1 - rho) * (1 - ca * ca) ** 2 / (3 * rho * (ca * ca + cs * cs)))
    return kingman(rho, ca, cs) * g

R = {}
for rho in (0.5, 0.9):
    for shape in ("gamma", "h2", "lognorm"):
        R[(rho, shape)] = sum(gg1(rho, shape, s) for s in (1, 2, 3)) / 3
    print(f"load {rho}: sim gamma {R[(rho,'gamma')]:.2f} H2 {R[(rho,'h2')]:.2f} lognormal {R[(rho,'lognorm')]:.2f}; Kingman {kingman(rho):.2f} KLB {klb(rho):.2f}")
spread = {rho: max(R[(rho, s)] for s in ("gamma", "h2", "lognorm")) / min(R[(rho, s)] for s in ("gamma", "h2", "lognorm")) for rho in (0.5, 0.9)}
p1 = spread[0.5] > 1.2
p2 = abs(klb(0.5) - R[(0.5, "gamma")]) >= abs(kingman(0.5) - R[(0.5, "gamma")])
p3 = spread[0.9] < spread[0.5]
checks = [("P1 shapes differ > 20% at load 0.5", p1), ("P2 KLB not closer for gamma at 0.5", p2), ("P3 spread shrinks at 0.9", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; load 0.5 gamma/H2/lognormal {R[(0.5,'gamma')]:.2f}/{R[(0.5,'h2')]:.2f}/{R[(0.5,'lognorm')]:.2f} "
      f"(spread x{spread[0.5]:.2f}) vs Kingman {kingman(0.5):.2f} KLB {klb(0.5):.2f}; load 0.9 {R[(0.9,'gamma')]:.1f}/{R[(0.9,'h2')]:.1f}/{R[(0.9,'lognorm')]:.1f} "
      f"(x{spread[0.9]:.2f}) vs Kingman {kingman(0.9):.1f} KLB {klb(0.9):.1f}")
