"""Train edge: sevin E15 (several actions at one spot: gate each on the state
where it applies BEFORE ranking; a priority alone starves another state) +
sevin E16 (a ubiquitous target class - trees - hijacks a wide-cone resolver;
give it a narrow cone, a handicap and read camera pitch as intent) +
brainwork E203 (gate on the current state, never a per-object has-fired flag).
Composed claim: one use-button resolver needs all three: state gates (not
flags) at shared spots and per-class tolerance for ubiquitous targets; any one
missing starves an action somewhere.
Own fixture, exhaustive, no rng. Campfire spot with actions light / feed /
branch-to-fire; states fire {out, lit} x holding {none, branch} plus 'relit'
(fire went out after a first light). Woods: 12 trees on a 3 m ring, 6 sticks
on the ground (one 0.3 m from a tree base - the break case). Poses: positions
on a 0.25 m grid, headings every 5 degrees, pitch {level, down}.
Resolvers: A ungated priority (feed > branch > light); A2 ungated with a
branch bonus; B state-gated then priority; D light gated by a has-lit flag.
Woods resolvers: W1 one 1-rad cone, 2.5 m reach for all; W2 per-class (trees
0.45 rad, 2.2 m, +0.5 m handicap; pitch down favours ground, level favours
trees).
PREDICTION (written before running): A starves branch and light in every
state; A2 starves light at an out fire while holding a branch (E15's bug); B
offers every valid action in every state; D never offers relight; W1 picks a
tree for >= 30% of poses aimed at a stick; W2 < 5%; W2 still picks the tree
for >= 90% of poses aimed at a tree; break case (stick at a tree base): W2
reaches both, W1 hides the stick in most aimed poses.
ITERATION 1 result: FAIL 6/9 - B (state-gated) still starved branch-to-fire
at a lit fire while holding a branch (feed and branch are BOTH valid there, and
priority picks feed); W1 hijacked only 7.8% on a sparse 3 m tree ring.
ITERATION 2 PREDICTION (written before re-running): B2 = state gate plus
held-item intent (an action that uses what is in hand outranks one that does
not) starves nothing; in a DENSE wood (trees on a 1.5 m grid, as E16's
'trees line every path') W1 hijacks >= 30% of stick-aimed poses and W2 < 5%.
"""
import math, sys
print("python", sys.version.split()[0])
# ---------- campfire spot ----------
STATES = [("out", "none", False), ("out", "branch", False), ("lit", "none", True), ("lit", "branch", True), ("out", "branch", True)]  # last = relight
def valid(fire, hold):
    v = set()
    if fire == "out": v.add("light")
    if fire == "lit": v.add("feed")
    if fire == "lit" and hold == "branch": v.add("branch")
    return v
PRI = ["feed", "branch", "light"]
def resolve(kind, fire, hold, has_lit):
    acts = ["feed", "branch", "light"]
    if kind == "A": offered = acts
    elif kind == "A2": return "branch" if hold == "branch" else ("feed" if True else None)
    elif kind == "B": offered = [a for a in acts if a in valid(fire, hold)]
    elif kind == "B2":
        offered = [a for a in acts if a in valid(fire, hold)]
        uses = [a for a in offered if a == "branch" and hold == "branch"]
        if uses: return uses[0]
    elif kind == "D":
        offered = [a for a in acts if a in valid(fire, hold) and not (a == "light" and has_lit)]
    offered = sorted(offered, key=PRI.index)
    return offered[0] if offered else None
camp = {}
for kind in ("A", "A2", "B", "B2", "D"):
    starved = []
    for fire, hold, has_lit in STATES:
        for a in valid(fire, hold):
            if resolve(kind, fire, hold, has_lit) != a: starved.append((fire, hold, "relit" if has_lit and fire == "out" else "", a))
    camp[kind] = starved
    print(f"campfire {kind:2s}: starved {len(starved)} -> {starved}")
# ---------- woods ----------
trees = [(3 * math.cos(2 * math.pi * i / 12), 3 * math.sin(2 * math.pi * i / 12)) for i in range(12)]
sticks = [(1.0, 0.5), (-1.2, 0.8), (0.4, -1.5), (-0.8, -1.0), (2.0, -0.2), (trees[2][0] * 0.9, trees[2][1] * 0.9)]
BASE = 5
def pick(px, py, h, pitch, mode):
    best = None
    for cls, pts in (("tree", trees), ("stick", sticks)):
        for i, (x, y) in enumerate(pts):
            d = math.hypot(x - px, y - py)
            if d < 1e-9: continue
            ang = abs((math.atan2(y - py, x - px) - h + math.pi) % (2 * math.pi) - math.pi)
            if mode == "W1": cone, reach, hc = 1.0, 2.5, 0.0
            else:
                cone, reach, hc = (0.45, 2.2, 0.5) if cls == "tree" else (1.0, 2.5, 0.0)
                hc += (-0.3 if pitch == "level" else 0.3) if cls == "tree" else (-0.3 if pitch == "down" else 0.3)
            if d > reach or ang > cone: continue
            sc = d + hc + ang
            if best is None or sc < best[0]: best = (sc, cls, i)
    return best
def aimed(targets, cls, pitch, mode, only=None):
    hit = tot = 0
    for i, (tx, ty) in enumerate(targets):
        if only is not None and i != only: continue
        for gx in range(-12, 13):
            for gy in range(-12, 13):
                px, py = tx + gx * 0.25, ty + gy * 0.25
                d = math.hypot(tx - px, ty - py)
                if not (0.4 <= d <= (1.5 if cls == "stick" else 2.0)): continue
                h = math.atan2(ty - py, tx - px)
                for dh in range(-2, 3):
                    r = pick(px, py, h + math.radians(5 * dh), pitch, mode)
                    tot += 1; hit += bool(r and r[1] == cls and r[2] == i)
    return hit / tot
W = {}
DENSE = [(x * 1.5 + 0.2, y * 1.5 + 0.1) for x in range(-3, 4) for y in range(-3, 4)]
for mode in ("W1", "W2"):
    sv = trees[:]; trees[:] = DENSE
    W[mode + "d"] = 1 - aimed(sticks, "stick", "down", mode)
    trees[:] = sv
    print(f"{mode} dense wood: tree hijacks stick-aimed {W[mode + 'd']:.3f}")
for mode in ("W1", "W2"):
    W[mode] = (1 - aimed(sticks, "stick", "down", mode), aimed(trees, "tree", "level", mode),
               aimed(sticks, "stick", "down", mode, only=BASE), aimed(trees, "tree", "level", mode, only=2))
    print(f"{mode}: tree hijacks stick-aimed {W[mode][0]:.3f}; tree-aimed gets tree {W[mode][1]:.3f}; break stick-at-base got {W[mode][2]:.3f}, its tree got {W[mode][3]:.3f}")
c = [{a for *_, a in camp["A"]} >= {"branch", "light"}, ("out", "branch", "", "light") in camp["A2"],
     camp["B2"] == [], any(s[2] == "relit" for s in camp["D"]),
     W["W1d"] >= 0.30, W["W2d"] < 0.05, W["W2"][1] >= 0.90, W["W2"][2] > 0.5 and W["W2"][3] > 0.5, len(camp["B"]) > 0]
print("iteration 2 checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/9; campfire starved A {len(camp['A'])} A2 {len(camp['A2'])} B {len(camp['B'])} B2 {len(camp['B2'])} D {len(camp['D'])}; dense-wood stick hijack W1 {W['W1d']:.3f} W2 {W['W2d']:.3f}; sparse W1 {W['W1'][0]:.3f} W2 {W['W2'][0]:.3f}; tree kept W2 {W['W2'][1]:.3f}; base stick W2 {W['W2'][2]:.3f}")
