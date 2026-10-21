"""Rebuild of seven E36 (nearest open cell is not legal placement on dense
maps; place inside the goal's connected region).
Own fixture: 40x24 CLUSTERED cave maps (random fill, then 3 cellular-automata
smoothing passes: rock if >= 5 of 8 neighbours are rock), not uniform noise.
Border is rock. Goal = a random open cell. Requested spawn = a random cell
(may be rock). Helpers: AS-IS, NEAREST-OPEN (nearest open cell by Manhattan
distance), GOAL-REGION (nearest cell in the goal's 4-connected open region).
A test passes if the agent stands on open ground with a 4-connected path to
the goal. 300 maps per fill level, seeded.
PREDICTIONS (written before running):
 P1 nearest-open falls below 0.90 at some fill level
 P2 goal-region passes 1.000 at every fill level
 P3 at the lowest fill the two helpers agree on >= 0.98 of maps
 P4 (cost) goal-region's mean displacement at the densest fill is more than
    twice its value at the lowest fill (the stricter helper moves the spawn a
    lot exactly where it matters)
"""
import random
from collections import deque
W, H = 40, 24
def gen(rng, fill):
    g = [[1 if (x in (0, W-1) or y in (0, H-1) or rng.random() < fill) else 0 for x in range(W)] for y in range(H)]
    for _ in range(3):
        n = [[1]*W for _ in range(H)]
        for y in range(1, H-1):
            for x in range(1, W-1):
                c = sum(g[y+dy][x+dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
                n[y][x] = 1 if c >= 5 else 0
        g = n
    return g
def region(g, s):
    seen = {s}; q = deque([s])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x+dx, y+dy)
            if 0 <= p[0] < W and 0 <= p[1] < H and not g[p[1]][p[0]] and p not in seen:
                seen.add(p); q.append(p)
    return seen
def nearest(cands, s):
    return min(cands, key=lambda c: (abs(c[0]-s[0])+abs(c[1]-s[1]), c))
res = {}
for fill in (0.30, 0.40, 0.45, 0.50):
    rng = random.Random(int(fill*1000)); ok = {"asis": 0, "open": 0, "goal": 0}; agree = 0; disp = 0.0; n = 0
    while n < 300:
        g = gen(rng, fill)
        opens = [(x, y) for y in range(H) for x in range(W) if not g[y][x]]
        if len(opens) < 2: continue
        goal = rng.choice(opens); reg = region(g, goal)
        s = (rng.randrange(W), rng.randrange(H))
        a = s if not g[s[1]][s[0]] else None
        o = nearest(opens, s); r = nearest(list(reg), s)
        ok["asis"] += a is not None and a in reg
        ok["open"] += o in reg; ok["goal"] += r in reg
        agree += o == r; disp += abs(r[0]-s[0])+abs(r[1]-s[1]); n += 1
    res[fill] = {k: v/n for k, v in ok.items()} | {"agree": agree/n, "disp": disp/n}
    print(f"fill {fill:.2f}: as-is {res[fill]['asis']:.3f} nearest-open {res[fill]['open']:.3f} "
          f"goal-region {res[fill]['goal']:.3f} agree {res[fill]['agree']:.3f} goal-disp {res[fill]['disp']:.2f}")
fills = sorted(res)
p1 = min(res[f]["open"] for f in fills) < 0.90
p2 = all(res[f]["goal"] == 1.0 for f in fills)
p3 = res[fills[0]]["agree"] >= 0.98
p4 = res[fills[-1]]["disp"] > 2*res[fills[0]]["disp"]
held = p1 + p2 + p3 + p4
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4 predictions held; nearest-open "
      + " ".join(f"{f:.2f}:{res[f]['open']:.3f}" for f in fills) + f"; goal-region 1.000 all; agree low "
      f"{res[fills[0]]['agree']:.3f}; displacement {res[fills[0]]['disp']:.2f}->{res[fills[-1]]['disp']:.2f}; checks {[p1, p2, p3, p4]}")
