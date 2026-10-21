"""Prediction (before run): bisect-search and integer-bitmask cover tests, at offset 1931 for P in [6, 9], give period-average shadow counts IDENTICAL to a dict reference at N in {P-1, P, 2P-1, 2P, 2P+1}, flat (avg[N]==avg[N-1]) exactly at N=P and N=2P.
Built to break: base-0 control must differ at N=P; an any-instead-of-all cover rule must not match the dict average at N=P; a cover test that assumes ascending input but is fed a reversed list (stream-order bug) must not match either. Deterministic, stdlib only."""
from fractions import Fraction as F
from bisect import bisect_left

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_bisect(b, a):
    for x in b:
        i = bisect_left(a, x)
        if i == len(a) or a[i] != x: return False
    return True
def cov_intmask(b, a):
    ma = 0
    for x in a: ma |= 1 << x
    mb = 0
    for x in b: mb |= 1 << x
    return mb & ~ma == 0
def cov_any(b, a):
    D = dict.fromkeys(a); return any(x in D for x in b)
def cov_bisect_reversed(b, a):   # BUG: unsorted haystack
    return cov_bisect(b, a[::-1])

NAMES = ["dict", "bisect", "intmask"]
IMPL = {"dict": cov_dict, "bisect": cov_bisect, "intmask": cov_intmask}

def count(P, T, N, impls):
    sh = {n: 0 for n in impls}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for n, cov in impls.items():
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[n] += last != cut
    return sh

def avg(P, base, N, impls=IMPL):
    tot = {n: 0 for n in impls}
    for r in range(P):
        for k, v in count(P, base + r, N, impls).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in [6, 9]:
    A = {N: avg(P, 1931, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(len(set(v.values())) == 1 for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P, {"dict": cov_dict})["dict"] != A[P]["dict"]
    anyv = avg(P, 1931, P, {"any": cov_any})["any"]
    rev = avg(P, 1931, P, {"rev": cov_bisect_reversed})["rev"]
    good = A[P]["dict"]
    ok = ok and same and flats == [P, 2 * P] and ctrl and anyv != good and rev != good
    out.append(f"P{P} flats={flats} avgP={good} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} any_avgP={anyv} reversed_avgP={rev}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
