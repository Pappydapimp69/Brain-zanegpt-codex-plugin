"""Kernel apply: PATHFINDING/astar/uniform-diagonal-cost... (octile) + PATHFINDING/integration/a-found-path-must-be-consumed
+ PATHFINDING/navmesh-vs-grid/when-grid-still-wins (cheap local patching).
PREDICTION (before running): on 300 deterministic 20x20 maps (28% walls, hash-generated, seed parameter) solved by both cost
models: (a) the uniform-diagonal route differs from the octile route in 5-30% of maps (kernel reported 16.8%) and is
strictly longer in true Euclidean length in a smaller share than 'differs' (ties exist); (b) a greedy step-toward-goal walker
gets stuck on at least 15% of maps where A* found a route, while consuming the A* path never gets stuck; (c) blocking one
cell on the path and replanning touches exactly 1 grid cell and the new route avoids it. BREAK: forbid diagonal corner-cutting
and see whether the route-change share survives."""
import heapq, math, sys

W = H = 20
def make(seed, dens=28):
    g = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            v = (x * 73856093 ^ y * 19349663 ^ seed * 83492791) & 0xFFFFFF
            v = (v * 2654435761 >> 7) % 100
            g[y][x] = 1 if v < dens else 0
    g[0][0] = g[H - 1][W - 1] = 0
    return g

D8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
def astar(g, uniform, cut=True, s=(0, 0), t=None):
    t = t or (W - 1, H - 1)
    def h(p):
        dx, dy = abs(p[0] - t[0]), abs(p[1] - t[1])
        return max(dx, dy) if uniform else (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)
    openq = [(h(s), 0, s)]; best = {s: 0.0}; par = {}
    n = 0
    while openq:
        f, _, p = heapq.heappop(openq)
        if p == t:
            path = [p]
            while p in par: p = par[p]; path.append(p)
            return path[::-1]
        for dx, dy in D8:
            q = (p[0] + dx, p[1] + dy)
            if not (0 <= q[0] < W and 0 <= q[1] < H) or g[q[1]][q[0]]: continue
            if dx and dy and not cut and (g[p[1]][p[0] + dx] or g[p[1] + dy][p[0]]): continue
            c = best[p] + (1 if uniform or not (dx and dy) else math.sqrt(2))
            if c < best.get(q, 1e18) - 1e-12:
                best[q] = c; par[q] = p; n += 1; heapq.heappush(openq, (c + h(q), n, q))
    return None

def elen(path): return sum(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(path, path[1:]))

def study(seeds, cut):
    both = diff = longer = 0
    for sd in seeds:
        g = make(sd); u = astar(g, True, cut); o = astar(g, False, cut)
        if u and o:
            both += 1
            if u != o: diff += 1
            if elen(u) > elen(o) + 1e-9: longer += 1
    return both, diff, longer

SEEDS = range(300)
ok = True
both, diff, longer = study(SEEDS, True)
print(f"S1 corner-cutting allowed: solved by both {both}/300, route differs {diff} ({100*diff/both:.1f}%), strictly longer true length {longer} ({100*longer/both:.1f}%)")
miss_a = not (0.05 <= diff / both <= 0.30)   # prediction (a) window; recorded, not gated
ok &= longer <= diff and longer > 0
b2, d2, l2 = study(SEEDS, False)
print(f"S2 BREAK no corner-cutting: solved {b2}/300, route differs {d2} ({100*d2/b2:.1f}%), strictly longer {l2} ({100*l2/b2:.1f}%)")

# S3 greedy walker vs consuming the path
def greedy_stuck(g, limit=200):
    p = (0, 0); t = (W - 1, H - 1); seen = set()
    for _ in range(limit):
        if p == t: return False
        cands = [(math.hypot(p[0] + dx - t[0], p[1] + dy - t[1]), (p[0] + dx, p[1] + dy)) for dx, dy in D8
                 if 0 <= p[0] + dx < W and 0 <= p[1] + dy < H and not g[p[1] + dy][p[0] + dx]]
        d, q = min(cands) if cands else (1e9, p)
        if d >= math.hypot(p[0] - t[0], p[1] - t[1]): return True   # no improving neighbour: stuck
        p = q
    return True
solved = stuck_g = stuck_a = 0
for sd in SEEDS:
    g = make(sd); o = astar(g, False)
    if not o: continue
    solved += 1; stuck_g += greedy_stuck(g)
    stuck_a += any(g[y][x] for x, y in o) or o[-1] != (W - 1, H - 1)
print(f"S3 A* solved {solved}; greedy walker stuck {stuck_g} ({100*stuck_g/solved:.1f}%); path-consumer stuck {stuck_a}")
ok &= stuck_g / solved >= 0.15 and stuck_a == 0

# S4 local patch
patched = replanned = avoided = 0
for sd in SEEDS:
    g = make(sd); o = astar(g, False)
    if not o or len(o) < 4: continue
    cell = o[len(o) // 2]; g[cell[1]][cell[0]] = 1; patched += 1       # ONE cell flipped
    n = astar(g, False)
    if n: replanned += 1; avoided += cell not in n
print(f"S4 patch one cell: {patched} patched, replan found {replanned}, new route avoids the cell {avoided}; cells touched per patch: 1")
ok &= avoided == replanned and replanned > 0
# S5 density sweep: does the route-change share depend on wall density?
sweep = []
for dens in (0, 10, 20, 28):
    bb = dd = 0
    for sd in range(120):
        g = make(sd, dens); u = astar(g, True); o = astar(g, False)
        if u and o: bb += 1; dd += u != o
    sweep.append((dens, bb, round(100 * dd / bb, 1)))
print("S5 (wall density %, solved, route differs %):", sweep)
ok &= sweep[0][2] == 0 and sweep[1][2] > 0 and sweep[3][2] > sweep[1][2]
print("prediction (a) window 5-30% missed:", miss_a)
print("RESULT:", "PASS" if ok else "FAIL",
      f"(prediction window 5-30% missed: {miss_a}) uniform route differs {100*diff/both:.1f}% (strictly longer {100*longer/both:.1f}%), no-corner-cut {100*d2/b2:.1f}%; greedy stuck {100*stuck_g/solved:.1f}% vs path-consumer 0; one-cell patch replans {replanned}/{patched}")
