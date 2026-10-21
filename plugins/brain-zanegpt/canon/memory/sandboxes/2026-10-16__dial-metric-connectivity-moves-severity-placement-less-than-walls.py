"""Loop-2 variant of the distance-dial question: does the dial's graph connectivity (4-way vs 8-way
BFS) matter as much as BFS vs Euclid? Beats at severity 2,4,6,8,10 (target fraction s/10 of the max
distance). Each beat is placed on the cell whose dial reading is nearest the target; the TRUE distance
is 4-way walking cost (grid movement is 4-way). Fit = mean exp(-((true/mx_true - s/10)/0.25)^2).
Assumption: connectivity is a second-order detail. Prediction (before run): on the serpentine map
8-way dial fit is within 0.05 of 4-way (walls dominate), but on an open map 8-way dial is worse than 4-way
by at least 0.03 (diagonal shortcuts the true walk does not have), and Euclid is worst on serpentine.
Breaker: open map with 4-way true movement, where Euclid and 8-way should be near-equal (within 0.03)."""
import math
from collections import deque
N = 21
def bfs(walls, diag):
    d = {(0, 0): 0}; q = deque([(0, 0)])
    mv = [(1,0),(-1,0),(0,1),(0,-1)] + ([(1,1),(1,-1),(-1,1),(-1,-1)] if diag else [])
    while q:
        x, y = q.popleft()
        for dx, dy in mv:
            n = (x+dx, y+dy)
            if 0 <= n[0] < N and 0 <= n[1] < N and n not in walls and n not in d:
                d[n] = d[(x, y)] + 1; q.append(n)
    return d
serp = set()
for i, x in enumerate(range(3, 20, 4)):
    serp |= {(x, y) for y in (range(0, 19) if i % 2 == 0 else range(2, 21))}
def fit(walls, kind):
    true = bfs(walls, False); cells = list(true); tm = max(true.values())
    if kind == "bfs4": r = {c: true[c] for c in cells}
    elif kind == "bfs8": e = bfs(walls, True); r = {c: e[c] for c in cells}
    else: r = {c: math.hypot(*c) for c in cells}
    rm = max(r.values()); tot = 0
    for s in (2, 4, 6, 8, 10):
        t = s / 10
        c = min(cells, key=lambda c: abs(r[c] / rm - t))
        tot += math.exp(-((true[c] / tm - t) / 0.25) ** 2)
    return tot / 5
R = {(m, k): fit(w, k) for m, w in (("open", set()), ("serp", serp)) for k in ("bfs4", "bfs8", "euclid")}
for k, v in R.items(): print(k, round(v, 3))
a = abs(R[("serp","bfs8")] - R[("serp","bfs4")]) <= 0.05
b = R[("open","bfs4")] - R[("open","bfs8")] >= 0.03
c = R[("serp","euclid")] < min(R[("serp","bfs4")], R[("serp","bfs8")])
e = abs(R[("open","euclid")] - R[("open","bfs8")]) <= 0.03
print(f"RESULT: {'PASS' if a and b and c and e else 'FAIL'} serp8-4={R[('serp','bfs8')]-R[('serp','bfs4')]:+.3f} "
      f"open4-8={R[('open','bfs4')]-R[('open','bfs8')]:+.3f} serp_euclid_worst={c} open_euclid_vs8={abs(R[('open','euclid')]-R[('open','bfs8')]):.3f}")
