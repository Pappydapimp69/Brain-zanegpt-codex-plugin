# Sandbox: how fast does earliest-finish greedy stop being optimal as job weights spread out?
# Own LCG (seed 12345), 6 jobs, start 0..11, length 1..6; weights drawn from 1..W, or tied to length.
from itertools import combinations
class L:
    def __init__(s, seed): s.x = seed
    def n(s, k):
        s.x = (s.x * 1103515245 + 12345) % 2**31
        return (s.x >> 8) % k
def best(jobs):
    b = 0
    for r in range(len(jobs) + 1):
        for c in combinations(jobs, r):
            c = sorted(c, key=lambda j: j[1])
            if all(c[i][1] <= c[i + 1][0] for i in range(len(c) - 1)):
                b = max(b, sum(j[2] for j in c))
    return b
def ef(jobs):
    t, tot = -1, 0
    for s, e, w in sorted(jobs, key=lambda j: (j[1], j[0])):
        if s >= t: tot += w; t = e
    return tot
def run(mode, n=3000):
    g = L(12345); opt = 0; loss = 0.0
    for _ in range(n):
        jobs = []
        for _ in range(6):
            s = g.n(12); ln = g.n(6) + 1
            w = {"1": 1, "2": 1 + g.n(2), "3": 1 + g.n(3), "5": 1 + g.n(5), "9": 1 + g.n(9),
                 "len": ln, "inv": 7 - ln}[mode]
            jobs.append((s, s + ln, w))
        b, e = best(jobs), ef(jobs)
        opt += b == e; loss += (b - e) / b
    return 100 * opt / n, 100 * loss / n
out = {}
for m in ("1", "2", "3", "5", "9", "len", "inv"):
    out[m] = run(m)
    print("weights=%-3s EF optimal %.1f%%  mean weight lost %.1f%%" % ((m,) + out[m]))
mono = all(out[a][0] >= out[b][0] for a, b in (("1", "2"), ("2", "3"), ("3", "5"), ("5", "9")))
ok = out["1"][0] == 100.0 and mono and out["2"][0] < 100 and out["len"][0] < out["9"][0] < out["2"][0]
print("RESULT: %s earliest-finish optimal %.1f%% at W=1, %.1f%% at W=2, %.1f%% at W=9; length-tied weights %.1f%%, inverse-length %.1f%%"
      % ("PASS" if ok else "FAIL", out["1"][0], out["2"][0], out["9"][0], out["len"][0], out["inv"][0]))
