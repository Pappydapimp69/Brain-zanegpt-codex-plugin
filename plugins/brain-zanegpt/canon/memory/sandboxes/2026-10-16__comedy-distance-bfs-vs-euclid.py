"""Toy: a comedy beat lands only if harm <= the framing's distance from grounded reality
(severe harm needs distance, mild harm needs closeness). Framings sit on a 2D map with walls;
distance should be WALK distance (BFS) from the grounded start, not straight-line (Euclid).
Escalation schedule picks each beat's harm = estimated distance of its framing. Score = share of
beats that land (harm <= true BFS distance). Deterministic grid, no RNG."""
from collections import deque
import math
GRID = ["S.#....",
        ".##.##.",
        "...#...",
        ".#...#.",
        "...#.F."]   # S grounded start; # wall = framing step you cannot jump; cells are framings
R, C = len(GRID), len(GRID[0])
def bfs(grid):
    d = {(0,0):0}; q = deque([(0,0)])
    while q:
        y,x = q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx = y+dy,x+dx
            if 0<=ny<R and 0<=nx<C and grid[ny][nx] != '#' and (ny,nx) not in d:
                d[(ny,nx)] = d[(y,x)]+1; q.append((ny,nx))
    return d
def run(grid, estimator):
    walk = bfs(grid); cells = [c for c in walk if c != (0,0)]
    est = {c: estimator(c, walk) for c in cells}
    landed = sum(1 for c in cells if est[c] <= walk[c])          # harm never above true distance
    headroom = sum(est.values()) / sum(walk[c] for c in cells)    # share of the distance budget used
    inv = sum(1 for a in cells for b in cells if est[a] < est[b] and walk[a] > walk[b])  # escalation order wrong
    return landed, len(cells), headroom, inv
euclid = lambda cell, walk: round(math.hypot(*cell))                # straight-line, ignores walls
bfs_est = lambda cell, walk: walk[cell]                              # true walk distance
open_grid = ["."*C for _ in range(R)]
open_grid[0] = "S" + "."*(C-1)
res = {}
for name, g, e in (("wall map, Euclid estimate", GRID, euclid), ("wall map, BFS estimate", GRID, bfs_est),
                   ("BREAK: open map, Euclid estimate", open_grid, euclid), ("open map, BFS estimate", open_grid, bfs_est)):
    l,t,h,inv = run(g, e); res[name]=(l,t,h,inv)
    print(f"{name}: landed {l}/{t}, budget used {h:.2f}, order inversions {inv}")
W,B,O = res["wall map, Euclid estimate"], res["wall map, BFS estimate"], res["BREAK: open map, Euclid estimate"]
ok = B[2]==1.0 and B[3]==0 and W[2]<0.8 and W[3]>0 and O[3]>0 and O[2]>W[2]
print("RESULT: PASS" if ok else "RESULT: FAIL", f"wall map Euclid uses {W[2]:.2f} of the distance budget with {W[3]} order inversions vs BFS {B[2]:.2f}/{B[3]}; open map Euclid {O[2]:.2f}/{O[3]}")
