"""Prediction (before run): the reduce-and-chain-lookup cover test, run at offset 6029 for P in [5, 7], gives period-average shadow counts IDENTICAL to a dict-membership reference
at N in {P-1, P, 2P-1, 2P, 2P+1}, with averages flat exactly at N=P and N=2P (avg[N]==avg[N-1]).
Built to break: base-0 control must differ at N=P; a buggy any-landing-covered rule (any instead of all) must NOT reproduce the dict average at N=P. Deterministic, stdlib only."""
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

from functools import reduce
def cov_red(b, a):
    sa = frozenset(a)
    return reduce(lambda acc, x: acc and (x in sa), b, True)

COVS = (("dict", cov_dict), ("reduce-and-chain-lookup", cov_red))
NAMES = ["dict", "reduce-and-chain-lookup"]

def count(P, T, N):
    sh = {n: 0 for n in NAMES}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for nm, cov in COVS:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[nm] += last != cut
    return sh

def avg(P, base, N):
    tot = {n: 0 for n in NAMES}
    for r in range(P):
        for k, v in count(P, base + r, N).items():
            tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

def cov_any(b, a):
    D = dict.fromkeys(a)
    return any(x in D for x in b)

def wrong_rule(P, base, N):
    tot = 0
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    cut = b if not cov_any(V[b], V[a]) else (a if V[a] else 0)
                    tot += last != cut
    return F(tot, P)

ok = True; out = []
for P in [5, 7]:
    A = {N: avg(P, 6029, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(len(set(v.values())) == 1 for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    wrong = wrong_rule(P, 6029, P)
    ok = ok and same and flats == [P, 2 * P] and ctrl and wrong != A[P]["dict"]
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} any_rule_avgP={wrong}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
