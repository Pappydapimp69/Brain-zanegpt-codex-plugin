"""Sandbox: flow-field (one BFS from goal) vs per-agent A* crossover, 4-connected grids.
Prediction (before first run): crossover agents = BFS_cost / mean_A*_cost.
 - open map: crossover scales with nothing but ~constant across sizes 15..40 (A* cost ~ BFS cost*c) -> within 2x band across sizes.
 - maze/serpentine map: A* must expand nearly every reachable cell -> crossover <= 2 agents.
 - scattered-block map in between. Crossover spread across map classes at one size > 3x (BREAK of 'regardless').
"""
import heapq
from collections import deque

def make(kind, n):
    g = [[0]*n for _ in range(n)]
    if kind == "scatter":
        for y in range(n):
            for x in range(n):
                if (x*7 + y*13 + x*y) % 5 == 0 and (x, y) not in ((0,0),(n-1,n-1)): g[y][x] = 1
    elif kind == "serpentine":
        for y in range(1, n, 2):
            for x in range(n): g[y][x] = 1
            g[y][n-1 if (y//2) % 2 == 0 else 0] = 0
    return g

def nbrs(g, x, y):
    n = len(g)
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        a, b = x+dx, y+dy
        if 0 <= a < n and 0 <= b < n and not g[b][a]: yield a, b

def bfs_cost(g, goal):
    seen = {goal}; q = deque([goal]); c = 0
    while q:
        p = q.popleft(); c += 1
        for m in nbrs(g, *p):
            if m not in seen: seen.add(m); q.append(m)
    return c, seen

def astar_cost(g, s, t):
    h = lambda p: abs(p[0]-t[0]) + abs(p[1]-t[1])
    best = {s: 0}; pq = [(h(s), 0, s)]; done = set(); c = 0
    while pq:
        f, d, p = heapq.heappop(pq)
        if p in done: continue
        done.add(p); c += 1
        if p == t: return c
        for m in nbrs(g, *p):
            if d+1 < best.get(m, 1e9): best[m] = d+1; heapq.heappush(pq, (d+1+h(m), d+1, m))
    return None

def crossover(kind, n):
    g = make(kind, n); goal = (n-1, n-1)
    bc, reach = bfs_cost(g, goal)
    starts = sorted(p for p in reach if abs(p[0]-goal[0]) + abs(p[1]-goal[1]) >= n//2)
    starts = starts[::max(1, len(starts)//12)][:12]
    costs = [astar_cost(g, s, goal) for s in starts]
    return bc / (sum(costs)/len(costs))

res = {}
for kind in ("open", "scatter", "serpentine"):
    res[kind] = {n: crossover(kind, n) for n in (15, 25, 41)}
    print(kind, {n: round(v, 2) for n, v in res[kind].items()})
size_spread = {k: max(v.values())/min(v.values()) for k, v in res.items()}
class_spread = max(res[k][25] for k in res) / min(res[k][25] for k in res)
print("size spread (max/min across 15..40):", {k: round(v, 2) for k, v in size_spread.items()})
print("class spread at n=25:", round(class_spread, 2))
ok = size_spread["open"] < 2 and res["serpentine"][25] <= 2 and class_spread > 3
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" open size spread {size_spread['open']:.2f}x, serpentine crossover {res['serpentine'][25]:.2f} agents, class spread {class_spread:.1f}x at n=25")
