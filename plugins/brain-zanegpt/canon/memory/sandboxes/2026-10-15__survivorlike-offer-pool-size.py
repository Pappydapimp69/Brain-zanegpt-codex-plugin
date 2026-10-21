# Survivor-like level-up: offer 3 distinct upgrades uniformly from a pool of n, L level-ups per run.
# Exact fractions, no RNG. Checks the closed form against a brute-force enumeration on a tiny pool.
# PREDICTION (before first run): one target upgrade, L=20: n=30 -> P(seen) ~0.88, n=60 -> ~0.64;
# a 2-piece synergy (needs both seen) at n=30 drops to ~0.75; maxed items leaving the pool push
# the late-run odds up by more than 0.05 at n=30.
from fractions import Fraction as F
from itertools import combinations
def C(n, k):
    from math import comb; return comb(n, k)
def miss1(n, k=3): return F(C(n-1, k), C(n, k))                       # target absent from one offer
def p_one(n, L, k=3): return 1 - miss1(n, k) ** L
def p_both(n, L, k=3):                                                  # inclusion-exclusion over the two pieces
    m1 = miss1(n, k); m2 = F(C(n-2, k), C(n, k)); return 1 - 2 * m1 ** L + m2 ** L
def brute_one(n, L, k=3):                                               # enumerate every offer sequence
    offers = list(combinations(range(n), k)); hit = 0; tot = 0
    def rec(d, seen):
        nonlocal hit, tot
        if d == L: tot += 1; hit += seen; return
        for o in offers: rec(d + 1, seen or (0 in o))
    rec(0, False); return F(hit, tot)
bf = brute_one(6, 3); cf = p_one(6, 3)
print('S0 brute force n=6 L=3: %s closed form %s match=%s' % (bf, cf, bf == cf))
L = 20
for n in (15, 30, 45, 60, 90): print('S1 n=%2d  P(one target seen in %d) %.3f   P(2-piece synergy) %.3f' % (n, L, float(p_one(n, L)), float(p_both(n, L))))
# largest pool that keeps a single target >= 90% findable in L level-ups
nmax = max(n for n in range(4, 400) if p_one(n, L) >= F(9, 10))
print('S2 largest pool with P>=0.9 at L=20: n=%d (rule n <= 3L/ln10 = %.1f)' % (nmax, 3 * L / 2.302585))
# S3: shrinking pool - each level-up after the 6th one item maxes out and leaves (n drops by 1)
def p_shrink(n, L, k=3, start=6):
    miss = F(1)
    for i in range(L): nn = n - max(0, i - start); miss *= miss1(nn, k)
    return 1 - miss
ps = p_shrink(30, L); print('S3 n=30 with maxed items leaving: %.3f (vs %.3f fixed)' % (float(ps), float(p_one(30, L))))
# S4 (built to BREAK the pool rule): weighted offers where the target is 'rare' at weight 1/4 of others
def p_weighted(n, L, w):   # sequential draw of 3 without replacement, weight w for target, 1 for others
    tot = (n - 1) + w; pm = F(1); rest = n - 1
    for j in range(3): pm *= F(rest - j, 1) / (rest - j + w)
    return 1 - pm ** L
pw = p_weighted(30, L, F(1, 4)); print('S4 n=30 target weight 1/4: %.3f' % float(pw))
ok = bf == cf and abs(float(p_one(30, L)) - .878) < .01 and abs(float(p_one(60, L)) - .642) < .01 and float(pw) < .5
print('RESULT: %s P(seen) n=30 %.3f n=60 %.3f, 2-piece n=30 %.3f, pool cap for 90%% at L=20 is n=%d, maxed-out removal +%.3f, rarity 1/4 -> %.3f'
      % ('PASS' if ok else 'FAIL', float(p_one(30, L)), float(p_one(60, L)), float(p_both(30, L)), nmax, float(ps - p_one(30, L)), float(pw)))
