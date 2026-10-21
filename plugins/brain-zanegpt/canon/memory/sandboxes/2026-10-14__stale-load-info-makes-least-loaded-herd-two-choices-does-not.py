"""Seeding LOAD-BALANCING. 10 servers, 8000 jobs; policies pick a server per job.
Round-robin (RR), hash (HASH), least-loaded by a SNAPSHOT of loads refreshed every R jobs (LL),
power-of-two-choices on two hashed candidates using the same snapshot (P2C).
Metric: PEAK imbalance = max over time (after 1000 jobs warm-up) of max load / mean load.
Load = cumulative work assigned so far (a first run with a draining queue showed a 2.0 sawtooth even for round-robin,
a discreteness artifact, so it was replaced). Warm-up 1000 jobs. Deterministic hash, stdlib only.

PREDICTION (before first run):
 P1 equal sizes, fresh snapshot (R=1): peak imbalance RR <= 1.02, LL <= 1.05, P2C <= 1.30, HASH >= 1.40.
 P2 equal sizes, stale snapshot R=100: LL peak imbalance >= 3.0 (herding onto one server per interval) and
    P2C <= 1.60, i.e. P2C degrades far less than LL.
 P3 heavy-tailed sizes (5% of jobs are 40x): RR peak >= 1.5 while LL fresh <= 1.5.
 P4 BREAK: at R=1 with heavy tails LL still beats P2C; the herd advantage of P2C exists only when R is large.
"""
N, JOBS, WARM = 10, 8000, 1000
def h(i, k=0):
    x = (i * 2654435761 + k * 40503 + 977) & 0xFFFFFFFF
    x ^= x >> 15; x = (x * 2246822519) & 0xFFFFFFFF; x ^= x >> 13; x = (x * 3266489917) & 0xFFFFFFFF; x ^= x >> 16
    return x

def run(policy, R, heavy):
    load = [0.0] * N; snap = [0.0] * N; peak = 0.0
    sizes = [(40.0 if (heavy and h(i, 9) % 100 < 5) else 1.0) for i in range(JOBS)]
    mean_size = sum(sizes) / JOBS
    for i in range(JOBS):
        if i % R == 0: snap = load[:]
        if policy == 'RR': s = i % N
        elif policy == 'HASH': s = h(i) % N
        elif policy == 'LL': s = min(range(N), key=lambda j: (snap[j], j))
        else:
            a, b = h(i, 1) % N, h(i, 2) % N
            s = a if (snap[a], a) <= (snap[b], b) else b
        load[s] += sizes[i]
        if i >= WARM:
            m = sum(load) / N
            if m > 0: peak = max(peak, max(load) / m)
    return peak

res = {}
for heavy in (False, True):
    for R in (1, 100):
        for p in ('RR', 'HASH', 'LL', 'P2C'):
            res[(heavy, R, p)] = run(p, R, heavy)
        print("heavy=%-5s R=%3d  RR %.2f  HASH %.2f  LL %.2f  P2C %.2f" % (
            heavy, R, *(res[(heavy, R, p)] for p in ('RR', 'HASH', 'LL', 'P2C'))))
g = lambda hv, R, p: res[(hv, R, p)]
p1 = g(False, 1, 'RR') <= 1.02 and g(False, 1, 'LL') <= 1.05 and g(False, 1, 'P2C') <= 1.30 and g(False, 1, 'HASH') >= 1.40
p2 = g(False, 100, 'LL') >= 3.0 and g(False, 100, 'P2C') <= 1.60
p3 = g(True, 1, 'RR') >= 1.5 and g(True, 1, 'LL') <= 1.5
p4 = g(True, 1, 'LL') < g(True, 1, 'P2C')
print("PREDICTIONS held:", p1, p2, p3, p4)
print("RESULT: %s equalR1 RR/LL/P2C/HASH=%.2f/%.2f/%.2f/%.2f; equalR100 LL/P2C=%.2f/%.2f; heavyR1 RR/LL/P2C=%.2f/%.2f/%.2f (held %d/4)" % (
    "PASS" if all([p1, p2, p3, p4]) else "FAIL", g(False,1,'RR'), g(False,1,'LL'), g(False,1,'P2C'), g(False,1,'HASH'),
    g(False,100,'LL'), g(False,100,'P2C'), g(True,1,'RR'), g(True,1,'LL'), g(True,1,'P2C'), sum([p1,p2,p3,p4])))
