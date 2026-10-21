"""Apply LOAD-BALANCING/least-loaded-herds-on-stale-load-info to real queues: the kernel
modelled cumulative assigned work (no jobs ever finish). Here 10 servers each finish one
unit of work per tick; jobs arrive every 1/(0.9*10) ticks (90% utilisation), sizes 1
(or 5% of jobs 40x, scaled so utilisation stays 0.9); the load report (queue lengths) is
refreshed every R arrivals. Policies: least-loaded by the report, two choices by the
report (servers picked by a deterministic LCG), round-robin, random-by-hash (one LCG pick).
Metric: peak queue (work) on any server and mean queue over the run, 20,000 jobs.
PREDICTION (written before running): with real departures the kernel's ranking holds: at
R = 100 stale least-loaded's peak queue is >= 2x two-choices'; fresh (R = 1) least-loaded
is best; with heavy-tailed sizes round-robin's peak is >= 2x fresh least-loaded's."""
N, UTIL, JOBS = 10, 0.9, 20000
class LCG:
    def __init__(self, s): self.s = s
    def next(self, m): self.s = (1103515245 * self.s + 12345) % (2 ** 31); return self.s % m
def run(policy, R, heavy):
    q = [0.0] * N; rep = q[:]; rr = 0; rng = LCG(7); peak = 0.0; tot = 0.0
    if heavy:
        sizes = [40.0 if (k * 37) % 100 < 5 else 1.0 for k in range(JOBS)]
    else:
        sizes = [1.0] * JOBS
    mean_size = sum(sizes) / JOBS
    gap = mean_size / (UTIL * N)                     # ticks between arrivals
    for k in range(JOBS):
        for i in range(N): q[i] = max(0.0, q[i] - gap)  # each server drains 1 unit/tick
        if k % R == 0: rep = q[:]
        if policy == "least": s = min(range(N), key=lambda i: (rep[i], i))
        elif policy == "two":
            a, b = rng.next(N), rng.next(N); s = a if rep[a] <= rep[b] else b
        elif policy == "rr": s = rr; rr = (rr + 1) % N
        else: s = rng.next(N)
        q[s] += sizes[k]; peak = max(peak, q[s]); tot += sum(q) / N
    return peak, tot / JOBS
res = {}
for heavy in (False, True):
    for R in (1, 10, 100):
        res[(heavy, R)] = {p: run(p, R, heavy) for p in ("least", "two", "rr", "hash")}
        print(("heavy " if heavy else "equal ") + f"R {R:3d}: " +
              "  ".join(f"{p}: peak {v[0]:6.1f} mean {v[1]:5.2f}" for p, v in res[(heavy, R)].items()))
e100 = res[(False, 100)]; e1 = res[(False, 1)]; h1 = res[(True, 1)]
c1 = e100["least"][0] >= 2 * e100["two"][0]
c2 = e1["least"][0] <= min(v[0] for v in e1.values())
c3 = h1["rr"][0] >= 2 * h1["least"][0]
print(f"RESULT: {'PASS' if c1 and c2 and c3 else 'FAIL'} equal R100 peak: least {e100['least'][0]:.1f} vs two {e100['two'][0]:.1f} ({c1}); "
      f"fresh least best: {c2} ({e1['least'][0]:.1f}); heavy R1 rr {h1['rr'][0]:.1f} vs least {h1['least'][0]:.1f} ({c3}); "
      f"heavy R100 least {res[(True,100)]['least'][0]:.1f} vs two {res[(True,100)]['two'][0]:.1f}")
