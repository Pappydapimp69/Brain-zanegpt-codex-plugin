"""Prediction (before run): at new offset 1201 for P in [9, 11], a first-cover dict (time -> first lag, streamed) and the
stream-style covers (shared-iterator two-pointer, heappop walk) give IDENTICAL 2-lag period-average shadow counts at
N in {P-1, P, 2P-1, 2P, 2P+1}, with averages flat exactly at N=P and N=2P (and nowhere else in P..2P+1 except those two).
Built to break: base-0 control must differ at N=P; an any-for-all cover rule must give a different average at N=P. Stdlib, deterministic."""
from fractions import Fraction as F
import heapq

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cut_first_cover(ea, eb, a, b):
    first = {}
    for x in ea: first.setdefault(x, a)
    cut = a if first else 0
    for x in eb:
        if x not in first: first[x] = b; cut = b
    return cut

def covered_two_pointer(eb, ea):
    it = iter(ea)
    return all(any(y == x for y in it) for x in eb)

def covered_heap(eb, ea):
    h = list(ea); heapq.heapify(h)
    for x in eb:
        while h and h[0] < x: heapq.heappop(h)
        if not h or h[0] != x: return False
    return True

def covered_any(eb, ea):
    D = set(ea); return any(x in D for x in eb)

def cut_by(cov, ea, eb, a, b):
    return b if not cov(eb, ea) else (a if ea else 0)

IMPLS = ["first_cover", "two_pointer", "heap", "any_bug"]

def count(P, T, N):
    sh = dict.fromkeys(IMPLS, 0)
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                sh["first_cover"] += last != cut_first_cover(V[a], V[b], a, b)
                sh["two_pointer"] += last != cut_by(covered_two_pointer, V[a], V[b], a, b)
                sh["heap"] += last != cut_by(covered_heap, V[a], V[b], a, b)
                sh["any_bug"] += last != cut_by(covered_any, V[a], V[b], a, b)
    return sh

def avg(P, base, N):
    tot = dict.fromkeys(IMPLS, 0)
    for r in range(P):
        for k, v in count(P, base + r, N).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (9, 11):
    Ns = list(range(P - 1, 2 * P + 2))
    A = {N: avg(P, 1201, N) for N in Ns}
    good = ("first_cover", "two_pointer", "heap")
    agree = all(len({A[N][k] for k in good}) == 1 for N in Ns)
    flats = [N for N in Ns[1:] if A[N]["first_cover"] == A[N - 1]["first_cover"]]
    ctrl = avg(P, 0, P)["first_cover"] != A[P]["first_cover"]
    bug = A[P]["any_bug"] != A[P]["first_cover"]
    print(P, "avgP=%s avg2P=%s" % (A[P]["first_cover"], A[2 * P]["first_cover"]), "flats", flats, agree, ctrl, bug, flush=True)
    ok = ok and agree and flats == [P, 2 * P] and ctrl and bug
    out.append("P%d avgP=%s avg2P=%s flats=%s agree=%s ctrl_differs=%s any_bug_differs=%s" % (P, A[P]["first_cover"], A[2 * P]["first_cover"], flats, agree, ctrl, bug))
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
