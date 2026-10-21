# Iteration 1: assertion code was buggy and the loose prediction below was partly refuted (see RESULT of iteration 2).
# Prediction (before run): on an 8-connected octile grid (diagonal cost sqrt2) the weighted-A* gain again sits at w<=1.25
# on open/scattered maps and cost penalty stays <5%; but with FLAT diagonal cost 1 and an octile (sqrt2) heuristic the
# heuristic is inadmissible-inconsistent in the other direction: a Chebyshev heuristic is the matching one, and using the
# wrong one at w=1 changes the returned path COST or expansions by >10%.
import heapq, math
def mk(kind, n=40):
    g = [[0]*n for _ in range(n)]
    if kind == "bars":
        for i, x in enumerate(range(6, n-6, 6)):
            for y in range(n): g[y][x] = 1
            g[0 if i % 2 else n-1][x] = 0; g[1 if i % 2 else n-2][x] = 0
    if kind == "blocks":
        for y in range(n):
            for x in range(n):
                if (x*7+y*13) % 11 == 0 and (x, y) not in ((0, 0), (n-1, n-1)): g[y][x] = 1
    return g
D = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
def astar(g, s, t, h, w, diag):
    n = len(g); best = {s: 0.0}; q = [(w*h(s), 0.0, s)]; done = set(); ex = 0
    while q:
        f, c, p = heapq.heappop(q)
        if p in done: continue
        done.add(p); ex += 1
        if p == t: return c, ex
        for dx, dy in D:
            a, b = p[0]+dx, p[1]+dy
            if not (0 <= a < n and 0 <= b < n) or g[b][a]: continue
            if dx and dy and (g[p[1]][a] or g[b][p[0]]): continue   # no corner cutting
            nc = c + (diag if dx and dy else 1.0)
            if nc < best.get((a, b), 1e9): best[(a, b)] = nc; heapq.heappush(q, (nc + w*h((a, b)), nc, (a, b)))
    return None, ex
W = [1, 1.1, 1.25, 1.5, 2, 5]
out = {}
for kind in ("open", "bars", "blocks"):
    g = mk(kind); n = len(g); s = (0, 0); t = (n-1, n-1)
    def octile(p):
        dx, dy = abs(p[0]-t[0]), abs(p[1]-t[1]); return (dx+dy) + (math.sqrt(2)-2)*min(dx, dy)
    def cheb(p): return max(abs(p[0]-t[0]), abs(p[1]-t[1]))
    opt, e1 = astar(g, s, t, octile, 1, math.sqrt(2))
    rows = [(w,)+astar(g, s, t, octile, w, math.sqrt(2)) for w in W]
    print(kind, "opt=%.2f exp1=%d" % (opt, e1), [(w, e, round(c/opt, 3)) for w, c, e in rows])
    # flat diagonal cost 1: matching heuristic is Chebyshev; octile is then over-estimating
    fc_opt, fe_c = astar(g, s, t, cheb, 1, 1.0)
    fo_cost, fe_o = astar(g, s, t, octile, 1, 1.0)
    print("   flat-diag: cheb cost=%.2f exp=%d | octile-heuristic cost=%.2f exp=%d" % (fc_opt, fe_c, fo_cost, fe_o))
    out[kind] = (rows, e1, opt, fc_opt, fo_cost, fe_c, fe_o)
def exp_at(k, w): return [x[2] for x in out[k][0] if x[0] == w][0]
def cost_at(k, w): return [x[1] for x in out[k][0] if x[0] == w][0] / out[k][2]
# per map: does w=1.25 cut expansions by half? (open map is already perfect at w=1: 40 expansions = path length)
halved = {k: exp_at(k, 1.25) < 0.5 * out[k][1] for k in out}
maxpen = {k: round(max(cost_at(k, w) for w in W), 3) for k in out}
inad_extra = {k: out[k][4] - out[k][3] for k in out}         # octile-under-flat-diag cost minus Chebyshev cost
exp_ratio = {k: round(out[k][6] / out[k][5], 2) for k in out}  # expansions octile/cheb under flat diag
ok = halved["blocks"] and not halved["open"] and not halved["bars"] and max(maxpen.values()) >= 1.05 and all(v < 1e-9 for v in inad_extra.values())
print("RESULT: %s halved_by_w1.25=%s max_cost_ratio=%s flat_diag_octile_extra_cost=%s flat_diag_expansion_ratio_octile_vs_cheb=%s" %
      ("PASS" if ok else "FAIL", halved, maxpen, {k: round(v, 2) for k, v in inad_extra.items()}, exp_ratio))
