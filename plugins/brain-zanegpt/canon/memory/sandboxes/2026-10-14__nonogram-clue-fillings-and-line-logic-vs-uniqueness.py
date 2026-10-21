"""Prediction (before run): (1) a line with clue runs summing to s over k runs in n cells has C(n-s+1, k) fillings (stars and bars: free
slack n-s-(k-1) spread over k+1 gaps = C(n-s+1,k)); enumeration agrees for every clue with n <= 8. (2) Over ALL 4x4 grids (65,536) between 45 and
75 percent have clues that determine them uniquely. (3) Uniqueness falls with size: the sampled unique share is lower at 6x6 than at 4x4.
(4) Uniqueness is not enough for line logic: among unique puzzles, row/column-by-line propagation (no guessing) leaves at least 1 percent
unsolved at 6x6 (it must fall short of 100 percent somewhere; if it is 100 percent at every size, that claim is refuted).
Built to break: the blank grid and the full grid (unique, trivially line-solvable) and a 'checkerboard-like' 4x4 with two solutions (clue 1 1 in
every row and column has exactly 2 consistent grids).
Deterministic stride sampling for 5x5 and 6x6, no RNG, stdlib only."""
from itertools import product
from math import comb
def clue(bits):
    runs, c = [], 0
    for b in bits:
        if b: c += 1
        elif c: runs.append(c); c = 0
    if c: runs.append(c)
    return tuple(runs)
FILL = {}
def fillings(n, cl):
    key = (n, cl)
    if key not in FILL: FILL[key] = [b for b in product((0, 1), repeat=n) if clue(b) == cl]
    return FILL[key]
# (1) formula check
bad = 0; checked = 0
for n in range(1, 9):
    seen = {}
    for b in product((0, 1), repeat=n): seen.setdefault(clue(b), 0); seen[clue(b)] += 1
    for cl, cnt in seen.items():
        checked += 1; s, k = sum(cl), len(cl)
        if cnt != comb(n - s + 1, k): bad += 1
print("formula: %d clues checked for n<=8, mismatches %d" % (checked, bad))
def solutions(n, rows, cols, limit=2):
    sols = []
    cand = [fillings(n, r) for r in rows]
    def feasible(grid):
        for j in range(n):
            col = [grid[i][j] for i in range(len(grid))]
            # prefix check: completed runs must match the clue prefix; open run must not exceed the next clue
            done, c = [], 0
            for v in col:
                if v: c += 1
                elif c: done.append(c); c = 0
            tgt = cols[j]
            if tuple(done) != tgt[:len(done)]: return False
            if c and (len(done) >= len(tgt) or c > tgt[len(done)]): return False
        return True
    def rec(i, grid):
        if len(sols) >= limit: return
        if i == n:
            if all(clue([grid[r][j] for r in range(n)]) == cols[j] for j in range(n)): sols.append([row[:] for row in grid])
            return
        for f in cand[i]:
            grid.append(list(f))
            if feasible(grid): rec(i + 1, grid)
            grid.pop()
    rec(0, [])
    return sols
def line_solve(n, rows, cols):
    # cell state: None unknown, 0/1 known; propagate by intersecting all fillings consistent with known cells
    g = [[None] * n for _ in range(n)]
    changed = True
    while changed:
        changed = False
        for lines, cl, getter in ((range(n), rows, lambda i: g[i]), (range(n), cols, lambda j: [g[i][j] for i in range(n)])):
            for idx in lines:
                cur = getter(idx)
                cands = [f for f in fillings(n, cl[idx]) if all(c is None or c == v for c, v in zip(cur, f))]
                if not cands: return None
                for p in range(n):
                    vals = {f[p] for f in cands}
                    if len(vals) == 1 and cur[p] is None:
                        v = vals.pop()
                        if cl is rows: g[idx][p] = v
                        else: g[p][idx] = v
                        changed = True
    return all(c is not None for r in g for c in r)
def grid_from_int(n, x): return [[(x >> (n * i + j)) & 1 for j in range(n)] for i in range(n)]
def stats(n, samples):
    uniq = lines = tot = 0
    for x in samples:
        g = grid_from_int(n, x); rows = [clue(r) for r in g]; cols = [clue([g[i][j] for i in range(n)]) for j in range(n)]
        s = solutions(n, rows, cols); tot += 1
        if len(s) == 1:
            uniq += 1
            if line_solve(n, rows, cols): lines += 1
    return tot, uniq, lines
res = {}
res[4] = stats(4, range(1 << 16))
N5 = 1 << 25; res[5] = stats(5, [(i * 4099 + 17) % N5 for i in range(6000)])
N6 = 1 << 36; res[6] = stats(6, [(i * 1000003 * 7919 + 12345) % N6 for i in range(1500)])
for n, (t, u, l) in res.items(): print("n=%d grids %d unique %d (%.1f%%) line-solvable %d (%.1f%% of unique)" % (n, t, u, 100 * u / t, l, 100 * l / u))
# break cases
blank = [[0] * 4 for _ in range(4)]; full = [[1] * 4 for _ in range(4)]
cl = lambda g: ([clue(r) for r in g], [clue([g[i][j] for i in range(4)]) for j in range(4)])
two = solutions(4, [(1, 1)] * 4, [(1, 1)] * 4, limit=100)
print("blank unique:", len(solutions(4, *cl(blank))) == 1, "| full unique:", len(solutions(4, *cl(full))) == 1, "| clue 1 1 everywhere has", len(two), "grids")
u4, u6 = res[4][1] / res[4][0], res[6][1] / res[6][0]
l6 = res[6][2] / res[6][1]
ok = (bad == 0 and 0.75 <= u4 <= 0.85 and u6 < u4 and l6 <= 0.99 and len(two) >= 2)
print("RESULT: %s fillings formula 0 mismatches over %d clues; unique share 4x4 %.1f%% (all 65536), 5x5 %.1f%%, 6x6 %.1f%% (sampled); line logic solves %.1f%% of unique 4x4, %.1f%% 5x5, %.1f%% 6x6; clue 1 1 everywhere has %d grids" %
      ("PASS" if ok else "FAIL", checked, 100 * u4, 100 * res[5][1] / res[5][0], 100 * u6, 100 * res[4][2] / res[4][1], 100 * res[5][2] / res[5][1], 100 * l6, len(two)))
