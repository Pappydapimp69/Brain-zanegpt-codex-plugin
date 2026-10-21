# Exact enumeration. A nightly batch of n tasks must finish inside a wall-clock window (local 00:00 -> 06:00).
# Normal night = 6 real hours; spring-forward night = 5 real hours; fall-back night = 7 real hours.
# Task hours {0.5,1,2} p {.5,.3,.2}; shared delay factor {1,1.5,2.5} p {.6,.3,.1} (brainwork/E92 shape).
from itertools import product
from fractions import Fraction as F
D = [(F(1,2),F(1,2)),(F(1),F(3,10)),(F(2),F(1,5))]
S = [(F(1),F(3,5)),(F(3,2),F(3,10)),(F(5,2),F(1,10))]
def p_fit(n, window, shared):
    tot = F(0)
    if shared:
        for f, pf in S:
            for combo in product(D, repeat=n):
                d = sum(x for x,_ in combo); p = pf
                for _,q in combo: p *= q
                if d*f <= window: tot += p
    else:
        for combo in product(D, repeat=n):
            d = sum(x for x,_ in combo); p = F(1)
            for _,q in combo: p *= q
            if d <= window: tot += p
    return float(tot)
n = 3  # worst-case sum = 6 h, planned to exactly fill a normal 6 h night
r = {}
for name, w in (("normal",6),("spring",5),("fall",7)):
    for sh in (True, False):
        r[(name,sh)] = p_fit(n, F(w), sh)
        print(f"{name:6} window={w}h shared={sh}: P(finish)={r[(name,sh)]:.3f}")
# naive "6 worst-case hours is safe" belief: true only without shared delay
ok1 = r[("normal",False)] == 1.0
ok2 = r[("normal",True)] < 0.95
ok3 = r[("spring",True)] < r[("normal",True)] - 0.02 and r[("fall",True)] > r[("normal",True)]
# BREAK: does the extra fall-back hour rescue the plan? no: still below 1
ok4 = r[("fall",True)] < 0.95
print("RESULT: %s normal-night P=%.3f shared vs %.3f independent; spring-forward %.3f; fall-back %.3f still short of 1"
      % ("PASS" if ok1 and ok2 and ok3 and ok4 else "FAIL", r[("normal",True)], r[("normal",False)], r[("spring",True)], r[("fall",True)]))
