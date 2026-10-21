"""Audience-fit of humor style: where 'affiliative is safe, aggressive backfires' breaks.

STRUCTURE ONLY. Every number below is a stated assumption of a toy scoring model,
not a measurement of real people. The four-style frame (affiliative, self-enhancing,
aggressive, self-defeating) is from the Humor Styles Questionnaire literature
(recalled, not read first-hand here).

PREDICTIONS (written before the first run; hand-computed from the equations):
 P1 single joke, tau=0.3, 36 receiver cells: affiliative negative in 0 cells;
    aggressive positive in exactly 19 cells (all 18 shared-target + the in-group,
    other-target, tolerance 0.8, equal-power cell).
 P2 hidden backfire (aggressive true payoff < 0 but observed laughter >= 0.2),
    by sender power gap: +0.5 -> 6 of 6; 0 -> 2 of 5; -0.5 -> 3 of 6.
 P3 repetition: affiliative first negative marginal joke for out-group is index 6
    (0-based); never negative for in-group within 40 jokes.
 P4 aggressive shared-target cells with negative cumulative payoff: 6 of 18 at n=8,
    16 of 18 at n=20.
 P5 third-party weight tau: all 18 shared cells positive at tau=0.3, fewer at 0.4
    (worst cell flips at tau about 0.38).
 P6 move-target (keep mechanism, no victim): mean over shared cells, kept beats moved
    at tau=0 and moved beats kept at tau=0.5; crossover tau about 0.06.
 P7 rank claim: on the full 36-cell mix aggressive mean < affiliative mean at tau=0.3,
    but on the 18 shared-target cells aggressive mean > affiliative mean (narrowly).
"""
import itertools

TOLS = (0.2, 0.5, 0.8)
GROUPS = ("in", "out")
RELS = ("shared", "other")      # target shared with receiver vs receiver/their side/liked party
POWERS = (-0.5, 0.0, 0.5)       # sender power minus receiver power
AMUSE = {"aff": 0.50, "enh": 0.30, "agg": 0.70, "def": 0.45}
EDGE = {"aff": 0.0, "enh": 0.0, "agg": 0.8, "def": 0.0}
CELLS = list(itertools.product(TOLS, GROUPS, RELS, POWERS))

def params(**kw):
    p = dict(decay=0.85, excl=0.12, tau=0.3, bond=1.3, sens=0.3, oblig=0.4)
    p.update(kw)
    return p

def joke(style, cell, k, P, moved=False):
    """Return (rapport, harm, observed_laugh) for the k-th joke (0-based)."""
    tol, grp, rel, pw = cell
    pp = max(pw, 0.0)
    fit = 1.0 if grp == "in" else 0.6
    dec = P["decay"] ** k
    rapport = harm = 0.0
    if style == "aff":
        laugh = AMUSE["aff"] * fit * dec
        rapport = laugh - (P["excl"] if grp == "out" else 0.0)
    elif style == "enh":
        laugh = AMUSE["enh"] * fit * dec
        rapport = laugh
    elif style == "agg" and moved:
        laugh = AMUSE["agg"] * fit * dec   # mechanism kept, no victim, no bond boost
        rapport = laugh
    elif style == "agg":
        if rel == "shared":
            laugh = AMUSE["agg"] * fit * P["bond"] * dec
            recv = EDGE["agg"] * (1 - tol) * 0.25 * (1 + pp)
            third = P["tau"] * EDGE["agg"]
        else:
            laugh = AMUSE["agg"] * fit * 0.3 * dec
            recv = EDGE["agg"] * (1 - tol) * (1 + pp) * (1 + P["sens"] * k) * (1.5 if grp == "out" else 1.0)
            third = 0.0
            if pw < 0:
                harm += 0.6 * (-pw) * EDGE["agg"]   # sender-side retaliation cost
        rapport = laugh
        harm += recv + third
    elif style == "def":
        laugh = AMUSE["def"] * fit * dec
        rapport = laugh
        harm = 0.1 * (1 - tol)
        if pw > 0:
            rapport += 0.15
        else:
            harm += (0.10 + 0.3 * (-pw)) * (1 + 0.25 * k)
    obs = laugh + P["oblig"] * pp
    return rapport, harm, obs

def payoff(style, cell, k, P, **kw):
    r, h, _ = joke(style, cell, k, P, **kw)
    return r - h

def cum(style, cell, n, P, **kw):
    return sum(payoff(style, cell, k, P, **kw) for k in range(n))

def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)

checks = []
def check(name, ok, detail):
    checks.append(ok)
    print(("ok   " if ok else "MISS ") + name + " :: " + detail)

P = params()
shared = [c for c in CELLS if c[2] == "shared"]

# P1
aff_neg = sum(payoff("aff", c, 0, P) < 0 for c in CELLS)
agg_pos_cells = [c for c in CELLS if payoff("agg", c, 0, P) > 0]
extra = [c for c in agg_pos_cells if c[2] != "shared"]
check("P1", aff_neg == 0 and len(agg_pos_cells) == 19 and extra == [(0.8, "in", "other", 0.0)],
      "aff negative=%d, agg positive=%d, non-shared positives=%s" % (aff_neg, len(agg_pos_cells), extra))
print("single-joke style means over 36 cells:",
      {s: round(mean(payoff(s, c, 0, P) for c in CELLS), 3) for s in AMUSE})

# P2
negs = [c for c in CELLS if payoff("agg", c, 0, P) < 0]
got = {}
for pw in POWERS:
    sub = [c for c in negs if c[3] == pw]
    hid = [c for c in sub if joke("agg", c, 0, P)[2] >= 0.2]
    got[pw] = (len(hid), len(sub))
check("P2", got == {0.5: (6, 6), 0.0: (2, 5), -0.5: (3, 6)}, "hidden/negative by power gap: %s" % got)

# P3
def first_neg(style, cell, Pm, cap=40):
    for k in range(cap):
        if payoff(style, cell, k, Pm) < 0:
            return k
    return None
fo = {c: first_neg("aff", c, P) for c in CELLS if c[1] == "out"}
fi = {c: first_neg("aff", c, P) for c in CELLS if c[1] == "in"}
check("P3", set(fo.values()) == {6} and set(fi.values()) == {None},
      "aff first-negative out-group=%s in-group=%s" % (sorted(set(fo.values()), key=str), sorted(set(fi.values()), key=str)))
print("sensitivity: aff out-group first-negative index by (decay, excl):")
for d in (0.75, 0.85, 0.95):
    print("  decay %.2f:" % d, {e: first_neg("aff", (0.5, "out", "other", 0.0), params(decay=d, excl=e)) for e in (0.06, 0.12, 0.2)})

# P4
n8 = sum(cum("agg", c, 8, P) < 0 for c in shared)
n20 = sum(cum("agg", c, 20, P) < 0 for c in shared)
check("P4", (n8, n20) == (6, 16), "shared-target aggressive cumulative negative: n=8 -> %d/18, n=20 -> %d/18" % (n8, n20))
print("aff cumulative negative cells (36): n=8 -> %d, n=20 -> %d, n=40 -> %d" % tuple(
    sum(cum("aff", c, n, P) < 0 for c in CELLS) for n in (8, 20, 40)))

# P5
cnt = {t: sum(payoff("agg", c, 0, params(tau=t)) > 0 for c in shared) for t in (0.0, 0.3, 0.4, 0.5)}
check("P5", cnt[0.3] == 18 and cnt[0.4] < 18, "positive shared cells by tau: %s" % cnt)

# P6
def sh_mean(tau, moved):
    return mean(payoff("agg", c, 0, params(tau=tau), moved=moved) for c in shared)
k0, m0, k5, m5 = sh_mean(0, False), sh_mean(0, True), sh_mean(0.5, False), sh_mean(0.5, True)
cross = None
for i in range(0, 1001):
    t = i / 1000
    if sh_mean(t, False) < sh_mean(t, True):
        cross = t
        break
check("P6", k0 > m0 and m5 > k5 and cross is not None and 0.04 <= cross <= 0.09,
      "tau=0 kept %.3f moved %.3f; tau=0.5 kept %.3f moved %.3f; crossover tau=%s" % (k0, m0, k5, m5, cross))

# P7
a36 = mean(payoff("aff", c, 0, P) for c in CELLS)
g36 = mean(payoff("agg", c, 0, P) for c in CELLS)
a18 = mean(payoff("aff", c, 0, P) for c in shared)
g18 = mean(payoff("agg", c, 0, P) for c in shared)
check("P7", g36 < a36 and g18 > a18, "36-cell agg %.3f vs aff %.3f; shared-18 agg %.3f vs aff %.3f" % (g36, a36, g18, a18))

# extra tables (not predictions)
print("self-defeating single-joke payoff by power gap (mean over tol/group/rel):",
      {pw: round(mean(payoff("def", c, 0, P) for c in CELLS if c[3] == pw), 3) for pw in POWERS})
print("def cumulative n=8 negative cells by power gap:",
      {pw: sum(cum("def", c, 8, P) < 0 for c in CELLS if c[3] == pw) for pw in POWERS})

if all(checks):
    print("RESULT: PASS %d/%d predictions held; claim breaks at shared-target in-group audience, hidden under power gap, and by repetition for both styles (toy model, structure only)" % (sum(checks), len(checks)))
else:
    print("RESULT: FAIL %d/%d predictions held; see MISS lines" % (sum(checks), len(checks)))
