# Counterfeit-coin puzzle by exhaustive adaptive search: one coin of N is odd (heavier or lighter, unknown); a
# balance gives left/right/equal; find the odd coin AND whether it is heavy or light within k weighings.
# State = (u, a, b, g): u untested coins (heavy or light), a that could be heavy, b that could be light, g known genuine
# (usable as padding).
# Any coin leaving the suspect sets becomes genuine. Known results: N_max = (3^k - 3)/2 with no spare genuine coin
# (3, 12, 39 for k 2, 3, 4) and (3^k - 1)/2 with one (4, 13, 40).
# PREDICTION (before run): the search finds N_max = 3 and 12 for k = 2 and 3 with no spare coin, 4 and 13 with a spare
# genuine coin, N = 13 with no spare fails at k = 3, and the first weighing of the 12-coin solution is 4 against 4.
from functools import lru_cache
@lru_cache(maxsize=None)
def solve(u, a, b, g, k, total):
    if u == 0 and a + b <= 1: return True
    if k == 0: return False
    if 2 * u + a + b > 3 ** k: return False            # information bound on outcome classes
    for u1 in range(u + 1):
      for u2 in range(u - u1 + 1):
        for a1 in range(a + 1):
          for a2 in range(a - a1 + 1):
            for b1 in range(b + 1):
              for b2 in range(b - b1 + 1):
                l, r = u1 + a1 + b1, u2 + a2 + b2
                if l + r == 0 or abs(l - r) > g: continue
                outs = ((0, u1 + a1, u2 + b2), (0, u2 + a2, u1 + b1), (u - u1 - u2, a - a1 - a2, b - b1 - b2))
                if all(solve(uu, aa, bb, total - uu - aa - bb, k - 1, total) for uu, aa, bb in outs): return True
    return False
def first(n, spare, k):
    for u1 in range(1, n + 1):
        for u2 in range(0, n - u1 + 1):
            if abs(u1 - u2) > spare: continue
            outs = ((0, u1, u2), (0, u2, u1), (n - u1 - u2, 0, 0))
            if all(solve(uu, aa, bb, n + spare - uu - aa - bb, k - 1, n + spare) for uu, aa, bb in outs) and u1 >= u2: return (u1, u2)
    return None
def solved(n, spare, k): return first(n, spare, k) is not None
res = {}
for k in (2, 3):
    for spare in (0, 1):
        m = max(n for n in range(2, 16) if solved(n, spare, k)) if any(solved(n, spare, k) for n in range(2, 16)) else 0
        res[(k, spare)] = m
        print(f"k={k} spare genuine={spare}: largest N solved = {m}; first weighing: {first(m, spare, k)}")
no13 = not solved(13, 0, 3)
ok = (res[(2, 0)] == 3 and res[(3, 0)] == 12 and res[(2, 1)] == 4 and res[(3, 1)] == 13 and no13 and first(12, 0, 3) == (4, 4))
print(f"RESULT: {'PASS' if ok else 'FAIL'} largest N by (weighings, spare genuine): {res}; 13 coins without a spare in 3 weighings unsolved {no13}; 12-coin first weighing {first(12, 0, 3)}")
