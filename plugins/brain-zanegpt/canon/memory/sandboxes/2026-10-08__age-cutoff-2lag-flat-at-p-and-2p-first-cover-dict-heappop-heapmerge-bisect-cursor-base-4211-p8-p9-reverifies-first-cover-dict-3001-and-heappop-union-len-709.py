"""Prediction (before run): four cover implementations (first-cover dict, heappop drain, heapq.merge+groupby union length,
a moving-lo bisect cursor) run at offset 4211 for P in [8, 9] give period-average shadow counts IDENTICAL to each other at
N in {P-1, P, 2P-1, 2P, 2P+1}; flats exactly at N=P and N=2P; recorded values P8 8 then 18, P9 100/9 then 220/9.
Built to break: base-0 control must differ at N=P; an any-landing-covered rule must NOT reproduce the average at N=P;
Deterministic, stdlib only."""
from fractions import Fraction as F
from bisect import bisect_left
import heapq
from itertools import groupby

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_heap_pop(b, a):
    h = list(a); heapq.heapify(h)
    for x in b:
        while h and h[0] < x: heapq.heappop(h)
        if not h or h[0] != x: return False
    return True

def cov_merge_union_len(b, a):
    u = lambda *ls: sum(1 for _ in groupby(heapq.merge(*ls)))
    return u(a, b) == u(a)

def cov_bisect_cursor(b, a):
    lo = 0
    for x in b:
        lo = bisect_left(a, x, lo)
        if lo == len(a) or a[lo] != x: return False
    return True

def cov_any(b, a):
    D = dict.fromkeys(a)
    return any(x in D for x in b)

COVS = (("dict", cov_dict), ("heap_pop", cov_heap_pop), ("merge_union_len", cov_merge_union_len), ("bisect_cursor", cov_bisect_cursor))
NAMES = [n for n, _ in COVS]

def count(P, T, N, covs=COVS):
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

REC = {8: (F(8), F(18)), 9: (F(100, 9), F(220, 9))}
ok = True; out = []
for P in (8, 9):
    Ns = [P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1]
    A = {N: avg(P, 4211, N) for N in Ns}
    agree = all(len(set(A[N].values())) == 1 for N in Ns)
    d = {N: A[N]["dict"] for N in Ns}
    flats = [N for N in (P, 2 * P) if d[N] == A[{P: P - 1, 2 * P: 2 * P - 1}[N]]["dict"]]
    match = (d[P], d[2 * P]) == REC[P]
    ctrl = avg(P, 0, P, COVS[:1])["dict"] != d[P]
    anyv = avg(P, 4211, P, (("any", cov_any),))["any"]
    print(P, agree, flats, match, ctrl, anyv, flush=True)
    ok = ok and agree and flats == [P, 2 * P] and match and ctrl and anyv != d[P]
    out.append(f"P{P} flats={flats} avgP={d[P]} avg2P={d[2*P]} impls_agree={agree} match={match} ctrl_differs={ctrl} any_rule_avgP={anyv}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
