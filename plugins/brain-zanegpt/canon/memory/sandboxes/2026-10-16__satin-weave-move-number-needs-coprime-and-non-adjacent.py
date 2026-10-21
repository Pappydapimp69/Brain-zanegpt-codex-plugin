"""Sandbox: WEAVING - which repeat sizes n have a regular satin (one raised warp per pick, move number s)?
Real-source rule being tested (standard hand-weaving drafting practice, e.g. Black/Davison): a regular satin on n shafts uses a move number s
that is coprime to n and not 1 or n-1 (else it is a twill or repeats early); there is no regular satin on 6 shafts (nor 2, 3, 4).
Check is a brute-force drawdown, NOT the gcd rule: build the n x n tile with a raised cell at (r, (r*s) mod n), then test on the TORUS
(tile repeated) that every row and column has exactly one raised cell, that the repeat does not shrink (all n columns used), and that no two
raised cells touch, including diagonally and across tile edges.
PREDICTION (before run): satin exists for n in {5,7,8,9,10,11,12} and not for n in {2,3,4,6}; the count of valid s for n=5,7,8,10,12 is 2,4,4,4,4 (FIRST RUN REFUTED THIS: I forgot the coprime cut; counts are phi(n)-2 = 2,4,2,2,2, which is the corrected expectation);
the brute force and the gcd+range rule agree for every n in 2..24 and every s in 1..n-1."""
from math import gcd

def drawdown_ok(n, s):
    cells = {(r, (r * s) % n) for r in range(n)}
    if len({c for _, c in cells}) != n: return False       # a column reused: the repeat is smaller than n
    for (r, c) in cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (dr or dc) and ((r + dr) % n, (c + dc) % n) in cells: return False
    return True

def rule(n, s): return gcd(s, n) == 1 and s not in (1, n - 1)

valid = {n: [s for s in range(1, n) if drawdown_ok(n, s)] for n in range(2, 25)}
agree = all(drawdown_ok(n, s) == rule(n, s) for n in range(2, 25) for s in range(1, n))
exists = {n for n, v in valid.items() if v}
no_sat = [n for n in range(2, 25) if n not in exists]
counts = {n: len(valid[n]) for n in (5, 7, 8, 10, 12)}
print("no satin for", no_sat, "counts", counts, "agree", agree)
ok = agree and no_sat == [2, 3, 4, 6] and counts == {5: 2, 7: 4, 8: 2, 10: 2, 12: 2}
print("RESULT: %s no satin for n=%s; valid move numbers n=5:%s n=8:%s n=12:%s; brute force == coprime rule on %d (n,s) pairs: %s" % (
    "PASS" if ok else "FAIL", no_sat, valid[5], valid[8], valid[12], sum(n - 1 for n in range(2, 25)), agree))
