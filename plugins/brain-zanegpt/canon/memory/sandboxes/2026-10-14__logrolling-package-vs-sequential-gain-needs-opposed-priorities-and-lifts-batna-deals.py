"""Package (logrolling) vs issue-by-issue negotiation, 3 issues, levels 0..10.
Prediction (written before first run): opposed priorities -> package joint value
>= 1.3x sequential split-the-difference; identical priorities -> gain exactly 0;
with reservation values (BATNA) set between the two joint totals, sequential
yields no deal but package does."""
import itertools

L = range(11)

def util(wx, wy, lv):
    return (sum(w * l for w, l in zip(wx, lv)), sum(w * (10 - l) for w, l in zip(wy, lv)))

def sequential(wx, wy):          # each issue settled alone at the midpoint
    return util(wx, wy, (5, 5, 5))

def package(wx, wy, rx=0, ry=0):  # best Nash product over all 11^3 packages meeting both reservations
    best, arg = None, None
    for lv in itertools.product(L, repeat=3):
        ux, uy = util(wx, wy, lv)
        if ux < rx or uy < ry:
            continue
        key = (ux * uy, -sum(lv))
        if best is None or key > best:
            best, arg = key, lv
    return None if arg is None else util(wx, wy, arg)

def run(name, wx, wy, rx=0, ry=0):
    s = sequential(wx, wy)
    s_ok = s[0] >= rx and s[1] >= ry
    p = package(wx, wy, rx, ry)
    sj = sum(s) if s_ok else None
    pj = sum(p) if p else None
    print(f"{name}: seq={s} deal={s_ok} pkg={p} jointseq={sj} jointpkg={pj}")
    return s, s_ok, p

ok = True
s, so, p = run("opposed", (5, 3, 1), (1, 3, 5))
ok &= sum(p) >= 1.3 * sum(s)
s, so, p = run("identical(BREAK)", (5, 3, 1), (5, 3, 1))
ok &= sum(p) == sum(s)
s, so, p = run("partial", (5, 3, 1), (3, 3, 3))
partial_gain = sum(p) / sum(s)
print("partial gain ratio", round(partial_gain, 3))
ok &= 1.0 <= partial_gain < 1.3
# BATNA scenario: reservations above the sequential outcome, within reach of a package
s, so, p = run("high-BATNA", (5, 3, 1), (1, 3, 5), rx=55, ry=55)
ok &= (not so) and p is not None
# BATNA beyond any package: no deal for either method (alternative sets deal existence)
s, so, p = run("BATNA-too-high", (5, 3, 1), (1, 3, 5), rx=70, ry=70)
ok &= (not so) and p is None
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "package gain depends on opposed priorities; BATNA decides deal existence")
