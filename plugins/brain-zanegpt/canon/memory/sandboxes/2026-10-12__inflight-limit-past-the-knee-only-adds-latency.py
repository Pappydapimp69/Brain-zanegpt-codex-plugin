"""New-idea loop 1 (QUEUEING): an in-flight / concurrency limit should sit at throughput x latency
(Little's law L = lambda W); past the knee more in-flight work adds only waiting. Composes QUEUEING
capacity-planning (1/(1-rho)), pooling, QUEUEING-THEORY staffing, CONCURRENCY thread-pool sizing.
Deterministic seeded simulation (seed is a parameter).
 S1 open M/M/2 at rho 0.85: time-average number in system L vs lambda x mean time in system W.
 S2 closed system (fixed N jobs in flight, zero think time) on c = 4 servers, exp service mean 1:
    throughput X(N) and latency R(N) for N = 1..16.
 S3 a limit set to N = X_target x W_target for X_target = 3.2/s, W_target = 1.3 s.
Predictions written before running:
 P1 Little's law: L within 2% of lambda x W.
 P2 past N = 8 (2x servers) throughput rises < 5% more while latency keeps rising ~linearly (R(16)/R(8) > 1.8).
 P3 the Little-sized limit (N = round(3.2 x 1.3) = 4) reaches >= 90% of the 3.2/s target with latency <= 1.3 x 1.15.
"""
import heapq, random

def open_mmc(c, rho, seed=5, n=200000, warm=20000):
    rng = random.Random(seed); lam = c * rho
    t = 0.0; free = [0.0] * c; heapq.heapify(free)
    arr, dep = [], []
    for i in range(n):
        t += rng.expovariate(lam)
        st = max(t, heapq.heappop(free)); d = st + rng.expovariate(1.0)
        heapq.heappush(free, d)
        if i >= warm: arr.append(t); dep.append(d)
    T0, T1 = arr[0], arr[-1]
    W = sum(d - a for a, d in zip(arr, dep)) / len(arr)
    lam_hat = len(arr) / (T1 - T0)
    # time-average number in system over [T0, T1]
    ev = sorted([(a, 1) for a in arr] + [(d, -1) for d in dep if d <= T1])
    area, cur, last = 0.0, 0, T0
    for tt, k in ev:
        area += cur * (tt - last); cur += k; last = tt
    L = area / (T1 - T0)
    return L, lam_hat, W

def closed(N, c=4, seed=9, jobs=120000):
    rng = random.Random(seed); free = [0.0] * c; heapq.heapify(free)
    ready = [0.0] * N; heapq.heapify(ready)   # times when each in-flight slot submits its next job
    done, tot_r, t_end = 0, 0.0, 0.0
    while done < jobs:
        sub = heapq.heappop(ready); st = max(sub, heapq.heappop(free)); fin = st + rng.expovariate(1.0)
        heapq.heappush(free, fin); heapq.heappush(ready, fin)
        done += 1; tot_r += fin - sub; t_end = max(t_end, fin)
    return done / t_end, tot_r / done

L, lam, W = open_mmc(2, 0.85)
print(f"S1 Little: L {L:.3f} vs lambda*W {lam*W:.3f}")
rows = {N: closed(N) for N in (1, 2, 4, 6, 8, 12, 16)}
for N, (X, R) in rows.items(): print(f"S2 N={N:2d}: throughput {X:.3f}/s latency {R:.3f}s")
Nlim = round(3.2 * 1.3); Xl, Rl = closed(Nlim)
print(f"S3 limit N={Nlim}: throughput {Xl:.3f} (target 3.2), latency {Rl:.3f} (target 1.3)")
p1 = abs(L / (lam * W) - 1) <= 0.02
p2 = rows[16][0] / rows[8][0] < 1.05 and rows[16][1] / rows[8][1] > 1.8
p3 = Xl >= 0.9 * 3.2 and Rl <= 1.3 * 1.15
checks = [("P1 Little within 2%", p1), ("P2 past 2x servers: throughput flat, latency linear", p2), ("P3 Little-sized limit hits targets", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; Little L {L:.3f} vs {lam*W:.3f}; X/R N4 {rows[4][0]:.2f}/{rows[4][1]:.2f} N8 {rows[8][0]:.2f}/{rows[8][1]:.2f} "
      f"N16 {rows[16][0]:.2f}/{rows[16][1]:.2f}; limit N={Nlim} X {Xl:.2f} R {Rl:.2f}")
