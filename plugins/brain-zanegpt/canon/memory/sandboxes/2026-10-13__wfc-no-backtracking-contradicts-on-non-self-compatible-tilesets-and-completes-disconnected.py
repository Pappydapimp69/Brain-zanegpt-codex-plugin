"""Prediction (before run): over every 3-tile adjacency set whose H and V matrices are sampled by stride (3478 sets, 5x5 grid),
no-backtracking WFC with eager arc-consistency propagation and first-option collapse (a) fails at initial propagation for
roughly a third of sets, (b) hits a contradiction AFTER a collapse in more than 0 sets (I predict 30 to 100), (c) among
sets that complete, treating tile 0 as walkable, leaves a disconnected walkable region in more than 0 completed grids.
Built to break: restricting to sets where some tile is self-compatible in both axes should reduce contradictions to 0 (the
condition under which the entry's 0% may hold); if it stays above 0 that explanation is refuted.
Deterministic (strided enumeration, first-option choice), stdlib only."""
W = 5; n = 3

def solve(H, V):
    dom = [[set(range(n)) for _ in range(W)] for _ in range(W)]
    def prop(q):
        while q:
            x, y = q.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < W and 0 <= ny < W): continue
                M = H if dx else V
                fwd = dx > 0 or dy > 0
                ok = {b for b in dom[ny][nx] if any((M[a][b] if fwd else M[b][a]) for a in dom[y][x])}
                if ok != dom[ny][nx]:
                    dom[ny][nx] = ok
                    if not ok: return False
                    q.append((nx, ny))
        return True
    if not prop([(x, y) for x in range(W) for y in range(W)]): return "init", None
    while True:
        cells = [(len(dom[y][x]), y, x) for y in range(W) for x in range(W) if len(dom[y][x]) > 1]
        if not cells: return "ok", [[min(dom[y][x]) for x in range(W)] for y in range(W)]
        _, y, x = min(cells); dom[y][x] = {min(dom[y][x])}
        if not prop([(x, y)]): return "contradiction", None

def connected(g):
    open_ = {(x, y) for y in range(W) for x in range(W) if g[y][x] == 0}
    if not open_: return True
    seen = set(); st = [next(iter(open_))]
    while st:
        c = st.pop()
        if c in seen: continue
        seen.add(c)
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m = (c[0] + d[0], c[1] + d[1])
            if m in open_ and m not in seen: st.append(m)
    return seen == open_

M = [[[(bits >> (3 * a + b)) & 1 for b in range(3)] for a in range(3)] for bits in range(1 << 9)]
tot = init = ok = con = disc = 0
sc_tot = sc_con = 0
for H in M[::7]:
    for V in M[::11]:
        tot += 1
        r, g = solve(H, V)
        selfc = any(H[t][t] and V[t][t] for t in range(3))
        if r == "init": init += 1
        elif r == "ok":
            ok += 1; disc += (not connected(g))
        else:
            con += 1
        if selfc and r != "init":
            sc_tot += 1; sc_con += (r == "contradiction")
print(tot, init, ok, con, disc, sc_tot, sc_con)
res = tot == 3478 and 1000 <= init and con > 0 and disc > 0
print("RESULT: %s of %d sets: %d fail at init, %d complete (%d with disconnected walkable region), %d contradict after a collapse; with a self-compatible tile %d of %d still contradict" %
      ("PASS" if res else "FAIL", tot, init, ok, disc, con, sc_con, sc_tot))
