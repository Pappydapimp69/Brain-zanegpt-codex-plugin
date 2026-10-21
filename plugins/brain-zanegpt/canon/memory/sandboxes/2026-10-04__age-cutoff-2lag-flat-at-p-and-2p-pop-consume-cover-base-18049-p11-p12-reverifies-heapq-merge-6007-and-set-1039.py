"""Prediction (before run): a consuming dict.pop cover (each b element popped from a copy of a, any miss fails) at offset 18049 for P in (11, 12) equals dict membership at N in {P-1,P,2P-1,2P,2P+1}, flat exactly at N=P and N=2P; I expect P11 215/11 and 460/11, P12 to match its dict reference.
Built to break: base-0 control must differ at N=P; an any-instead-of-all cover must give a different (larger) average; a sizes-only cover should differ; the ignore-cover rule (cut = last landing lag) must give 0 shadows. Deterministic, stdlib only."""
from fractions import Fraction as F
import itertools, heapq, functools, operator

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_new(b, a):
    D = dict.fromkeys(a, True)
    miss = object()
    for x in b:
        if D.pop(x, miss) is miss:
            return False
    return True

def cov_any(b, a):
    S = set(a)
    return any(x in S for x in b)

def cov_sloppy(b, a):
    return len(b) <= len(a)

COVS = (("dict", cov_dict), ("new", cov_new), ("any", cov_any), ("sloppy", cov_sloppy))

def count(P, T, N):
    sh = {"dict": 0, "new": 0, "any": 0, "sloppy": 0, "last": 0}
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
    tot = {}
    for r in range(P):
        for k, v in count(P, base + r, N).items():
            tot[k] = tot.get(k, 0) + v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (11, 12):
    A = {N: avg(P, 18049, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(v["dict"] == v["new"] for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P)["new"] != A[P]["new"]
    wrong = A[P]["last"]
    anyd = A[P]["any"] != A[P]["dict"]
    sloppy_differs = any(v["sloppy"] != v["dict"] for v in A.values())
    print(P, flats, same, ctrl, wrong, anyd, sloppy_differs, flush=True)
    ok = ok and same and flats == [P, 2 * P] and ctrl and wrong == 0 and anyd
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} wrong_rule_avgP={wrong} any_rule_avgP={A[P]['any']} sloppy_differs={sloppy_differs}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
