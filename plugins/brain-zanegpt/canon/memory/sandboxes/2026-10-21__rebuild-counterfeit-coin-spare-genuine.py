# Own fixture: class-count dynamic programming over (unknown, maybe-heavy, maybe-light, known-genuine) pools,
# NOT a per-coin hypothesis-set search. Solved = coin AND direction known (<=1 hypothesis), plus a break variant
# where only the coin must be identified.
# Prediction (before run): max N (k=2,3,4) with no spare 3,12,39; with one spare 4,13,40; 13 coins k=3 no spare unsolvable
# (direction required) but SOLVABLE if only the coin must be identified; 12-coin first weighing 4 vs 4.
from functools import lru_cache
import sys; sys.setrecursionlimit(10000)
CAP = 14
def hyps(u, h, l): return 2*u + h + l
def make(need_dir):
    @lru_cache(maxsize=None)
    def ok(k, u, h, l, g):
        n = u + h + l
        if need_dir:
            if hyps(u, h, l) <= 1: return True
        else:
            if n <= 1: return True
        if k == 0: return False
        # information bound: 3 outcomes per weighing
        if hyps(u, h, l) > 3 ** k and need_dir: return False
        for u1 in range(u+1):
         for u2 in range(u1, u+1-0):
          if u1 + u2 > u: break
          for h1 in range(h+1):
           for h2 in range(h+1-h1):
            for l1 in range(l+1):
             for l2 in range(l+1-l1):
              left0 = u1+h1+l1; right0 = u2+h2+l2
              diff = abs(left0 - right0)
              if diff > g or left0 + right0 == 0: continue
              if (u1, h1, l1) > (u2, h2, l2) and False: continue
              # left down: left heavy-possible or right light-possible
              tot = u + h + l + g  # every coin outside the new suspect set is known genuine
              a = ok(k-1, 0, u1+h1, u2+l2, min(CAP, tot-(u1+h1+u2+l2)))
              if not a: continue
              b = ok(k-1, 0, u2+h2, u1+l1, min(CAP, tot-(u2+h2+u1+l1)))
              if not b: continue
              ng = min(CAP, tot-(u-u1-u2+h-h1-h2+l-l1-l2))
              c = ok(k-1, u-u1-u2, h-h1-h2, l-l1-l2, ng)
              if c: return True
        return False
    return ok
def best(k, spare, need_dir=True):
    f = make(need_dir)  # N=1 with no spare is unsolvable for direction, so scan, not stop at first failure
    return max(n for n in range(2, 16) if f(k, n, 0, 0, spare))
r = {(k, s): best(k, s) for k in (2, 3) for s in (0, 1)}
print("S1/S2 max N (need direction):", r)
print("S3 13 coins k=3 no spare, direction needed:", make(True)(3, 13, 0, 0, 0))
print("S4 (break) 13 coins k=3 no spare, coin only:", make(False)(3, 13, 0, 0, 0))
# first weighing of the 12-coin solution: which split sizes work
f = make(True); firsts = []
for m in range(1, 7):
    u1 = u2 = m
    if f(2, 0, m, m, 0) if False else False: pass
    ok1 = f(2, 0, m, m, 0)  # left down state: m maybe-heavy + m maybe-light
    ok2 = f(2, 12 - 2*m, 0, 0, 2*m)
    if ok1 and ok2: firsts.append(m)
print("S5 first-weighing sizes that leave every outcome solvable (12 coins, k=3):", firsts)
exp = {(2,0):3,(3,0):12,(2,1):4,(3,1):13}
ok = r == exp and not make(True)(3,13,0,0,0) and make(False)(3,13,0,0,0) and firsts == [4]
print("RESULT: %s max N %s; 13 unsolvable w/o spare (direction) but solvable coin-only; 12-coin first weighing %s vs %s" % ("PASS" if ok else "FAIL", r, firsts, firsts))
