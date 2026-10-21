"""Prediction (before run): at base 163 (fresh), P in [11,12], the heap-pop and shared-iterator two-pointer cover tests give period-average 2-lag shadow
counts IDENTICAL to the dict-membership reference at N in {P-1,P,2P-1,2P,2P+1}, with flats exactly at N=P and N=2P (avg[N]==avg[N-1]); the
base-0 control differs at N=P (built to break), and an any-instead-of-all cover rule gives a different avg at N=P (built to break).
Exact Fractions, deterministic, stdlib only."""
from fractions import Fraction as F
import heapq

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_two_pointer_gen(b, a):
    it = iter(a); return all(any(y == x for y in it) for x in b)
def cov_heap_pop(b, a):
    h = list(a); heapq.heapify(h)
    for x in b:
        while h and h[0] < x: heapq.heappop(h)
        if not h or h[0] != x: return False
    return True
def cov_any(b, a):
    D = dict.fromkeys(a); return any(x in D for x in b)

COVS = (("dict", cov_dict), ("two_pointer_gen", cov_two_pointer_gen), ("heap_pop", cov_heap_pop), ("any_bug", cov_any))

def avg(P, base, N):
    tot = {n: 0 for n, _ in COVS}
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    for n, c in COVS:
                        cut = b if not c(V[b], V[a]) else (a if V[a] else 0)
                        tot[n] += last != cut
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (11, 12):
    A = {N: avg(P, 163, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    agree = all(A[N]["dict"] == A[N][k] for N in A for k in ("two_pointer_gen", "heap_pop"))
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    anyd = A[P]["any_bug"] != A[P]["dict"]
    print(f"P{P}: avg dict N=P-1..2P+1", {N: str(A[N]['dict']) for N in A}, "any_bug@P", A[P]["any_bug"], "base0@P", avg(P, 0, P)["dict"], flush=True)
    ok = ok and agree and flats == [P, 2 * P] and ctrl and anyd
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={agree} ctrl_differs={ctrl} any_differs={anyd}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
