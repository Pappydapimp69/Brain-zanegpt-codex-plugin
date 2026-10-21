"""Prediction (before run): at P in {7,10}, the first-cover dict path (landing->first lag, cut=last lag adding a new time)
and the shared-iterator two-pointer / heappop covers give IDENTICAL exact period-average shadow counts at N in {P-1,P,2P-1,2P,2P+1},
and those averages are IDENTICAL at offsets 709 and 211 (a full period of offsets is averaged, so the base cancels); flats exactly at N=P and 2P.
Break cases: base 0 differs at N=P; two-pointer fed an UNSORTED landing list disagrees with dict; any-for-all differs. Deterministic, stdlib only."""
from fractions import Fraction as F
import heapq

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def shadow_firstcover(Va, Vb):
    first = {}
    cut = 0
    for lag, V in ((1, Va), (2, Vb)):
        new = False
        for x in V:
            if x not in first:
                first[x] = lag; new = True
        if new: cut = lag
    last = 2 if Vb else (1 if Va else 0)
    return last != cut

def cover_two_pointer(b, a):
    it = iter(a)
    return all(any(y == x for y in it) for x in b)

def cover_heap(b, a):
    h = list(a); heapq.heapify(h)
    for x in b:
        while h and h[0] < x: heapq.heappop(h)
        if not h or h[0] != x: return False
    return True

def shadow_cover(Va, Vb, cov):
    last = 2 if Vb else (1 if Va else 0)
    cut = 2 if not cov(Vb, Va) else (1 if Va else 0)
    return last != cut

def avg(P, base, N, kind, scramble=False):
    tot = 0
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    Va, Vb = V[a], V[b]
                    if kind == "dict": s = shadow_firstcover(Va, Vb)
                    elif kind == "two_pointer":
                        if scramble: Va = Va[::-1]
                        s = shadow_cover(Va, Vb, cover_two_pointer)
                    elif kind == "heap": s = shadow_cover(Va, Vb, cover_heap)
                    elif kind == "any":
                        s = shadow_cover(Va, Vb, lambda b_, a_: any(x in set(a_) for x in b_))
                    tot += s
    return F(tot, P)

ok = True; out = []
for P in (7, 10):
    Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
    A = {N: {k: avg(P, 709, N, k) for k in ("dict", "two_pointer", "heap")} for N in Ns}
    agree = all(len(set(v.values())) == 1 for v in A.values())
    B211 = {N: avg(P, 211, N, "dict") for N in Ns}
    base_inv = all(B211[N] == A[N]["dict"] for N in Ns)
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P, "dict") != A[P]["dict"]
    scr = avg(P, 709, P, "two_pointer", scramble=True) != A[P]["dict"]
    anyd = avg(P, 709, P, "any") != A[P]["dict"]
    ok = ok and agree and base_inv and flats == [P, 2 * P] and ctrl and scr and anyd
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={agree} base709==211={base_inv} ctrl_differs={ctrl} unsorted_breaks={scr} any_breaks={anyd}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
