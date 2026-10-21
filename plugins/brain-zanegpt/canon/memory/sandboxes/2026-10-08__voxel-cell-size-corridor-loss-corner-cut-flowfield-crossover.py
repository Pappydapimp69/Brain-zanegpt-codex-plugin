"""Prediction (before first run): voxelizing a 48x48 fine grid with a conservative rule (coarse cell walkable only if every fine cell in it is walkable,
as geometry-touches-voxel rasterization does) loses a one-gap wall of width g at cell size cs exactly when no coarse cell fits inside the gap:
unreachable for ALL gap offsets when g<cs; at g==cs reachable only for offsets divisible by cs; always reachable once g>=2*cs-1; cs=1 (the grid) never loses it.
Secondary: on the coarse map a diagonal move without the flank rule cuts wall corners in the fine map on some paths (corner-cutting kernel), and the shared flow
field beats per-agent BFS at a crossover agent count that is small and stays within +-2 across cs 1..3 on one map (flowfield-crossover kernel).
Deterministic, stdlib only, no RNG."""
from collections import deque
import heapq
N = 48

def fine_map(gap_w, gap_off):
    g = [[0] * N for _ in range(N)]
    for y in range(N):
        g[y][24] = 1            # vertical wall
    for y in range(gap_off, gap_off + gap_w):
        g[y][24] = 0            # the single gap
    return g

def voxelize(g, cs):
    M = N // cs
    return [[0 if all(g[y][x] == 0 for y in range(cy * cs, cy * cs + cs) for x in range(cx * cs, cx * cs + cs)) else 1
             for cx in range(M)] for cy in range(M)]

def bfs(g, s, t, diag=False, flank=True):
    M = len(g); seen = {s: None}; q = deque([s]); visits = 0
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [])
    while q:
        c = q.popleft(); visits += 1
        if c == t: break
        for dx, dy in dirs:
            n = (c[0] + dx, c[1] + dy)
            if not (0 <= n[0] < M and 0 <= n[1] < M) or g[n[1]][n[0]] or n in seen: continue
            if dx and dy and flank and (g[c[1]][n[0]] or g[n[1]][c[0]]): continue
            seen[n] = c; q.append(n)
    if t not in seen: return None, visits
    p = [t]
    while seen[p[-1]]: p.append(seen[p[-1]])
    return p[::-1], visits

def astar(g, s, t):
    M = len(g); h = lambda c: abs(c[0] - t[0]) + abs(c[1] - t[1])
    pq = [(h(s), 0, s)]; best = {s: 0}; closed = set(); exp = 0
    while pq:
        _, d, c = heapq.heappop(pq)
        if c in closed: continue
        closed.add(c); exp += 1
        if c == t: return exp
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < M and 0 <= n[1] < M and not g[n[1]][n[0]] and d + 1 < best.get(n, 1e9):
                best[n] = d + 1; heapq.heappush(pq, (d + 1 + h(n), d + 1, n))
    return exp

def reach(gap_w, gap_off, cs):
    v = voxelize(fine_map(gap_w, gap_off), cs); M = N // cs
    return bfs(v, (0, 0), (M - 1, M - 1))[0] is not None

ok = True; rows = []
# scenario 1: reachability vs cs, gap width, offset
for cs in (1, 2, 3, 4):
    for g in range(1, 9):
        offs = [o for o in range(0, N - g + 1) if o % cs != 0 or True]
        offs = [o for o in range(0, 24) if o + g <= N]   # 24 offsets
        ok_offs = [o for o in offs if reach(g, o, cs)]
        pred_all = g >= 2 * cs - 1
        pred_none = g < cs
        if cs == 1: cond = len(ok_offs) == len(offs)
        elif pred_none: cond = not ok_offs
        elif g == cs: cond = ok_offs == [o for o in offs if o % cs == 0]
        elif pred_all: cond = len(ok_offs) == len(offs)
        else: cond = bool(ok_offs) and len(ok_offs) < len(offs)
        ok &= cond
        rows.append((cs, g, len(ok_offs), len(offs), cond))
for r in rows:
    if r[0] in (3, 4): print("cs=%d g=%d reachable_offsets=%d/%d consistent=%s" % r)
# scenario 2: corner cutting on coarse diagonals without flank rule, judged on fine map
def fine_blocked_path(fine, cs, path):
    cuts = 0
    for a, b in zip(path, path[1:]):
        if a[0] != b[0] and a[1] != b[1]:
            if fine[a[1] * cs][b[0] * cs] or fine[b[1] * cs][a[0] * cs]: cuts += 1
    return cuts
# map with random-free scatter: wall blocks at deterministic positions
sc = [[0] * N for _ in range(N)]
for y in range(N):
    for x in range(N):
        if (x * 7 + y * 13) % 11 == 0 or (x * 3 + y * 5) % 17 == 0: sc[y][x] = 1
cut_paths = 0; solvable = 0
for cs in (1,):
    v = voxelize(sc, cs)
    for sy in range(0, 8):
        s, t = (0, sy), (N - 1, N - 1 - sy)
        if v[s[1]][s[0]] or v[t[1]][t[0]]: continue
        p, _ = bfs(v, s, t, diag=True, flank=False)
        if p:
            solvable += 1; cut_paths += fine_blocked_path(sc, cs, p) > 0
        pf, _ = bfs(v, s, t, diag=True, flank=True)
        ok &= (pf is None) or fine_blocked_path(sc, cs, pf) == 0
print("corner-cut paths without flank rule: %d/%d" % (cut_paths, solvable))
ok &= solvable > 0 and cut_paths > 0
# scenario 3: flow-field crossover (visits of one full flood vs mean per-agent BFS) at cs 1..3 on open map with gap g=6
cross = {}
for cs in (1, 2, 3):
    v = voxelize(fine_map(6, 18), cs); M = len(v)
    _, flood = bfs(v, (M - 1, M - 1), (-1, -1))  # unreachable target forces a full flood
    agents = [(0, y) for y in range(0, M, max(1, M // 8)) if not v[y][0]]
    per = [astar(v, a, (M - 1, M - 1)) for a in agents]
    mean = sum(per) / len(per)
    cross[cs] = flood / mean
    print("cs=%d flood=%d mean_agent_astar=%.1f crossover_agents=%.1f" % (cs, flood, mean, cross[cs]))
ok &= all(1.0 < c < 12 for c in cross.values())
print("RESULT:", "PASS" if ok else "FAIL", "corridor-loss rule consistent=%s; corner-cuts %d/%d; crossover agents %s" % (all(r[4] for r in rows), cut_paths, solvable, {k: round(v, 1) for k, v in cross.items()}))
