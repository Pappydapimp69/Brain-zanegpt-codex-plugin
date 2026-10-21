"""Prediction (before run): bisect-walk, groupby-merge, reduce-fold and sorted-length covers, run at offset 1811 for P in [9, 11], give period-average shadow
counts IDENTICAL to a dict-membership reference at N in {P-1, P, 2P-1, 2P, 2P+1}, with averages flat exactly at N=P and N=2P (avg[N]==avg[N-1]).
Built to break: base-0 control must differ at N=P; an any-landing-covered rule (any instead of all) must NOT reproduce the dict average at N=P;
a lengths-only cover (len(b)<=len(a)) must NOT reproduce it either. Deterministic, stdlib only."""
from fractions import Fraction as F
from functools import reduce
from bisect import bisect_left
import itertools

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_bisect(b, a):
    lo = 0
    for x in b:
        lo = bisect_left(a, x, lo)
        if lo == len(a) or a[lo] != x: return False
    return True

def cov_groupby(b, a):
    merged = [k for k, _ in itertools.groupby(sorted(list(a) + list(b)))]
    return len(merged) == len(a)

def cov_reduce(b, a):
    A = set(a)
    return reduce(lambda ok, x: ok and x in A, b, True)

def cov_sorted_len(b, a):
    return len(sorted(set(a).union(b))) == len(a)

COVS = (("dict", cov_dict), ("bisect", cov_bisect), ("groupby", cov_groupby), ("reduce", cov_reduce), ("sorted_len", cov_sorted_len))
NAMES = [n for n, _ in COVS]

def count(P, T, N):
    sh = {n: 0 for n in NAMES}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for name, cov in COVS:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[name] += last != cut
    return sh

def avg(P, base, N):
    tot = {n: 0 for n in NAMES}
    for r in range(P):
        for k, v in count(P, base + r, N).items():
            tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

def mutant(P, base, N, cov):
    tot = 0
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    tot += last != cut
    return F(tot, P)

cov_any = lambda b, a: any(x in set(a) for x in b)
cov_len = lambda b, a: len(b) <= len(a)

ok = True; out = []
for P in [9, 11]:
    A = {N: avg(P, 1811, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(len(set(v.values())) == 1 for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    wa = mutant(P, 1811, P, cov_any); wl = mutant(P, 1811, P, cov_len)
    ok = ok and same and flats == [P, 2 * P] and ctrl and wa != A[P]["dict"] and wl != A[P]["dict"]
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} any_rule_avgP={wa} len_rule_avgP={wl}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
