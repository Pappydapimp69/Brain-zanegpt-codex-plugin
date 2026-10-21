"""Prediction (before run), own fixture: sector angles on a 10-degree grid (36 units), degree 3..8, integer-degree
exact arithmetic. A reflection-composition test (fold the paper line direction through each crease in turn; flat iff
the direction returns to itself AND the number of creases is even) agrees with Kawasaki (both alternating sums = 180)
in 100 percent of patterns; odd degrees never pass; a tolerance of one grid step (10 deg) on the alternating sum accepts
extra patterns the exact test rejects (I predict 5 to 25 percent of all patterns). Built to break: degree-8 patterns,
and a non-grid half-step pattern."""
from itertools import product
def compositions(total, k, lo=1):
    if k == 1:
        if total >= lo: yield (total,)
        return
    for first in range(lo, total - lo * (k - 1) + 1):
        for rest in compositions(total - first, k - 1, lo): yield (first,) + rest
def kawasaki(sec, tol=0):
    a, b = sum(sec[0::2]), sum(sec[1::2])
    return len(sec) % 2 == 0 and abs(a - 180) <= tol and abs(b - 180) <= tol
def reflect_flat(sec):
    # crease k at cumulative angle c_k; reflecting a direction phi across a line at c gives (2c - phi) mod 360.
    # Walk once around: a flat fold maps the paper onto itself, so the composition of the reflections must fix a
    # generic test direction, which needs an even count of reflections and zero net rotation.
    if len(sec) % 2: return False
    creases, c = [], 0
    for s in sec: creases.append(c); c += s
    for phi in (7, 101, 233):          # three generic test directions
        x = phi
        for cr in creases: x = (2 * cr - x) % 360
        if x != phi: return False
    return True
U = 36; tot = 0; agree = 0; odd_pass = 0; tolacc = 0; disagree = []
deg_counts = {}
for k in range(3, 9):
    n = 0
    for sec in compositions(U, k):
        s = tuple(10 * u for u in sec); tot += 1; n += 1
        r, kw = reflect_flat(s), kawasaki(s)
        agree += (r == kw)
        if r != kw: disagree.append(s)
        if k % 2 and r: odd_pass += 1
        if kawasaki(s, 10) and not kw: tolacc += 1
    deg_counts[k] = n
exact = sum(1 for k in range(3, 9) for sec in compositions(U, k) if kawasaki(tuple(10 * u for u in sec)))
print("patterns", tot, deg_counts, "exact-flat", exact)
print("agree", agree, "disagree", len(disagree), disagree[:3], "odd passed", odd_pass)
print("tolerance(10deg) extra accepts", tolacc, "= %.1f percent of all" % (100 * tolacc / tot))
half = (90, 90, 90, 90.5)  # off-grid break: sums 180.5 / 179.5 is not 360
half_ok = (reflect_flat((95, 85, 95, 85)), kawasaki((95, 85, 95, 85)), kawasaki((90, 90, 90, 90.5)), kawasaki((90, 90, 90, 90.5), 10))
print("off-grid cases (95,85,95,85) refl/kaw", half_ok[:2], "(90,90,90,90.5) exact/tol", half_ok[2:])
ok = agree == tot and odd_pass == 0 and 0.05 <= tolacc / tot <= 0.25 and half_ok[2] is False and half_ok[3] is True
print("RESULT: %s %d patterns, %d disagreements, odd-degree passes %d, tol-10 extra accepts %.1f percent" % ("PASS" if ok else "FAIL", tot, len(disagree), odd_pass, 100 * tolacc / tot))
