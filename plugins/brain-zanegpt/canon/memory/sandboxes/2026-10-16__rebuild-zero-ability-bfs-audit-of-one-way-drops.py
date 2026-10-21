# Own fixture: random 7-room levels, 2 abilities (bit0, bit1). Edges: two-way or one-way drop, optional ability gate.
# Abilities are picked up on entering a room. Softlock = some reachable (room, abilities) state cannot reach GOAL.
# Audit = flag each drop whose destination, with ZERO abilities, cannot reach GOAL. Exact = state search.
# Scenario B (built to break): a consumable gate - using a gated edge spends the ability (non-monotone).
import random
N, START, GOAL = 7, 0, 6
def gen(rng):
    pick = {r: (1 << rng.randrange(2)) if rng.random() < .4 else 0 for r in range(N)}
    edges = []
    for _ in range(rng.randrange(9, 14)):
        a, b = rng.sample(range(N), 2)
        gate = rng.choice([0, 0, 1, 2])
        edges.append((a, b, gate, rng.random() < .35))  # (from, to, gate, oneway)
    return pick, edges
def moves(state, pick, edges, consume):
    r, ab = state
    for a, b, g, one in edges:
        for (x, y) in ((a, b),) if one else ((a, b), (b, a)):
            if x == r and (g == 0 or ab & g):
                nab = (ab & ~g if consume and g else ab) | pick[y]
                yield (y, nab)
def reach(srcs, pick, edges, consume):
    seen = set(srcs); st = list(srcs)
    while st:
        s = st.pop()
        for t in moves(s, pick, edges, consume):
            if t not in seen: seen.add(t); st.append(t)
    return seen
def run(consume, n=4000, seed=7):
    rng = random.Random(seed); soft = miss = flags = false = 0
    for _ in range(n):
        pick, edges = gen(rng)
        R = reach([(START, pick[START])], pick, edges, consume)
        softlocked = any(not any(r == GOAL for r, _ in reach([s], pick, edges, consume)) for s in R if s[0] != GOAL) \
            if any(r == GOAL for r, _ in R) else False
        drops = [e for e in edges if e[3]]
        flagged = [e for e in drops if not any(r == GOAL for r, _ in reach([(e[1], pick[e[1]])], pick, edges, consume))
                   and any(s[0] == e[0] for s in R)]
        soft += softlocked; flags += bool(flagged)
        if softlocked and not flagged: miss += 1
        if flagged and not softlocked: false += 1
    return soft, miss, flags, false
for name, c in (("monotone", False), ("consumable", True)):
    s, m, f, fa = run(c)
    print("%s softlocked=%d missed=%d flagged=%d false-alarm=%d (%.0f%% of flags)" % (name, s, m, f, fa, 100*fa/max(f, 1)))
    if not c: mono = (s, m, f, fa)
    else: cons = (s, m, f, fa)
ok = mono[1] == 0 and mono[3] > 0 and cons[1] > 0
print("RESULT: %s monotone missed %d of %d softlocked, false alarms %d of %d flagged levels (%.0f%%); consumable gates missed %d of %d" % (
    "PASS" if ok else "FAIL", mono[1], mono[0], mono[3], mono[2], 100*mono[3]/max(mono[2], 1), cons[1], cons[0]))
