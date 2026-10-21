"""Reliability sandbox: k-of-n redundancy, MTTF, and the beta-factor common-cause model.

Model (exponential, non-repairable, identical units, rate lam):
  beta-factor: each unit's rate splits into independent (1-beta)*lam and a shared
  common-cause event of rate beta*lam that kills ALL units at once (series block).
  R_sys(t) = exp(-beta*lam*t) * P(at least k of n independent units alive).
Everything is expanded into a finite sum of c_i * exp(-a_i t), so MTTF = sum c_i/a_i is EXACT
(Fractions) and Q(t) = 1 - R(t) is evaluated in closed form. No RNG, no integration.
Sources: mathpages kmath498 (dual MTTF 3/2, triplex 11/6);
         ReliaSoft HotWire 115 "The Beta Factor Method" (RAID pair, lam=0.017/yr, beta=0.08,
         1-year Q = 0.0016 with CCF vs 0.0003 ignoring it).
"""
from fractions import Fraction as F
from math import comb, exp, log

def terms(k, n, lam, beta):
    """R(t) = sum c*exp(-a t); returns dict a -> c (a, c Fractions)."""
    li, lc = (1 - beta) * lam, beta * lam
    out = {}
    for j in range(k, n + 1):  # exactly j alive: C(n,j) p^j (1-p)^(n-j), p = e^{-li t}
        for m in range(n - j + 1):  # (1-p)^(n-j) = sum C(n-j,m)(-1)^m p^m
            c = comb(n, j) * comb(n - j, m) * (-1) ** m
            a = (j + m) * li + lc
            out[a] = out.get(a, 0) + c
    return {a: c for a, c in out.items() if c != 0}

def mttf(k, n, lam=F(1), beta=F(0)):
    return sum(F(c) / a for a, c in terms(k, n, lam, beta).items())

def Q(k, n, t, lam=1.0, beta=0.0):
    # direct (not via expansion) to avoid cancellation at tiny lam*t
    p = exp(-(1 - beta) * lam * t)
    r = sum(comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))
    return 1 - exp(-beta * lam * t) * r

ok = True
def check(name, cond, detail):
    global ok
    ok &= bool(cond)
    print(f"[{'ok' if cond else 'XX'}] {name}: {detail}")

# S1 sanity, beta = 0
m12, m13, m23 = mttf(1, 2), mttf(1, 3), mttf(2, 3)
check("S1 1oo2/1oo3/2oo3 MTTF", (m12, m13, m23) == (F(3, 2), F(11, 6), F(5, 6)),
      f"{m12}, {m13}, {m23} (x 1/lam)")
# cross-check expansion against direct Q at one point
t0 = 0.37
rq = 1 - sum(c * exp(-float(a) * t0) for a, c in terms(1, 2, F(1), F(1, 10)).items())
check("S1b expansion == direct Q", abs(rq - Q(1, 2, t0, beta=0.1)) < 1e-12, f"{rq:.12f}")

# S2 reproduce the ReliaSoft RAID example
lam, b = 0.017, 0.08
q_ccf = Q(1, 2, 1.0, lam, b)
q_ind = Q(1, 2, 1.0, lam, 0.0)
check("S2 ReliaSoft RAID with CCF ~0.0016", abs(q_ccf - 0.0016) < 0.00005, f"{q_ccf:.6f}")
check("S2 ReliaSoft RAID ignoring CCF ~0.0003", abs(q_ind - 0.0003) < 0.00002, f"{q_ind:.6f}")
print(f"    ratio {q_ccf / q_ind:.2f}x; beta*lam*t = {b * lam:.6f}")

# S3 short mission, beta = 0.1
lt, b = 0.01, 0.1
qx = Q(1, 2, lt, 1.0, b); qs = 1 - exp(-lt); naive = qs**2
mb = mttf(1, 2, F(1), F(1, 10))
check("S3 short mission: CCF dominates (ratio >= 10)", qx / naive >= 10,
      f"Q exact {qx:.3e} vs naive Q^2 {naive:.3e} -> {qx / naive:.2f}x")
check("S3 MTTF barely moves (<2%)", abs(float(mb) / 1.5 - 1) < 0.02,
      f"MTTF {mb} = {float(mb):.4f}/lam ({(float(mb) / 1.5 - 1) * 100:+.2f}%)")
check("S3 closed form 2 - 1/(2-beta)", mb == 2 - 1 / (2 - F(1, 10)), "exact match")

# S4 BREAK: long mission -- does CCF still dominate?
lt = 3.0
qx = Q(1, 2, lt, 1.0, b); naive = (1 - exp(-lt)) ** 2
r4 = qx / naive
print(f"[--] S4 BREAK lam*t=3: exact {qx:.4f} vs naive {naive:.4f} -> {r4:.3f}x (CCF dominance gone)")
check("S4 claim correctly bounded (ratio < 1.1 at long mission)", r4 < 1.1, f"{r4:.3f}")
# crossover where beta*lam*t == ((1-beta)lam t)^2
xo = b / (1 - b) ** 2
print(f"    crossover lam*t = beta/(1-beta)^2 = {xo:.4f}; ratio there "
      f"{Q(1, 2, xo, 1.0, b) / (1 - exp(-xo)) ** 2:.2f}x")

# S5 2oo3 vs single: find crossover by bisection (deterministic)
lo, hi = 0.01, 3.0
for _ in range(80):
    mid = (lo + hi) / 2
    if Q(2, 3, mid) < 1 - exp(-mid): lo = mid
    else: hi = mid
check("S5 2oo3 beats single only below lam*t = ln2", abs(lo - log(2)) < 1e-9,
      f"crossover {lo:.6f} vs ln2 {log(2):.6f}; MTTF 2oo3 = {m23} < 1")

# summary sweep: ratio exact/naive for the pair, beta=0.1
print("    sweep beta=0.1:", ", ".join(
    f"lt={x}: {Q(1, 2, x, 1.0, 0.1) / (1 - exp(-x)) ** 2:.2f}x" for x in (0.001, 0.01, 0.1, 0.3, 1, 3)))

if ok:
    print("RESULT: PASS beta=0.1 pair: short-mission Q 10.9x the Q^2 estimate while MTTF moves -1.75% "
          "(1.4737 vs 1.5/lam); ReliaSoft RAID reproduced; dominance vanishes past lam*t~beta/(1-beta)^2; "
          "2oo3 MTTF 5/6 < single")
else:
    print("RESULT: FAIL see XX lines")
