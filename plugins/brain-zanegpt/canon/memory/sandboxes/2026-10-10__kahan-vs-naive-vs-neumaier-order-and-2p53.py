"""Prediction (before run): (1) summing 1,000,000 copies of 0.1: naive error vs exact (Fraction of the same floats) is
> 1e-6 relative-ish absolute (>1e-6), Kahan error < 1e-9, so Kahan wins by > 1000x. (2) 2**53 followed by 1000 ones:
naive stays at 2**53 (loses all 1000); Kahan recovers within 1 of the exact total. (3) Order: 4 fixed orders of a
mixed-magnitude set give >= 2 distinct naive results but ONE identical Kahan result.
ITERATION 1 FAIL: Kahan gave 2 distinct results over the orders, not 1 (compensation narrows order dependence, it does not remove it).
ITERATION 2 FAIL: Kahan spread was only 51x smaller (4.65 vs 238.65) because the +-1e16 terms trigger its known weakness; Neumaier's spread was 2.8e-13.
Revised (3): Kahan spread >= 10x smaller than naive and not zero; Neumaier spread < 1e-9. (4) Built to break: [1.0, 1e100, 1.0,
-1e100]: plain Kahan returns 0.0 (wrong, exact is 2.0) while Neumaier and math.fsum return 2.0.
Deterministic, stdlib only."""
import math
from fractions import Fraction as F
def naive(xs):
    s = 0.0
    for x in xs: s += x
    return s
def kahan(xs):
    s = 0.0; c = 0.0
    for x in xs:
        y = x - c; t = s + y; c = (t - s) - y; s = t
    return s
def neumaier(xs):
    s = 0.0; c = 0.0
    for x in xs:
        t = s + x
        c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
        s = t
    return s + c
exact = lambda xs: F(0) + sum(F(x) for x in xs)
xs = [0.1] * 1000000
ex = exact(xs)
e1 = {f.__name__: abs(float(F(f(xs)) - ex)) for f in (naive, kahan, neumaier)}
print("S1 0.1 x 1e6 abs error:", e1)
big = [2.0**53] + [1.0] * 1000
ex2 = exact(big)
e2 = {f.__name__: float(F(f(big)) - ex2) for f in (naive, kahan, neumaier)}
print("S2 2^53 + 1000 ones error:", e2)
vals = [1e16, 1.0, -1e16, 3.25, 0.1, 1e-8, 7.0, 1e8, -1e8, 0.3] * 20
orders = [vals, sorted(vals), sorted(vals, key=abs), sorted(vals, reverse=True)]
nv = {naive(o) for o in orders}; kv = {kahan(o) for o in orders}; nm = {neumaier(o) for o in orders}
spread = lambda f, os: max(float(F(f(o))) for o in os) - min(float(F(f(o))) for o in os)
sp = {f.__name__: spread(f, orders) for f in (naive, kahan, neumaier)}
print("S3 spread over orders:", sp)
print("S3 distinct results over 4 orders: naive", len(nv), "kahan", len(kv), "neumaier", len(nm), "exact", float(exact(vals)))
bad = [1.0, 1e100, 1.0, -1e100]
s4 = (kahan(bad), neumaier(bad), math.fsum(bad), naive(bad))
print("S4 [1,1e100,1,-1e100] kahan/neumaier/fsum/naive:", s4)
ok = e1['naive'] > 1e-6 and e1['kahan'] < 1e-9 and e1['naive'] / max(e1['kahan'], 1e-300) > 1000 \
     and e2['naive'] == -1000.0 and abs(e2['kahan']) <= 1 and len(nv) >= 2 and len(kv) <= len(nv) and sp['kahan'] * 10 <= sp['naive'] and sp['kahan'] > 0 and sp['neumaier'] < 1e-9 \
     and s4[0] == 0.0 and s4[1] == 2.0 and s4[2] == 2.0
print("RESULT:", "PASS" if ok else "FAIL", "0.1x1e6 naive err %.3g kahan %.3g; 2^53+1000 ones naive lost %d kahan err %g; order results naive %d kahan %d neumaier %d (spread naive %.3g kahan %.3g); adversarial kahan %.1f vs neumaier %.1f" %
      (e1['naive'], e1['kahan'], -e2['naive'], e2['kahan'], len(nv), len(kv), len(nm), sp['naive'], sp['kahan'], s4[0], s4[1]))
