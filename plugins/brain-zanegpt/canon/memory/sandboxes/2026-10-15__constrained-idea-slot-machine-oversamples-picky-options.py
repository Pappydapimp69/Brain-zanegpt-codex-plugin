"""Ideation: a morphological box (Zwicky) / prompt slot machine. Pick one option per
column (genre, setting, protagonist, twist); a list of 'does not go together' pairs prunes
combinations. The usual implementation picks columns in order, each uniformly among options
still compatible with what is already picked (restarting on a dead end). The alternative is
to draw a full combination uniformly and reject invalid ones.
Question: does the sequential picker serve every VALID idea equally often?
All probabilities are computed exactly with Fractions by enumeration; no RNG.

PREDICTION (written before first run): with an irregular ban list (some options banned with
many partners, some with none), the sequential picker's most likely valid combo is >= 3x as
likely as its least likely, total variation distance from uniform >= 0.15, and the
over-served combos are the ones that run through heavily banned ('picky') options.
Controls: no bans -> exactly uniform (ratio 1); a REGULAR ban list where every option has the
same number of banned partners in each next column -> also exactly uniform (built to break
the claim that 'any constraint' skews the picker)."""
from fractions import Fraction as F
from itertools import product
COLS = [("genre", ["noir", "romcom", "western", "space opera"]),
        ("setting", ["submarine", "high school", "monastery", "casino"]),
        ("protagonist", ["ghost", "accountant", "child", "robot"]),
        ("twist", ["time loop", "twins", "it was a dream", "unreliable narrator"])]
OPTS = [o for _, o in COLS]
def compatible(choice, bans):
    for (i, a), (j, b) in bans:
        if len(choice) > max(i, j) and choice[i] == a and choice[j] == b: return False
    return True
def valid_set(bans): return [c for c in product(*OPTS) if compatible(c, bans)]
def sequential_dist(bans):
    """exact distribution of pick-in-order-with-restart-on-dead-end over full combos"""
    raw = {}
    def walk(prefix, p):
        k = len(prefix)
        if k == len(OPTS): raw[tuple(prefix)] = raw.get(tuple(prefix), 0) + p; return
        ok = [o for o in OPTS[k] if compatible(tuple(prefix) + (o,), bans)]
        if not ok: return                       # dead end: mass lost, picker restarts
        for o in ok: walk(prefix + [o], p / len(ok))
    walk([], F(1))
    tot = sum(raw.values())
    return {c: p / tot for c, p in raw.items()}  # restart = renormalise over completed walks
def report(name, bans):
    V = valid_set(bans); u = F(1, len(V)); d = sequential_dist(bans)
    assert set(d) == set(V)
    ps = sorted(d.values())
    ratio = ps[-1] / ps[0]; tv = sum(abs(d[c] - u) for c in V) / 2
    # picky options: banned with >= 3 partners
    deg = {}
    for (i, a), (j, b) in bans:
        deg[(i, a)] = deg.get((i, a), 0) + 1; deg[(j, b)] = deg.get((j, b), 0) + 1
    picky = {k for k, v in deg.items() if v >= 3}
    through = [c for c in V if any((i, c[i]) in picky for i in range(4))]
    share_seq = sum(d[c] for c in through); share_uni = F(len(through), len(V))
    top = max(V, key=lambda c: d[c]); bot = min(V, key=lambda c: d[c])
    print(f"{name:22s} valid {len(V):3d}/256  max/min {float(ratio):5.2f}  TV {float(tv):.3f}  "
          f"picky-path share seq {float(share_seq):.3f} vs uniform {float(share_uni):.3f}")
    if ratio > 1: print(f"    most likely  {top} p={float(d[top]):.4f} ({float(d[top]/u):.2f}x uniform)\n"
                        f"    least likely {bot} p={float(d[bot]):.4f} ({float(d[bot]/u):.2f}x uniform)")
    return ratio, tv, share_seq, share_uni
G, S, P, T = 0, 1, 2, 3
IRREG = [((G, "romcom"), (S, "submarine")), ((G, "romcom"), (S, "monastery")), ((G, "romcom"), (S, "casino")),
         ((S, "monastery"), (P, "robot")), ((S, "monastery"), (P, "accountant")), ((S, "monastery"), (P, "ghost")),
         ((G, "western"), (P, "robot")),
         ((P, "child"), (T, "time loop")), ((P, "child"), (T, "twins")), ((P, "child"), (T, "unreliable narrator"))]
REG = []   # every option bans exactly one partner in the next column (a cyclic Latin pattern)
for c in range(3):
    for k, a in enumerate(OPTS[c]): REG.append(((c, a), (c + 1, OPTS[c + 1][k])))
r0 = report("no bans (control)", [])
r1 = report("irregular bans", IRREG)
r2 = report("regular bans (break)", REG)
ok = r0[0] == 1 and r2[0] == 1 and r1[0] >= 3 and r1[1] >= F(15, 100) and r1[2] > r1[3]
print(f"RESULT: {'PASS' if ok else 'FAIL'} sequential picker: no bans ratio {float(r0[0]):.2f}; irregular bans max/min "
      f"{float(r1[0]):.2f}, TV {float(r1[1]):.3f}, picky-path share {float(r1[2]):.3f} vs uniform {float(r1[3]):.3f}; "
      f"regular bans ratio {float(r2[0]):.2f} TV {float(r2[1]):.3f}")
