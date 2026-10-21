"""Prediction (before run): the position-indexed 0/1 table hit sum cover test, run at offset 109 for P in [7,8,9], gives period-average shadow counts IDENTICAL to a dict-membership reference
at N in {P-1, P, 2P-1, 2P, 2P+1}, flat exactly at N=P and N=2P (avg[N]==avg[N-1]). Built to break: base-0 control must differ at N=P; an any-instead-of-all cover must NOT reproduce the dict average. Deterministic, stdlib only."""
from fractions import Fraction as F
from math import gcd

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_any(b, a):
    D = dict.fromkeys(a)
    return any(x in D for x in b)

def cov_new(b, a):
    # exact-count signature: b covered iff the multiset sum of landing positions over a, restricted to b's positions, is rebuilt by
    # a position-indexed 0/1 table keyed in a dict of ints (value 1 per a landing); coverage = sum of table hits equals len(b)
    tab = {}
    for x in a: tab[x] = 1
    return sum(tab.get(x, 0) for x in b) == len(b)


COVS = (("dict", cov_dict), ("new", cov_new))

def count(P, T, N, covs):
    sh = {n: 0 for n, _ in covs}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for name, cov in covs:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[name] += last != cut
    return sh

def avg(P, base, N, covs=COVS):
    tot = {n: 0 for n, _ in covs}
    for r in range(P):
        for k, v in count(P, base + r, N, covs).items():
            tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in [7,8,9]:
    A = {N: avg(P, 109, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(len(set(v.values())) == 1 for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P, COVS[:1])["dict"] != A[P]["dict"]
    wrong = avg(P, 109, P, (("any", cov_any),))["any"]
    ok = ok and same and flats == [P, 2 * P] and ctrl and wrong != A[P]["dict"]
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} any_rule_avgP={wrong}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
