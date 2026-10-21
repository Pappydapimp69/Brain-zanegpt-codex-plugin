# Compose Kawasaki-by-reflection (single vertex folds flat iff the composition of reflections
# across its creases is the identity) with tessellation vertex enumeration (regular polygons
# whose interior angles sum to 360). Treat each cyclic polygon vertex type as a crease vertex
# whose sector angles are the polygon interior angles.
# PREDICTION (before run): 21 cyclic types; Kawasaki-by-reflection holds for exactly the even
# degree types whose alternating angle sums are both 180; of the 11 Archimedean tiling vertex
# types exactly 4 fold flat (3.3.3.3.3.3, 4.4.4.4, 3.6.3.6, 3.4.6.4);
# RUN 1 REFUTED THIS: 3.6.3.6 has sectors 60,120,60,120 whose alternating sums are 120 and 240, so it
# does not fold; the corrected, re-run expectation below is 3 of 11. non-tiling types can also
# fold flat (3.3.6.6 does), so tiling and flat folding are independent properties.
from fractions import Fraction
from itertools import permutations
ang = lambda n: Fraction(180 * (n - 2), n)
res = set()
def rec(start, left, cur):
    if left == 0:
        if len(cur) >= 3: res.add(tuple(cur))
        return
    for n in range(start, 43):
        if ang(n) <= left: rec(n, left - ang(n), cur + [n])
rec(3, Fraction(360), [])
def canon(seq):
    c = []
    for s in (seq, seq[::-1]):
        for i in range(len(s)): c.append(tuple(s[i:] + s[:i]))
    return min(c)
types = sorted({canon(list(p)) for m in res for p in set(permutations(m))})
def folds_flat(T):                      # reflection composition: phi -> 2*theta - phi
    theta, thetas = Fraction(0), []
    for n in T:
        thetas.append(theta); theta += ang(n)
    if len(T) % 2: return False         # odd number of reflections is a reflection, never identity
    shift = sum(((-1) ** k) * 2 * t for k, t in enumerate(thetas))
    return shift % 360 == 0
def alt_rule(T):
    return len(T) % 2 == 0 and sum(ang(n) for n in T[0::2]) == 180 and sum(ang(n) for n in T[1::2]) == 180
archimedean = {(3,3,3,3,3,3), (4,4,4,4), (6,6,6), (3,6,3,6), (3,4,6,4), (3,3,3,4,4), (3,3,4,3,4),
               (3,3,3,3,6), (3,12,12), (4,8,8), (4,6,12)}
arch = {canon(list(t)) for t in archimedean}
foldable = [T for T in types if folds_flat(T)]
agree = all(folds_flat(T) == alt_rule(T) for T in types)
arch_fold = [T for T in foldable if T in arch]
nontile_fold = [T for T in foldable if T not in arch]
name = lambda T: ".".join(map(str, T))
print("types", len(types), "reflection==alt rule on all:", agree)
print("flat-foldable types:", [name(T) for T in foldable])
print("Archimedean and foldable:", [name(T) for T in arch_fold])
print("foldable but not an Archimedean vertex type:", [name(T) for T in nontile_fold])
ok = (len(types) == 21 and agree and len(arch_fold) == 3 and (3,6,3,6) not in foldable and len(arch & set(types)) == 11
      and (3,3,6,6) in foldable and len(nontile_fold) >= 1)
print("RESULT: %s %d cyclic types, reflection test equals the alternating-sum rule on all, %d flat-foldable, %d of 11 Archimedean types fold flat, %d foldable types do not tile uniformly"
      % ("PASS" if ok else "FAIL", len(types), len(foldable), len(arch_fold), len(nontile_fold)))
