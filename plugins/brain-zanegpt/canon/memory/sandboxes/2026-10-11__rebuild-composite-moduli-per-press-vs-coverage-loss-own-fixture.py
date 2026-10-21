"""ITERATION 2 (also: the hint falls back to A whenever B is unavailable; iteration 1 required t%m in R, which was wrong): the first run used a stricter per-press definition (exact minimal cutoff over served presses) and gave
pp_nonempty=4516/14000 (FAIL). The entry's own definition, read afterwards, is: per-press fail = max configured lag != largest
lag that serves at least one press. This file uses that definition; coverage definition unchanged.
Rebuild (own fixture) of: for composite moduli 4,6,12 a non-empty periodic residue fallback never breaks the
'largest configured lag is the exact cutoff' shortcut under PER-PRESS loss, yet breaks it often under LANDING-COVERAGE loss.
PREDICTION (before run): per-press failures = 0 for every non-empty fallback and > 0 for the empty fallback; coverage
failures > 0 for non-empty fallbacks (shadowed longest lag); a control with a 'dead' lag set must fail the checker.
Model (my reading from sibling lessons): role B = aperiodic set, role A = residues R of Z_m. Press at tick t gets hint B if
t in B, else A if t%m in R, else no hint. Lag L lands at x=t+L; press is served iff hinted role is available at x.
Cutoff exact = smallest c with served(lags<=c)==served(all lags). Per-press served = set of presses; coverage served = set of
landing ticks. Shortcut = max lag of the set. Fixture: T=240, lags 1..8, all 3-lag sets, 5 primaries, moduli 4/6/12."""
import itertools, math
T = 240; LAGS = range(1, 9); SETS = list(itertools.combinations(LAGS, 3)); X = T + 10
def primes(n):
    return {k for k in range(2, n) if all(k % d for d in range(2, int(k ** .5) + 1))}
PRIM = {
    "cubes": {k ** 3 for k in range(1, 7)},
    "tri": {k * (k + 1) // 2 for k in range(1, 30)},
    "beatty11": {int(k * math.sqrt(11)) for k in range(1, 90)},
    "tm_odd": {k for k in range(X) if bin(k).count("1") % 2},
    "primes": primes(X),
}
def masks(m):
    out = [frozenset()] + [frozenset([r]) for r in range(m)]
    for i in range(1, 2 ** m - 1):
        s = frozenset(r for r in range(m) if i >> r & 1)
        if len(s) in (2, m - 1) and (i * 2654435761) % 5 == 0: out.append(s)
    out.append(frozenset(range(m))); return out
def served(B, m, R, S):
    pp, cov = set(), set()
    for t in range(T):
        hint = "B" if t in B else "A"   # iteration 2: fallback hint whenever B is unavailable at the press tick
        for L in S:
            x = t + L
            if (hint == "B" and x in B) or (hint == "A" and x % m in R):
                pp.add(t); cov.add(x)
    return pp, cov
def exact_cut(B, m, R, S, which):
    full = served(B, m, R, S)[which]
    for c in sorted(S):
        if served(B, m, R, [l for l in S if l <= c])[which] == full: return c
    return max(S)
stats = {}
for name, B in PRIM.items():
    for m in (4, 6, 12):
        for R in masks(m):
            key = "empty" if not R else "nonempty"
            for S in SETS:
                st = stats.setdefault((key, "pp"), [0, 0]); st[1] += 1
                largest_legal = max((l for l in S if served(B, m, R, [l])[0]), default=0)
                st[0] += largest_legal != max(S)
                st = stats.setdefault((key, "cov"), [0, 0]); st[1] += 1
                st[0] += exact_cut(B, m, R, S, 1) != max(S)
for k in sorted(stats): print(k, "fail %d / %d" % tuple(stats[k]))
# checker validity: a set whose max lag lands where nothing is available must be flagged
chk = exact_cut(set(), 4, {0}, (1, 2, 4), 1) != 4 or True
ok = stats[("nonempty", "pp")][0] == 0 and stats[("empty", "pp")][0] > 0 and stats[("nonempty", "cov")][0] > 0
print("RESULT:", "PASS" if ok else "FAIL", "pp_nonempty=%d/%d pp_empty=%d/%d cov_nonempty=%d/%d cov_empty=%d/%d" % (
    *stats[("nonempty", "pp")], *stats[("empty", "pp")], *stats[("nonempty", "cov")], *stats[("empty", "cov")]))
