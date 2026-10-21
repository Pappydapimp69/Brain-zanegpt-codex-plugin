# New domain TESSELLATION. Real source: Archimedean (uniform) tilings of regular polygons,
# Grunbaum & Shephard, Tilings and Patterns: 11 tilings, from 17 vertex types that fit 360 degrees.
# PREDICTION (before run): 21 multisets of regular polygons (3..42 sides) sum to 360 degrees;
# 17 distinct cyclic vertex types after ordering; an odd-polygon neighbour filter keeps 11.
from fractions import Fraction
from itertools import permutations
def ang(n): return Fraction(180*(n-2), n)
# 1) multisets of 3..6 polygons summing to 360
res = set()
def rec(start, left, cur):
    if left == 0:
        if len(cur) >= 3: res.add(tuple(cur))
        return
    for n in range(start, 43):
        a = ang(n)
        if a <= left: rec(n, left-a, cur+[n])
rec(3, Fraction(360), [])
multisets = sorted(res)
# 2) cyclic arrangements up to rotation/reflection
def canon(seq):
    cands = []
    for s in (seq, seq[::-1]):
        for i in range(len(s)): cands.append(tuple(s[i:]+s[:i]))
    return min(cands)
types = set()
for m in multisets:
    for p in set(permutations(m)): types.add(canon(list(p)))
# 3) odd-neighbour filter: around an odd-sided polygon the neighbours alternate, so the two
# polygons beside it at this vertex must be equal
def ok(seq):
    k = len(seq)
    for i, n in enumerate(seq):
        if n % 2 == 1 and seq[i-1] != seq[(i+1) % k]: return False
    return True
passing = sorted(t for t in types if ok(t))
print("multisets", len(multisets), "types", len(types), "pass odd filter", len(passing))
for t in passing: print(".".join(map(str,t)))
# 3b) iteration 2: closure walk. In a uniform tiling every vertex has the same type T, so walking
# round a polygon p edge by edge must pass through p-many vertices of type T and return to the start.
def closes(T):
    k = len(T)
    for p in set(T):
        if p % 2 == 0: continue            # even polygons close by alternating; odd ones are the test
        starts = [(i, s) for i in range(k) if T[i] == p for s in (1, -1)]
        found = False
        for (i, s) in starts:
            # state: at vertex with p at position i, leaving along the edge shared with T[i+s]
            def walk(j, side, steps):
                N = T[(j+side) % k]
                if steps == p: return (j, side) == (i, s) or (j, side) == (i, -s) and False
                for j2 in range(k):
                    if T[j2] != p: continue
                    if T[(j2-1) % k] == N: nxt = 1
                    elif T[(j2+1) % k] == N: nxt = -1
                    else: continue
                    if walk(j2, nxt, steps+1): return True
                return False
            if walk(i, s, 0): found = True; break
        if not found: return False
    return True
passing2 = sorted(t for t in types if closes(t))
print("closure walk keeps", len(passing2), [".".join(map(str,t)) for t in passing2])
# 4) break: 3.12.12 passes (odd 3 between two 12s) and 4.6.12 / 3.4.6.4 pass; 3.7.42 must fail
brk = {"3.3.4.12": closes((3,3,4,12)), "3.7.42": ok((3,7,42)), "3.12.12": ok((3,12,12)), "3.4.6.4": ok((3,4,6,4))}
print(brk)
good = len(multisets)==17 and len(types)==21 and len(passing)==8 and len(passing2)==11 and not brk["3.3.4.12"]
print(f"RESULT: {'PASS' if good else 'FAIL'} {len(multisets)} angle-sum multisets, {len(types)} cyclic vertex types, equal-neighbour filter keeps {len(passing)} (misses 3 real tilings), closure walk keeps {len(passing2)}")
