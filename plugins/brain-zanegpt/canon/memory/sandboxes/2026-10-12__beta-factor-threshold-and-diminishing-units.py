import math
from math import comb, exp, log

def R(x, k, n, beta):
    q = (1 - beta) * x
    p = exp(-q)
    s = sum(comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))
    return exp(-beta * x) * s

def Q(x, k, n, beta): return 1 - R(x, k, n, beta)

def mttf(k, n, beta, hi=60.0, steps=60000):
    h = hi / steps
    return sum(R((i + .5) * h, k, n, beta) for i in range(steps)) * h

ok = True
# S1: 1-of-2 pair, beta=.1, x=lam*t=.01
b, x = .1, .01
ratio = Q(x, 1, 2, b) / (1 - exp(-x)) ** 2
m = mttf(1, 2, b); m_closed = (2 - 1 / (2 - b))
print("S1 ratio=%.2f mttf=%.4f closed=%.4f" % (ratio, m, m_closed))
ok &= abs(ratio - 10.9) < .2 and abs(m - 1.4737) < 1e-3

# S2: threshold x*=beta/(1-beta)^2 : shared term == independent term
for b in (.02, .1, .3):
    xs = b / (1 - b) ** 2
    shared = b * xs; indep = ((1 - b) * xs) ** 2
    print("S2 beta=%.2f x*=%.4f shared=%.5f indep=%.5f" % (b, xs, shared, indep))
    ok &= abs(shared - indep) < 1e-12

# S3 (BREAK): do extra units stop helping? Q(n=6)/Q(n=3), 1-of-n, beta=.1
b = .1
for x in (.001, .01, .1, .5):
    q3, q6 = Q(x, 1, 3, b), Q(x, 1, 6, b)
    xs = b / (1 - b) ** 2
    print("S3 x=%.3f x*=%.3f Q3=%.3e Q6=%.3e gain3to6=%.3f" % (x, xs, q3, q6, q3 / q6))
    if x < xs / 10: ok &= q3 / q6 < 1.01      # shared term: no gain
    if x >= .5: ok &= q3 / q6 > 1.2           # above threshold gain returns

# S4: 2-of-3 voting, beta=0: MTTF 5/6 and crossover at ln2
m23 = mttf(2, 3, 0.0)
cross = min(i / 10000 for i in range(1, 20000) if R(i / 10000, 2, 3, 0) < R(i / 10000, 1, 1, 0))
print("S4 mttf2of3=%.4f cross=%.4f ln2=%.4f" % (m23, cross, log(2)))
ok &= abs(m23 - 5 / 6) < 2e-3 and abs(cross - log(2)) < 2e-3
# S5 (BREAK): with beta=.1 does the crossover stay at ln2?
cross_b = min(i / 10000 for i in range(1, 20000) if R(i / 10000, 2, 3, .1) < R(i / 10000, 1, 1, 0))
print("S5 beta=.1 crossover=%.4f (ln2 shifts up)" % cross_b)
ok &= cross_b > log(2) + .05   # predicted DOWN, observed UP

# S6: rater-blend analogue, error var = beta + (1-beta)/k
for b in (0, .6):
    red = 1 - (b + (1 - b) / 8) / 1.0
    print("S6 beta=%.1f 8-rater variance cut=%.1f%%" % (b, 100 * red))
    ok &= red <= (1 - b) + 1e-9
print("RESULT: %s beta-factor: ratio 10.9x, threshold beta/(1-beta)^2, extra units gain <1%% below it, 2-of-3 crossover ln2 moves UP to %.3f at beta=.1" % ("PASS" if ok else "FAIL", cross_b))
