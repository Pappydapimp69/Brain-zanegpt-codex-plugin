# New domain CONTINUED-FRACTIONS. Real scenario: leap-year rules approximate the tropical year
# 365.2421897 days (J2000 mean value, Meeus). Fractional part f = 0.2421897 = leap days per year.
# PREDICTION (before run): the convergents of f are 0/1, 1/4, 7/29, 8/33, 31/128; Gregorian 97/400 is NOT a convergent
# but beats 8/33 in absolute error is false (8/33 is closer); every convergent p/q is the closest fraction with denominator <= q
# (brute force); the Julian 1/4 drifts one day per ~128 years and 8/33 per ~ 4,000+ years.
from fractions import Fraction
f = Fraction(2421897, 10000000)
def cf(x, n=10):
    out = []
    for _ in range(n):
        a = x.numerator // x.denominator; out.append(a)
        x -= a
        if x == 0: break
        x = 1 / x
    return out
a = cf(f)
conv = []
h0, h1, k0, k1 = 0, 1, 1, 0
for ai in a:
    h0, h1 = h1, ai*h1 + h0 if False else ai*h1 + h0
    k0, k1 = k1, ai*k1 + k0
    conv.append(Fraction(h1, k1))
print("cf", a[:8]); print("convergents", [str(c) for c in conv[:7]])
def best_up_to(q):
    best = None
    for den in range(1, q+1):
        num = round(f*den)
        for n in (num-1, num, num+1):
            c = Fraction(n, den)
            if best is None or abs(c-f) < abs(best-f): best = c
    return best
bests = {c.denominator: best_up_to(c.denominator) == c for c in conv[1:7] if c.denominator <= 20000}
print("convergent is best with denominator <= q:", bests)
err = lambda c: abs(float(c-f))
cands = {"1/4": Fraction(1,4), "97/400": Fraction(97,400), "8/33": Fraction(8,33), "31/128": Fraction(31,128)}
for k, c in cands.items(): print(k, "error %.2e leap-days/yr" % err(c), "days to drift 1 day: %.0f years" % (1/err(c)))
is_conv = {k: c in conv for k, c in cands.items()}
print("is convergent", is_conv)
ok = (is_conv == {"1/4": True, "97/400": False, "8/33": True, "31/128": True} and all(bests.values())
      and err(cands["8/33"]) < err(cands["97/400"]))
print(f"RESULT: {'PASS' if ok else 'FAIL'} convergents {[str(c) for c in conv[1:6]]}; Gregorian 97/400 not a convergent; 8/33 error {err(cands['8/33']):.1e} vs 97/400 {err(cands['97/400']):.1e}")
