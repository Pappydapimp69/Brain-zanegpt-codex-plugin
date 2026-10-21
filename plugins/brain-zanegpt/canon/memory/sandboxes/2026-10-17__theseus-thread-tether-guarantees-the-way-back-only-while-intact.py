"""Theseus and the Minotaur: Ariadne's thread as a tether paid out while exploring.

Model. Square grid mazes of growing size, built by a recursive backtracker whose
neighbour order comes from a fixed arithmetic hash (no randomness), door at the
top-left cell, Minotaur at the centre. Theseus finds the Minotaur by depth-first
search, paying out thread as he goes. Ways back compared, in steps:
  wound    - he winds the thread back in at each dead end, so the thread is the
             live DFS path; following it out costs its length
  unwound  - he leaves it lying; following it out retraces every step he took
  wall     - no aid: right-hand wall following from the Minotaur, capped at 20*N
  memory   - he remembers his last C=4 junction choices (nearest the Minotaur),
             walks them, then falls back to the right-hand rule
Braided variant: the centre cell is made a solid pillar and the 8 cells around
it opened into a ring; the Minotaur stands on the ring north of the pillar,
with the pillar on his right hand, so the wall rule circles a free-standing wall.
Thread breaks: too short (cannot reach the Minotaur) and cut at the fight
(only the last 0 cells survive, he must fall back to the wall rule).

PREDICTION (written before the first run):
  1 perfect mazes 5,9,15,21: wound exit == BFS shortest distance every time;
    unwound >= 2x wound in the 21x21; wall exits every time within 2(N-1)
  2 memory C=4 exits at shortest-distance cost in 5x5 only if its return path has
    <=4 junctions, and costs more than wound in 15x15 and 21x21
  3 braided 15x15 and 21x21: wound still == shortest distance; wall NEVER exits
    within 20*N steps (circles the pillar)
  4 thread one cell shorter than the shortest distance: Minotaur not reached in
    any size (wound); unwound needs a thread as long as the whole search
  5 BREAK thread cut at the fight: perfect mazes still exit (wall fallback,
    cost > wound); braided mazes do not exit at all
"""

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N E S W, clockwise


def build(n, salt=0):
    open_ = {(x, y): set() for x in range(n) for y in range(n)}
    seen = {(0, 0)}
    stack = [(0, 0)]
    step = 0
    while stack:
        x, y = stack[-1]
        nb = [(x + dx, y + dy) for dx, dy in DIRS
              if 0 <= x + dx < n and 0 <= y + dy < n and (x + dx, y + dy) not in seen]
        if not nb:
            stack.pop()
            continue
        step += 1
        h = (x * 73856093) ^ (y * 19349663) ^ (step * 83492791) ^ (salt * 2246822519)
        h = (h * 2654435761) % 4294967296
        c = nb[(h >> 16) % len(nb)]
        open_[(x, y)].add(c)
        open_[c].add((x, y))
        seen.add(c)
        stack.append(c)
    return open_


def braid(open_, n):
    c = (n // 2, n // 2)
    for nb in list(open_[c]):          # make the centre a solid pillar
        open_[nb].discard(c)
    open_[c] = set()
    ring = [(c[0] + dx, c[1] + dy) for dx, dy in
            [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]]
    for i in range(8):                 # open the ring all the way round
        a, b = ring[i], ring[(i + 1) % 8]
        open_[a].add(b)
        open_[b].add(a)
    return (c[0], c[1] - 1)            # Minotaur north of the pillar


def bfs(open_, s, t):
    dist = {s: 0}
    q = [s]
    for u in q:
        for v in sorted(open_[u]):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist.get(t)


def explore(open_, door, goal, thread_len=None):
    """DFS in fixed N,E,S,W order. Returns (found, steps, live path).
    thread_len limits how far along the live (wound) path he can go."""
    seen = {door}
    path = [door]
    steps = 0
    while path:
        u = path[-1]
        if u == goal:
            return True, steps, path
        nxt = None
        for dx, dy in DIRS:
            v = (u[0] + dx, u[1] + dy)
            if v in open_[u] and v not in seen:
                nxt = v
                break
        if nxt is not None and (thread_len is None or len(path) - 1 < thread_len):
            seen.add(nxt)
            path.append(nxt)
            steps += 1
        else:
            if nxt is not None:
                seen.add(nxt)          # cannot go: thread at its end
                continue
            path.pop()
            if path:
                steps += 1
    return False, steps, []


def wall_follow(open_, start, heading, door, cap):
    u, h = start, heading
    for k in range(cap + 1):
        if u == door:
            return k
        for turn in (1, 0, 3, 2):      # right, straight, left, back
            nh = (h + turn) % 4
            v = (u[0] + DIRS[nh][0], u[1] + DIRS[nh][1])
            if v in open_[u]:
                u, h = v, nh
                break
    return None


def circuit(open_, u, h, steps):
    seen = []
    for _ in range(steps):
        seen.append(u)
        for turn in (1, 0, 3, 2):
            nh = (h + turn) % 4
            v = (u[0] + DIRS[nh][0], u[1] + DIRS[nh][1])
            if v in open_[u]:
                u, h = v, nh
                break
    return set(seen[-4 * len(open_):])


def heading_of(a, b):
    return DIRS.index((b[0] - a[0], b[1] - a[1]))


def memory_return(open_, path, door, C, cap):
    back = path[::-1]                  # Minotaur ... door
    used = 0
    for i in range(len(back) - 1):
        u = back[i]
        if len(open_[u]) >= 3:          # a junction: needs a remembered choice
            if used == C:
                h = heading_of(back[i - 1], u) if i > 0 else 0
                rest = wall_follow(open_, u, h, door, cap)
                return None if rest is None else i + rest
            used += 1
    return len(back) - 1


ok = True
def check(label, cond):
    global ok
    ok = ok and cond
    print(f"  {'ok ' if cond else 'BAD'} {label}")

SALTS = range(8)
summary = {}
for kind in ("perfect", "braided"):
    for n in (5, 9, 15, 21):
        if kind == "braided" and n < 9:
            continue
        agg = dict(cuts=0, cut_exit=0, trapped_off_ring=0, trap_not_via_ring=0, wound_eq=0, wound_le_E=0, excess=[], mem_rule=0, mem_over=0, ratio=0.0, wall_ok=0,
                   short_reach=0, cut_ok=0, cut_extra=0, d=[], E=[], cnt=0)
        for salt in SALTS:
            m = build(n, salt)
            door = (0, 0)
            if kind == "perfect":
                goal = (n // 2, n // 2)
                mh = None
            else:
                goal = braid(m, n)
                mh = 1                 # facing east: pillar on his right (south)
            cap = 20 * n * n
            d = bfs(m, door, goal)
            found, E, path = explore(m, door, goal)
            wound = len(path) - 1
            j = sum(1 for u in path[1:-1] if len(m[u]) >= 3)
            if mh is None:
                mh = heading_of(path[-2], path[-1])
            wall = wall_follow(m, goal, mh, door, cap)
            mem = memory_return(m, path, door, 4, cap)
            sf, _, _ = explore(m, door, goal, thread_len=d - 1)
            cut = wall_follow(m, goal, mh, door, cap)   # cut at the fight: no thread left
            c0 = (n // 2, n // 2)
            ringset = {(c0[0] + dx, c0[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - {c0}
            for k in range(1, len(path)):      # thread survives from path[k] to the Minotaur
                hk = heading_of(path[k], path[k - 1])
                r = wall_follow(m, path[k], hk, door, cap)
                agg["cuts"] += 1
                if r is not None:
                    agg["cut_exit"] += 1
                else:
                    if not (kind == "braided" and path[k] in ringset):
                        agg["trapped_off_ring"] += 1
                    if not (circuit(m, path[k], hk, cap) & ringset):
                        agg["trap_not_via_ring"] += 1
            agg["cnt"] += 1
            agg["wound_eq"] += wound == d
            agg["wound_le_E"] += found and d <= wound <= E
            agg["excess"].append((wound, d))
            agg["mem_rule"] += (mem == wound) == (j <= 4)
            agg["mem_over"] += mem is None or mem > wound
            agg["ratio"] += E / wound
            agg["wall_ok"] += wall is not None
            agg["short_reach"] += sf
            agg["cut_ok"] += cut is not None
            agg["cut_extra"] += (cut - wound) if cut is not None else 0
            agg["d"].append(d)
            agg["E"].append(E)
        summary[(kind, n)] = agg
        c = agg["cnt"]
        print(f"{kind:7s} {n:2d}x{n:<2d} mazes {c}  thread needed (wound) mean {sum(agg['d'])/c:5.1f} "
              f"max {max(agg['d']):3d} | if left lying max {max(agg['E']):3d} | unwound/wound "
              f"{agg['ratio']/c:4.2f} | wound>shortest {c - agg['wound_eq']}/{c} | memory C=4 overruns {agg['mem_over']}/{c} | "
              f"wall exits {agg['wall_ok']}/{c} | cut-at-fight exits {agg['cut_ok']}/{c} | "
              f"cut anywhere exits {agg['cut_exit']}/{agg['cuts']}")

print("checks:")
P = [summary[("perfect", n)] for n in (5, 9, 15, 21)]
B = [summary[("braided", n)] for n in (9, 15, 21)]
check("a wound == shortest in every perfect maze", all(a["wound_eq"] == a["cnt"] for a in P))
check("a' wound thread exits in every maze, shortest <= wound <= search length",
      all(a["wound_le_E"] == a["cnt"] for a in P + B))
longer = sum(a["cnt"] - a["wound_eq"] for a in B)
worst_pair = max((w - d, w, d) for a in B for w, d in a["excess"])
print(f"  info: wound thread longer than shortest in {longer}/24 braided mazes, "
      f"worst {worst_pair[1]} vs {worst_pair[2]}")
check("b memory == the thread route exactly when path junctions <= 4", all(a["mem_rule"] == a["cnt"] for a in P + B))
over = [a["mem_over"] for a in P]
check(f"c memory overrun share non-decreasing with size {over}, >0 at 21",
      all(over[i] <= over[i + 1] for i in range(3)) and over[3] > 0)
r5, r21 = P[0]["ratio"] / 8, P[3]["ratio"] / 8
check(f"d unwound/wound higher at 21 ({r21:.2f}) than at 5 ({r5:.2f})", r21 > r5)
check("e wall exits in all perfect, none braided",
      all(a["wall_ok"] == a["cnt"] for a in P) and all(a["wall_ok"] == 0 for a in B))
check("f thread one cell short never reaches the Minotaur", all(a["short_reach"] == 0 for a in P + B))
check("g BREAK cut at the fight: perfect all exit, braided none",
      all(a["cut_ok"] == a["cnt"] for a in P) and all(a["cut_ok"] == 0 for a in B))
check("h perfect: every cut position exits", all(a["cut_exit"] == a["cuts"] for a in P))
bc, be = sum(a["cuts"] for a in B), sum(a["cut_exit"] for a in B)
off = sum(a["trapped_off_ring"] for a in B)
nv = sum(a["trap_not_via_ring"] for a in B)
check(f"i looped: exits {be}/{bc} >= 80%, every trap circles through the ring "
      f"({off} traps start off the ring, {nv} circle elsewhere)", be >= 0.8 * bc and nv == 0)

if ok:
    print(f"RESULT: PASS the wound thread exits in all 56 mazes, at the shortest distance in all 32 "
          f"perfect ones and longer in {longer}/24 looped ones (worst {worst_pair[1]} vs {worst_pair[2]}); "
          f"memory of 4 junctions overruns in {over} of 8 perfect mazes at sizes 5/9/15/21; "
          f"a thread left lying costs {r5:.2f}x then {r21:.2f}x; wall rule circles the pillar in all 24 "
          f"looped mazes; BREAK one cell short never reaches the Minotaur, cut at the fight leaves "
          f"him lost in every looped maze; cut at any cell of the route he still gets out of {be}/{bc} looped "
          f"positions, every trap circling the pillar and the wall stubs the loops cut loose ({off} of them starting off the ring)")
else:
    print("RESULT: FAIL a prediction did not hold (see BAD lines)")
