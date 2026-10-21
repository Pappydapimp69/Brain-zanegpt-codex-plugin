"""Rebuild of seven E24 (expose-first A / rescue-exposes B / two-at-fire C).
Own fixture: party of 5 with one fake, 3-night rescue window, search finds 0.5
per night. Deduction accuracy is DERIVED, not assumed: 1-of-n pick accuracy
= 1/n + skill*(1-1/n) with skill 0.2 (so 1-of-5 0.36), and the 1-of-2 duplicate
pick from a memory model: a day has 8 facts, the fake bends one, a question
covers 3, memory recalls with 0.7, both asked the same question ->
acc2 = 0.5 + 0.5*(3/8)*0.7. Exact fractions.
A: each night, until the fake is exposed, a pylon test uses that night; after
exposure, remaining nights search. B: search every night; a find ends it free.
C: search every night; a find brings two to the fire, pick (acc2), a wrong pick
costs a second pylon.
PREDICTIONS (written before running):
 P1 A has the lowest real-back rate
 P2 C real-back within 0.05 of B
 P3 C spends under 1.5 pylons per rescue with the derived accuracy
 P4 A spends more pylons per disappearance than C
 P5 (break) if a pylon test does NOT use the night (dusk test), A's real-back
    rises to within 0.05 of B - i.e. the collapse is entirely the time cost
"""
from fractions import Fraction as Fr
W, S, N = 3, Fr(1, 2), 5
skill = Fr(1, 5)
def acc(n): return Fr(1, n) + skill*(1 - Fr(1, n))
acc2 = Fr(1, 2) + Fr(1, 2)*Fr(3, 8)*Fr(7, 10)
def miss(k): return (1-S)**k
# A with time cost: distribution of night index of exposure
def A(timecost):
    back = Fr(0); pyl = Fr(0)
    p_unexp = Fr(1); n = N - 1  # candidates besides... party 5 incl fake: test among 5
    n = N
    night = 0
    while n >= 1:
        a = acc(n)
        p_exp_now = p_unexp*a
        pyl += p_unexp  # one test this round
        nights_left = W - (night + 1) if timecost else W
        if nights_left > 0:
            back += p_exp_now*(1 - miss(nights_left))
        p_unexp *= (1 - a); n -= 1
        if timecost: night += 1
        if n == 0: break
    return back, pyl
B_back = 1 - miss(W)
C_back = B_back
C_pyl_per_rescue = acc2*1 + (1-acc2)*2
A_back, A_pyl = A(True)
A2_back, _ = A(False)
C_pyl = C_back*C_pyl_per_rescue
print(f"acc5 {float(acc(5)):.3f} acc2 {float(acc2):.4f}")
print(f"A back {float(A_back):.3f} pylons {float(A_pyl):.3f}; B back {float(B_back):.3f}; "
      f"C back {float(C_back):.3f} pylons/rescue {float(C_pyl_per_rescue):.3f} per disappearance {float(C_pyl):.3f}")
print(f"A with free (dusk) tests: back {float(A2_back):.3f}")
checks = [A_back < min(B_back, C_back), abs(C_back-B_back) <= Fr(1, 20), C_pyl_per_rescue < Fr(3, 2),
          A_pyl > C_pyl, abs(A2_back - B_back) <= Fr(1, 20)]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 5 else 'FAIL'} {held}/5 predictions held; A back {float(A_back):.3f} "
      f"B/C back {float(B_back):.3f}; C pylons/rescue {float(C_pyl_per_rescue):.3f}; A pylons {float(A_pyl):.3f}; "
      f"A dusk-test back {float(A2_back):.3f}")
