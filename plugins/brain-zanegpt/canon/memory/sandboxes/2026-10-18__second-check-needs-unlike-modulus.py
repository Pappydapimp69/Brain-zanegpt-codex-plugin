# Sandbox: two check digits on 4-digit numbers, hit by every two-digit change (positions i<j, new digits differ).
# Run 1 prediction (missed: unlike pair gave joint/product 0.38, not 0.8-1.25; the checks were anti-correlated, not independent): with unlike checks (digit sum mod 10 and weighted sum 1,2,3,4 mod 11, coprime moduli)
# the joint miss rate is within 0.8-1.25 of the product of the single miss rates; with a dependent pair
# (digit sum mod 10 and digit sum mod 5, BREAK) the joint miss rate equals the mod-10 rate, >=1.9x the product.
# Also: the sum check misses 100% of transpositions while the weighted check misses 0% of them.
# Run 2 prediction (after run 1): unlike pair joint/product below 0.6 because a sum-preserving change (d_j = -d_i mod 10) rarely
# preserves the weighted sum mod 11; dependent pair stays >= 1.9x. Everything else unchanged.
from itertools import combinations, product
N = [(a, b, c, d) for a in range(10) for b in range(10) for c in range(10) for d in range(10)]
W = (1, 2, 3, 4)
checks = {
    "sum10": lambda x: sum(x) % 10, "w11": lambda x: sum(w * v for w, v in zip(W, x)) % 11,
    "sum5": lambda x: sum(x) % 5,
}
def two_digit_changes():
    for x in N:
        for i, j in combinations(range(4), 2):
            for vi, vj in product(range(10), repeat=2):
                if vi != x[i] and vj != x[j]:
                    y = list(x); y[i], y[j] = vi, vj; yield x, tuple(y)
def rates(a, b):
    n = ma = mb = mj = 0
    for x, y in two_digit_changes():
        n += 1; sa = checks[a](x) == checks[a](y); sb = checks[b](x) == checks[b](y)
        ma += sa; mb += sb; mj += sa and sb
    return ma / n, mb / n, mj / n
pa, pb, pj = rates("sum10", "w11"); r1 = pj / (pa * pb)
print("unlike: miss sum10=%.4f w11=%.4f joint=%.4f joint/product=%.2f" % (pa, pb, pj, r1))
qa, qb, qj = rates("sum10", "sum5"); r2 = qj / (qa * qb)
print("dependent (BREAK): miss sum10=%.4f sum5=%.4f joint=%.4f joint/product=%.2f" % (qa, qb, qj, r2))
tr = [(x, (x[1], x[0], x[2], x[3])) for x in N if x[0] != x[1]]
t_sum = sum(checks["sum10"](x) == checks["sum10"](y) for x, y in tr) / len(tr)
t_w = sum(checks["w11"](x) == checks["w11"](y) for x, y in tr) / len(tr)
print("transposition miss: sum10=%.2f w11=%.2f" % (t_sum, t_w))
ok = r1 < 0.6 and r2 >= 1.9 and abs(qj - qa) < 1e-12 and t_sum == 1.0 and t_w == 0.0
print("RESULT: %s unlike checks joint/product %.2f, dependent pair %.2f; transpositions missed by sum 100%% and weighted 0%%"
      % ("PASS" if ok else "FAIL", r1, r2))
