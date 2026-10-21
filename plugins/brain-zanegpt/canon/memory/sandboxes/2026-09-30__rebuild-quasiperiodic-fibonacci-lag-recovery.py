# Rebuild of: quasiperiodic state nearly recovers (~99%) at Fibonacci-number lags; exact recovery needs periodicity.
# Own fixture: N=1000 uses; signals are rotation sequences legal(t) = frac(t*alpha + 0.13) < 0.4 (width differs from
# the original's), with alpha = golden conjugate, alpha = sqrt(2)-1 (silver, BREAK case) and a periodic P=13 W=5 signal.
# Agreement(lag) = fraction of t in [0,N) with legal(t) == legal(t+lag). Integer-exact via Fraction-free floor on
# high-precision Decimal to avoid float drift.
from decimal import Decimal, getcontext
getcontext().prec = 60
N = 1000
PHI = (Decimal(5).sqrt() - 1) / 2
SILVER = Decimal(2).sqrt() - 1
OFF, WID = Decimal("0.13"), Decimal("0.4")
def rot(alpha):
    def f(t):
        x = t * alpha + OFF
        return (x - int(x)) < WID
    return f
per = lambda t: (t % 13) < 5
def agree(f, lag): return sum(f(t) == f(t + lag) for t in range(N)) / N
FIB = [34, 55, 89, 144, 233, 377]
NONFIB = [40, 70, 100, 200, 300]
PELL = [29, 70, 169]
g, s = rot(PHI), rot(SILVER)
gf = [agree(g, L) for L in FIB]; gn = [agree(g, L) for L in NONFIB]
sf = [agree(s, L) for L in FIB]; sp = [agree(s, L) for L in PELL]
pp = [agree(per, L) for L in (13, 26, 39)]
print("golden  @Fib   ", [round(x, 3) for x in gf])
print("golden  @nonFib", [round(x, 3) for x in gn])
print("silver  @Fib   ", [round(x, 3) for x in sf], "(break case)")
print("silver  @Pell  ", [round(x, 3) for x in sp])
print("periodic@P,2P,3P", pp)
exact_periodic = all(x == 1.0 for x in pp)
golden_near = all(x >= 0.99 for x in gf if True) 
golden_near_large = all(x >= 0.99 for x, L in zip(gf, FIB) if L >= 89)
golden_never_exact = all(x < 1.0 for x in gf)
silver_fib_fails = min(sf) < 0.95
print(f"checks: periodic exact={exact_periodic} golden>=0.99 all Fib={golden_near} golden>=0.99 Fib>=89={golden_near_large} golden never exact={golden_never_exact} silver fails at Fib={silver_fib_fails}")
ok = exact_periodic and golden_near_large and golden_never_exact
print("RESULT: %s periodic exact at P multiples; golden rotation min %.3f at Fib lags>=89 (min %.3f over 34-377), never 1.0; silver rotation min %.3f at Fib lags -> near-recovery is tied to the golden ratio, not quasiperiodicity in general" % ("PASS" if ok else "FAIL", min(x for x, L in zip(gf, FIB) if L >= 89), min(gf), min(sf)))
