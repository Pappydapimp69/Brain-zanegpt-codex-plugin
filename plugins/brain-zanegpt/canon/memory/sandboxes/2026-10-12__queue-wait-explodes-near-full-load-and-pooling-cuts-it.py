"""New domain QUEUEING, seed sandbox. Two claims:
 K1 Kingman (1961) G/G/1: mean wait in queue Wq ~ rho/(1-rho) * (ca^2 + cs^2)/2 * s  (VUT: variability x
    utilisation x time); an upper bound in general, exact as rho -> 1, exact for M/M/1.
 K2 pooling: one shared queue feeding c servers (M/M/c, Erlang C) waits far less than c separate queues
    each with its own server at the same load.
Deterministic: seeded generators (seed parameter), Lindley recursion W' = max(0, W + S - A) for G/G/1
(150000 customers, first 10000 discarded), exact Erlang C for pooling plus a seeded M/M/c event check.
Gamma-distributed gaps and services with coefficient of variation ca, cs (0 = constant).
Predictions written before running:
 P1 M/M/1 (ca = cs = 1): simulated Wq within 6% of Kingman at rho 0.5, 0.8, 0.9.
 P2 constant arrivals and service (D/D/1): Wq = 0 at every rho < 1.
 P3 light traffic, high variability (rho 0.5, ca = cs = 2): Kingman OVERestimates by more than 20%.
 P4 rho 0.8 -> 0.95 multiplies the M/M/1 wait by about 4.75 (19/4), whatever the mean service time.
 P5 pooling 4 servers at rho 0.9: shared-queue wait is under a third of the separate-queue wait.
"""
import heapq, math, random

def draw(rng, mean, cv):
    if cv == 0: return mean
    k = 1 / cv ** 2
    return rng.gammavariate(k, mean / k)

def gg1(rho, ca, cs, seed=7, n=150000, warm=10000, s=1.0):
    rng_a, rng_s = random.Random(seed), random.Random(seed + 1000)
    w, tot, cnt = 0.0, 0.0, 0
    for i in range(n):
        if i >= warm: tot += w; cnt += 1
        w = max(0.0, w + draw(rng_s, s, cs) - draw(rng_a, s / rho, ca))
    return tot / cnt

def kingman(rho, ca, cs, s=1.0):
    return rho / (1 - rho) * (ca ** 2 + cs ** 2) / 2 * s

def erlang_c_wq(c, rho, s=1.0):
    a = c * rho
    top = a ** c / math.factorial(c) / (1 - rho)
    pw = top / (sum(a ** k / math.factorial(k) for k in range(c)) + top)
    return pw * s / (c * (1 - rho))

def mmc_sim(c, rho, seed=11, n=120000, warm=10000, s=1.0):
    rng = random.Random(seed); free = [0.0] * c; heapq.heapify(free); t = 0.0; tot = 0.0; cnt = 0
    for i in range(n):
        t += rng.expovariate(c * rho / s)
        start = max(t, heapq.heappop(free))
        heapq.heappush(free, start + rng.expovariate(1 / s))
        if i >= warm: tot += start - t; cnt += 1
    return tot / cnt

rows = {}
for rho in (0.5, 0.8, 0.9, 0.95):
    for ca, cs in ((1, 1), (0, 0), (2, 2), (0.5, 0.5), (0, 1)):
        rows[(rho, ca, cs)] = (gg1(rho, ca, cs), kingman(rho, ca, cs))
    print(f"rho {rho}: " + "  ".join(f"ca{ca}/cs{cs} sim {rows[(rho,ca,cs)][0]:.2f} K {rows[(rho,ca,cs)][1]:.2f}" for ca, cs in ((1,1),(0,0),(2,2),(0.5,0.5),(0,1))))
sep = kingman(0.9, 1, 1); pooled = erlang_c_wq(4, 0.9); pooled_sim = mmc_sim(4, 0.9)
print(f"4 servers at rho 0.9: separate queues Wq {sep:.2f}; shared queue Erlang C {pooled:.2f} (sim {pooled_sim:.2f}); ratio {pooled/sep:.3f}")
err = lambda r: abs(rows[r][0] / rows[r][1] - 1)
p1 = all(err((r, 1, 1)) <= 0.06 for r in (0.5, 0.8, 0.9))
p2 = all(rows[(r, 0, 0)][0] == 0 for r in (0.5, 0.8, 0.9, 0.95))
p3 = rows[(0.5, 2, 2)][1] > 1.2 * rows[(0.5, 2, 2)][0]
p4 = abs(kingman(0.95, 1, 1) / kingman(0.8, 1, 1) - 4.75) < 1e-9 and abs(rows[(0.95,1,1)][0] / rows[(0.8,1,1)][0] / 4.75 - 1) < 0.25
p5 = pooled < sep / 3 and abs(pooled_sim / pooled - 1) < 0.1
checks = [("P1 M/M/1 within 6% of Kingman", p1), ("P2 D/D/1 never waits", p2), ("P3 Kingman overestimates light-traffic high-variability by >20%", p3),
          ("P4 0.8 -> 0.95 multiplies wait ~4.75", p4), ("P5 pooled 4-server wait < 1/3 of separate", p5)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 5 else 'FAIL'} {held}/5; M/M/1 sim/K rho0.5 {rows[(0.5,1,1)][0]:.2f}/{rows[(0.5,1,1)][1]:.2f} rho0.9 {rows[(0.9,1,1)][0]:.2f}/{rows[(0.9,1,1)][1]:.2f}; "
      f"cv2 rho0.5 sim {rows[(0.5,2,2)][0]:.2f} K {rows[(0.5,2,2)][1]:.2f}, rho0.95 sim {rows[(0.95,2,2)][0]:.2f} K {rows[(0.95,2,2)][1]:.2f}; "
      f"0.8->0.95 sim x{rows[(0.95,1,1)][0]/rows[(0.8,1,1)][0]:.2f}; pooled/separate {pooled/sep:.3f}")
