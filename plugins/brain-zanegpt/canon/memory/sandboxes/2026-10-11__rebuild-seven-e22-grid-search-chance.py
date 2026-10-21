"""Rebuild of seven E22 on a DIFFERENT map shape and noise model.
Fixture: 17x17 open grid, camp at centre, missing member at a uniform random
cell >=2 from camp; the call gives a bearing only (no distance). Two noise
models: Gaussian angle noise, and a heavy-tailed mix (70% Gaussian, 30% call
from a uniform random bearing - echo). Skilled search: the 14 cells whose
bearing from camp is closest to the heard bearing (ties by distance). Naive:
14 uniform random cells. Nights out: member random-walks 1 step per night,
call is fresh each night. Seeded Monte Carlo, 20000 trials per cell.
PREDICTIONS (written before running):
 P1 gap at low noise (sigma 10 deg) >= 0.30
 P2 find rate does not fall with nights out 0..3 (spread < 0.03) - fresh cue
 P3 at the claimed cap (4 of 24 sectors = 60 deg) gap still >= 0.10
 P4 at sigma 120 deg gap < 0.10 (deep noise collapses skill)
 P5 heavy-tailed noise at sigma 10 keeps gap >= 0.20
"""
import math, random
N = 17; C = N // 2; K = 14; T = 20000
cells = [(x, y) for x in range(N) for y in range(N) if max(abs(x-C), abs(y-C)) >= 2]
def bearing(c):
    return math.atan2(c[1]-C, c[0]-C)
def angd(a, b):
    d = (a - b) % (2*math.pi)
    return min(d, 2*math.pi - d)
def skilled(heard):
    return set(sorted(cells, key=lambda c: (round(angd(bearing(c), heard), 9),
                      abs(c[0]-C)+abs(c[1]-C)))[:K])
def run(sigma, nights, tail, seed):
    rng = random.Random(seed); hs = hn = 0
    for _ in range(T):
        p = rng.choice(cells)
        for _ in range(nights):
            dx, dy = rng.choice([(1,0),(-1,0),(0,1),(0,-1)])
            q = (min(N-1, max(0, p[0]+dx)), min(N-1, max(0, p[1]+dy)))
            if q in cellset: p = q
        if rng.random() < tail:
            heard = rng.uniform(-math.pi, math.pi)
        else:
            heard = bearing(p) + rng.gauss(0, math.radians(sigma))
        if p in skilled(heard): hs += 1
        if p in set(rng.sample(cells, K)): hn += 1
    return hs/T, hn/T
cellset = set(cells)
_cache = {}
_sk = skilled
def skilled(heard):  # memoise by 1-degree bin for speed
    k = round(math.degrees(heard)) % 360
    if k not in _cache: _cache[k] = _sk(math.radians(k))
    return _cache[k]
res = {}
for s in (10, 30, 60, 120):
    res[s] = run(s, 0, 0.0, s)
nights = [run(10, n, 0.0, 100+n)[0] for n in range(4)]
tail = run(10, 0, 0.3, 999)
for s, (a, b) in res.items():
    print(f"sigma {s:3d}: skilled {a:.3f} naive {b:.3f} gap {a-b:.3f}")
print("nights 0..3 skilled:", " ".join(f"{x:.3f}" for x in nights))
print(f"heavy tail sigma10: skilled {tail[0]:.3f} naive {tail[1]:.3f} gap {tail[0]-tail[1]:.3f}")
g = {s: a-b for s, (a, b) in res.items()}
checks = [g[10] >= 0.30, max(nights)-min(nights) < 0.03, g[60] >= 0.10, g[120] < 0.10,
          tail[0]-tail[1] >= 0.20]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 5 else 'FAIL'} {held}/5 predictions held; gap s10 {g[10]:.3f} "
      f"s60 {g[60]:.3f} s120 {g[120]:.3f}; nights {nights[0]:.3f}->{nights[3]:.3f}; "
      f"heavy-tail gap {tail[0]-tail[1]:.3f}; checks {checks}")
