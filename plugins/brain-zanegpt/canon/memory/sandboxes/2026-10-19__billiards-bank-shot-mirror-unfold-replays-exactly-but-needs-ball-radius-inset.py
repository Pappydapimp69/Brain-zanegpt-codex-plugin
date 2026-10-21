"""Sandbox: bank shots on a rectangular table by mirror-unfolding the target.
Exact rational arithmetic; the unfolded aim line is replayed by a step-by-step
reflection simulator and compared with the plan. No RNG."""
from fractions import Fraction as F
import itertools, math

W, H = F(100), F(50)
WALLS = {"L": ("x", F(0)), "R": ("x", W), "B": ("y", F(0)), "T": ("y", H)}

def refl(pt, wall):
    ax, c = WALLS[wall]
    return (2 * c - pt[0], pt[1]) if ax == "x" else (pt[0], 2 * c - pt[1])

def unfold(target, seq):
    t = target
    for w in reversed(seq):          # reflect across the LAST cushion first
        t = refl(t, w)
    return t

def replay(cue, aim, target, max_hits=4, k=F(1), w=W, h=H, x0=F(0), y0=F(0)):
    """Replay a ball from cue toward aim in the box [x0,w]x[y0,h]; returns (cushions hit before
    passing target, closest approach to target). k = tangential speed retained per bounce."""
    px, py = cue; dx, dy = aim[0] - cue[0], aim[1] - cue[1]
    hits = []; best = None
    for _ in range(max_hits + 1):
        ts = []
        if dx > 0: ts.append(((w - px) / dx, "R"))
        if dx < 0: ts.append(((x0 - px) / dx, "L"))
        if dy > 0: ts.append(((h - py) / dy, "T"))
        if dy < 0: ts.append(((y0 - py) / dy, "B"))
        t, wall = min(ts)
        # closest approach on this leg
        L2 = dx * dx + dy * dy
        s = max(F(0), min(t, ((target[0] - px) * dx + (target[1] - py) * dy) / L2))
        qx, qy = px + s * dx, py + s * dy
        d2 = (qx - target[0]) ** 2 + (qy - target[1]) ** 2
        if best is None or d2 < best[0]: best = (d2, list(hits))
        px, py = px + t * dx, py + t * dy
        if wall in "LR": dx = -dx; dy = dy * k
        else: dy = -dy; dx = dx * k
        hits.append(wall)
    return best[1], math.sqrt(best[0])

grid = [F(v) for v in range(10, 100, 20)]
pts = [(x, y) for x in grid for y in (F(10), F(25), F(40)) if y < H]
def plan_cases(seqs):
    for cue, tgt in itertools.permutations(pts, 2):
        for seq in seqs:
            yield cue, tgt, seq

one = [(w,) for w in "LRBT"]
two = [s for s in itertools.product("LRBT", repeat=2) if s[0] != s[1]]
res = {}
for name, seqs in (("one", one), ("two", two)):
    n = ok_geom = replay_ok = 0
    for cue, tgt, seq in plan_cases(seqs):
        n += 1
        aim = unfold(tgt, seq)
        hits, miss = replay(cue, aim, tgt)
        # valid plan iff the replay passes through the target after exactly the planned cushions
        if miss == 0:
            ok_geom += 1
            if hits == list(seq): replay_ok += 1
    res[name] = (n, ok_geom, replay_ok)
    print(name, "cushion plans:", n, "| aim line reaches target:", ok_geom, "| ...with the planned cushion order:", replay_ok)

# BREAK 1: ball centre is confined to the table inset by the ball radius r. Aiming with nominal unfolding
# (full table) but playing in the inset box misses.
r = F(5, 2)
miss1 = []
for cue, tgt, seq in plan_cases(one):
    aim = unfold(tgt, seq)
    hits, m = replay(cue, aim, tgt, w=W - r, h=H - r, x0=r, y0=r)
    miss1.append(float(m))
print("BREAK radius: nominal-table aim, inset-box play: mean miss %.2f, max miss %.2f (r=%.1f)" % (sum(miss1) / len(miss1), max(miss1), float(r)))
# FIX: unfold on the inset box
def unfold_inset(target, seq):
    t = target
    for w in reversed(seq):
        ax, c = WALLS[w]
        c = c + (r if c == 0 else -r)
        t = (2 * c - t[0], t[1]) if ax == "x" else (t[0], 2 * c - t[1])
    return t
fixed = max(float(replay(cue, unfold_inset(tgt, seq), tgt, w=W - r, h=H - r, x0=r, y0=r)[1]) for cue, tgt, seq in plan_cases(one) if r <= cue[0] and r <= cue[1])
print("inset-box unfolding max miss (exact arithmetic): %.6f" % fixed)
# BREAK 2: cushion keeps only k of the tangential speed
for k in (F(1), F(99, 100), F(95, 100), F(90, 100)):
    ms = [float(replay(cue, unfold(tgt, seq), tgt, k=k)[1]) for cue, tgt, seq in plan_cases(one)]
    print("tangential retention k=%.2f: max miss %.2f, cases missing by more than the ball radius: %d of %d" % (float(k), max(ms), sum(m > float(r) for m in ms), len(ms)))
# float replay: strict equality vs tolerance (exact arithmetic reached 0 miss in every plan above)
strict = tol = nfl = 0
for cue, tgt, seq in plan_cases(two):
    c, t2, a2 = [tuple(float(v) for v in q) for q in (cue, tgt, unfold(tgt, seq))]
    _, m = replay(c, a2, t2)
    nfl += 1; strict += (m == 0); tol += (m < 1e-9)
print("float replay of two-cushion plans: strict miss==0 in %d of %d, tolerance 1e-9 in %d" % (strict, nfl, tol))
full = res["one"][1] == res["one"][0] and res["two"][1] == res["two"][0]
order_gap = res["one"][2] < res["one"][0] and res["two"][2] < res["two"][1]
ok = full and order_gap and max(miss1) > 0 and fixed == 0
print("RESULT: %s unfolded aim reached the target in %d/%d one-cushion and %d/%d two-cushion plans, but with the PLANNED cushion order in only %d and %d; nominal-table aim missed by up to %.2f with r=2.5 while inset unfolding missed by %.1f; float replay needed a tolerance (strict equality %d/%d vs 1e-9 tolerance %d/%d)"
      % ("PASS" if ok else "FAIL", res["one"][1], res["one"][0], res["two"][1], res["two"][0], res["one"][2], res["two"][2], max(miss1), fixed, strict, nfl, tol, nfl))
