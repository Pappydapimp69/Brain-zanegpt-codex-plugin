"""Does the paths/weakest-link loop starve quiet areas? Deterministic model of
brain train's seam queue: weakest-link order (fewest edges on the less-connected
node) interleaved 1:3 with strong-path order (max node strength), as in
_paths_order with follow_share=0.75. Each pick lands one lesson = one new edge.
Variants: specificity weighting on/off (strength / sqrt(deg a * deg b)),
decay per DAY vs per LESSON, and an idle week in the middle. No RNG."""
import math

HUB = [f"h{i}" for i in range(10)]
QUIET = [f"q{i}" for i in range(30)]
NODES = HUB + QUIET

def seed():
    edges = []                                  # (a, b, day)
    for i in range(10):                         # dense hub: every hub pair, used 3x
        for j in range(i + 1, 10):
            if (i + j) % 2:                     # half the hub pairs linked (used 3x); half left as seams
                edges += [(HUB[i], HUB[j], 0)] * 3
    for k in range(0, 30, 3):                   # a third of quiet nodes touch the hub once
        edges.append((QUIET[k], HUB[k % 10], 0))
    return edges

def strengths(edges, day, n_lessons, spec, mode, decay=0.85):
    deg = {}
    pairs = {}
    for idx, (a, b, d) in enumerate(edges):
        age = (day - d) if mode == "day" else (n_lessons - idx)
        pairs[(a, b)] = pairs.get((a, b), 0.0) + decay ** max(0, age) if mode != "lesson" else \
            pairs.get((a, b), 0.0) + decay ** (max(0, age) / 4)   # per-lesson: fade 0.85 per 4 lessons
    for a, b in pairs:
        deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
    ns = {}
    for (a, b), s in pairs.items():
        if spec:
            s /= math.sqrt(deg[a] * deg[b])
        ns[a] = ns.get(a, 0) + s; ns[b] = ns.get(b, 0) + s
    return ns, deg, set(pairs) | {(b, a) for a, b in pairs}

def run(spec, mode, idle=False, steps=120, per_day=2, tie='name'):
    edges = seed()
    quiet_picks = hub_picks = 0
    covered = set()
    day = 0
    for step in range(steps):
        if step and step % per_day == 0:
            day += 8 if (idle and step == steps // 2) else 1
        ns, deg, seen = strengths(edges, day, len(edges), spec, mode)
        in_graph = set(deg)
        cand = [(a, b) for i, a in enumerate(NODES) for b in NODES[i + 1:]
                if (a, b) not in seen and (a in in_graph or b in in_graph)]
        weak = sorted(cand, key=lambda c: (min(deg.get(c[0], 0), deg.get(c[1], 0)),
                                           max(deg.get(c[0], 0), deg.get(c[1], 0)) if tie == 'deg' else 0, c))
        strong = sorted(cand, key=lambda c: (-max(ns.get(c[0], 0), ns.get(c[1], 0)), c))
        a, b = (weak if mode == "off" or step % 4 == 0 else strong)[0]
        edges.append((a, b, day))
        if a in QUIET and b in QUIET:
            quiet_picks += 1
        covered |= {x for x in (a, b) if x in QUIET}
        if a in HUB or b in HUB:
            hub_picks += 1
    return quiet_picks / steps, len(covered), hub_picks / steps

V = [("weakest only (paths off)", False, "off", False),
     ("paths, raw strength, per-day fade", False, "day", False),
     ("paths + specificity, per-day fade", True, "day", False),
     ("paths + specificity, per-day fade, idle week", True, "day", True),
     ("paths + specificity, per-lesson fade, idle week", True, "lesson", True)]
R = {}
TIE = __import__('sys').argv[1] if len(__import__('sys').argv) > 1 else 'name'
print('weakest-link tie-break:', TIE)
for name, spec, mode, idle in V:
    R[name] = run(spec, mode, idle, tie=TIE)
    q, c, h = R[name]
    print(f"{name:50s} quiet-quiet picks {q:5.1%}  quiet nodes covered {c:2d}/30  hub-touching picks {h:5.1%}")
raw = R[V[1][0]][0]; spec = R[V[2][0]][0]; off = R[V[0][0]][0]
idle_day = R[V[3][0]][0]; idle_les = R[V[4][0]][0]
print(f"RESULT: {'PASS' if spec > raw and idle_les > idle_day else 'FAIL'} "
      f"quiet-quiet share: off {off:.1%}, raw {raw:.1%}, +specificity {spec:.1%}; idle week per-day {idle_day:.1%} vs per-lesson {idle_les:.1%}")
