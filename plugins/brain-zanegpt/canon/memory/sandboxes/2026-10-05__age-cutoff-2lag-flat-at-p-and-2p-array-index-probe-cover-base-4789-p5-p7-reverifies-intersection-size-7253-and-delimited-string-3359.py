"""Prediction (before run): a array.index with ValueError probe cover test at offset 4789 for P in (5, 7) gives period-average
shadow counts IDENTICAL to a dict-membership reference at N in {P-1, P, 2P-1, 2P, 2P+1}, with averages flat exactly at N=P and N=2P (avg[N]==avg[N-1]).
Built to break: base-0 control must differ at N=P; an any-for-all cover must differ from dict at N=P; an array probe that tests only the first element of b is run too and should differ. Deterministic, stdlib only."""
from fractions import Fraction as F
import itertools, operator, struct, collections, functools

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_any(b, a):
    D = dict.fromkeys(a)
    return any(x in D for x in b)

import array
def cov_new(b, a):
    arr = array.array("l", a)
    def has(x):
        try:
            arr.index(x)
            return True
        except ValueError:
            return False
    return all(has(x) for x in b)
def cov_bug(b, a):
    arr = array.array("l", a)
    ends = b[:1]
    return all(x in arr for x in ends)

COVS = (("dict", cov_dict), ("new", cov_new), ("any", cov_any), ("bug", cov_bug))

def count(P, T, N):
    sh = {"dict": 0, "new": 0, "any": 0, "bug": 0, "last": 0}
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
    tot = {"dict": 0, "new": 0, "any": 0, "bug": 0, "last": 0}
    for r in range(P):
        for k, v in count(P, base + r, N).items():
            tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (5, 7):
    A = {N: avg(P, 4789, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(v["dict"] == v["new"] for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P)["new"] != A[P]["new"]
    anyd = A[P]["any"]
    bugd = any(v["bug"] != v["dict"] for v in A.values())
    wrong = A[P]["last"]
    print(P, flats, same, ctrl, anyd, bugd, wrong, flush=True)
    ok = ok and same and flats == [P, 2 * P] and ctrl and anyd != A[P]["dict"] and bugd and wrong == 0
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} any_rule_avgP={anyd} bug_differs={bugd}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
