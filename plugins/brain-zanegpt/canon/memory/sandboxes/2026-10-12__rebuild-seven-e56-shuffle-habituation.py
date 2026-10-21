"""Rebuild of seven E56 (fourth-wall effects: shuffle bag beats random; random wastes
a quarter of triggers by twice the pool; variants past ~2 showings).
Own fixture: pools N = 5 and 12, habituation r = 0.2, 0.5, 0.65 (not 0.35), dud
threshold 0.2, closed-form expectations (prior showings of an effect before trigger t
~ Binomial(t-1, 1/N), so E[r^k] = (1-(1-r)/N)^(t-1)), dud share by exact binomial.
Predictions written before running:
 P1 shuffle >= random for every (r, N) at M = N (Jensen; expect hold).
 P2 the shuffle/random ratio stays >= 1.25 for r up to 0.65 (expect MISS at high r).
 P3 random wastes >= 0.2 of triggers by M = 2N for every r (expect MISS at r = 0.65).
"""
from math import comb, log

def random_total(N, M, r):
    a = 1 - (1 - r) / N
    return sum(a ** t for t in range(M))

def shuffle_total(N, M, r):
    return sum(r ** (t // N) for t in range(M))

def dud_k(r):
    k = 0
    while r ** k >= 0.2:
        k += 1
    return k  # smallest prior-showing count that makes a dud

def random_dud_share(N, M, r):
    K = dud_k(r); p = 1 / N; tot = 0.0
    for t in range(M):
        tot += 1 - sum(comb(t, k) * p**k * (1 - p)**(t - k) for k in range(min(K, t + 1)))
    return tot / M

ratios, duds, p1 = {}, {}, True
for N in (5, 12):
    for r in (0.2, 0.5, 0.65):
        rt, st = random_total(N, N, r), shuffle_total(N, N, r)
        ratios[(N, r)] = st / rt
        duds[(N, r)] = random_dud_share(N, 2 * N, r)
        p1 &= st >= rt - 1e-12
        print(f"N={N:2d} r={r:.2f}: M=N shuffle {st:.2f} random {rt:.2f} (x{st/rt:.3f}); "
              f"random dud share at M=2N {duds[(N, r)]:.3f}; dud from showing {dud_k(r)+1}")
p2 = all(v >= 1.25 for v in ratios.values())
p3 = all(v >= 0.2 for v in duds.values())
checks = [("P1 shuffle >= random", p1), ("P2 ratio >= 1.25 for all r", p2), ("P3 random dud share >= 0.2 at 2N", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks:
    print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; ratio range x{min(ratios.values()):.3f}-x{max(ratios.values()):.3f}; "
      f"random dud share at 2N {min(duds.values()):.3f}-{max(duds.values()):.3f}")
