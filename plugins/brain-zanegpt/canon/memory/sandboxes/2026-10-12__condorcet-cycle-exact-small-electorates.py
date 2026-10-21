"""Exact Condorcet-cycle / no-Condorcet-winner probability, 3 candidates,
impartial culture (each voter picks one of 6 strict orders uniformly).
Exact DP over pairwise margin vectors (m_ab, m_bc, m_ac); integer counts / 6^n.
Claim: for ODD n the exact cycle probability is 1/18 at n=3, rises strictly
monotonically with n, and stays below Guilbaud's limit 8.77% (Wikipedia: n=101 -> 8.690%).
BREAK scenario: EVEN n, where pairwise ties make 'no strict Condorcet winner'
far more common than 8.77%."""
import math
from fractions import Fraction
from itertools import permutations

GUILBAUD = 0.25 - 3 / (2 * math.pi) * math.asin(1 / 3)   # = 3acos(1/3)/(2pi) - 1/2
ORDERS = list(permutations("abc"))
def vec(o):
    r = {c: i for i, c in enumerate(o)}
    s = lambda x, y: 1 if r[x] < r[y] else -1
    return (s("a", "b"), s("b", "c"), s("a", "c"))
VECS = [vec(o) for o in ORDERS]

NMAX = 61   # NMAX=101 reproduced Wikipedia's 8.690% exactly but took ~45 s; 61 keeps runtime < 30 s
TABLE = {}   # n -> margin distribution; one cumulative DP pass up to NMAX
B = 2 * NMAX + 3            # pack (x, y, z) margins into one int key: faster dict ops
OFF = NMAX + 1
STEPS = [dx * B * B + dy * B + dz for dx, dy, dz in VECS]
def _build():
    d = {OFF * B * B + OFF * B + OFF: 1}
    for n in range(1, NMAX + 1):
        nd = {}
        get = nd.get
        for k, w in d.items():
            for s in STEPS:
                j = k + s
                nd[j] = get(j, 0) + w
        d = nd
        if n % 2 or n <= 30:
            TABLE[n] = _eval(n, {(k // (B * B) - OFF, k // B % B - OFF, k % B - OFF): w
                                 for k, w in d.items()})

def probs(n):
    return TABLE[n]

def _eval(n, d):
    tot = 6 ** n; cyc = nocw = 0
    for (ab, bc, ac), w in d.items():
        # a beats b iff ab>0 ; b beats c iff bc>0 ; a beats c iff ac>0
        a = ab > 0 and ac > 0; b = ab < 0 and bc > 0; c = ac < 0 and bc < 0
        if not (a or b or c): nocw += w
        if (ab > 0 and bc > 0 and ac < 0) or (ab < 0 and bc < 0 and ac > 0): cyc += w
    return Fraction(cyc, tot), Fraction(nocw, tot)

_build()
ok = True
print(f"Guilbaud limit = {GUILBAUD:.5f}")
# Scenario 1: n=3 exact value
c3, _ = probs(3); print("S1 n=3 cycle =", c3, f"{float(c3):.5f}")
ok &= (c3 == Fraction(1, 18))
# Scenario 2: odd n 3..51, monotone and below limit
prev = 0; odd = {}
for n in range(1, NMAX + 1, 2):
    c, nc = probs(n); odd[n] = float(c)
    assert c == nc, "odd n: no ties, so no-CW == cycle"
    ok &= float(c) < GUILBAUD and (n == 1 or float(c) > prev); prev = float(c)
print("S2 odd n:", {n: round(v, 5) for n, v in odd.items() if n in (3,5,7,9,11,15,21,31,41,51,61)})
# Scenario 3: largest n stays below Wikipedia's n=101 value 8.690% (monotone toward the limit)
c61, _ = probs(NMAX); print(f"S3 n={NMAX} cycle = {float(c61):.5f} (< 0.08690 at n=101)")
ok &= float(c61) < 0.08690
# Scenario 4 (BREAK): even n, 'no strict Condorcet winner'
ev = {}
for n in range(2, 31, 2):
    c, nc = probs(n); ev[n] = (round(float(c), 5), round(float(nc), 5))
print("S4 even n (cycle, noCW):", ev)
even_all_above = all(v[1] > GUILBAUD for v in ev.values())
print("S4 every even n<=30 has noCW > 8.77%:", even_all_above)
ok &= even_all_above   # claim's scope boundary: limit is NOT a bound for even n
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" odd-n IC cycle prob exact: n=3 1/18=5.556%, n=51 {odd[51]*100:.3f}%, n={NMAX} {float(c61)*100:.3f}%, strictly rising and below Guilbaud {GUILBAUD*100:.3f}%; even n<=30 noCW {min(v[1] for v in ev.values())*100:.1f}-{max(v[1] for v in ev.values())*100:.1f}% (bound fails)")
