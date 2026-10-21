"""Prediction (before run): at offset 3709, P in (7, 8), the first-cover dict shadow count equals the shared-iterator
two-pointer and heappop-walk covers when landing lists are ascending (flats exactly [P, 2P]); when the lists are
REVERSED or rotated, the two stream covers disagree with the dict average at N=P while the dict (order-free) still
matches. Built to break: reversed and rotated list orders. Deterministic, stdlib only."""
from fractions import Fraction as F
import heapq

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_iter(b, a):
    it = iter(a); return all(any(y == x for y in it) for x in b)
def cov_heap(b, a):
    h = list(a); heapq.heapify(h)
    for x in b:
        while h and h[0] < x: heapq.heappop(h)
        if not h or h[0] != x: return False
    return True

def first_cover_dict(ev, N):  # the E1 first-cover path
    sh = 0
    for a in range(1, N + 1):
        for b in range(a + 1, N + 1):
            first = {}
            for x in ev[a]: first.setdefault(x, a)
            cut = a if first else 0
            for x in ev[b]:
                if x not in first: first[x] = b; cut = b
            last = b if ev[b] else (a if ev[a] else 0)
            sh += last != cut
    return sh

def stream(ev, N, cov):
    sh = 0
    for a in range(1, N + 1):
        for b in range(a + 1, N + 1):
            last = b if ev[b] else (a if ev[a] else 0)
            cut = b if not cov(ev[b], ev[a]) else (a if ev[a] else 0)
            sh += last != cut
    return sh

ORD = {"asc": lambda l: l, "rev": lambda l: l[::-1], "rot": lambda l: l[len(l) // 2:] + l[:len(l) // 2]}

def avgs(P, base, N, order):
    tot = {"dict": 0, "iter": 0, "heap": 0}
    for r in range(P):
        for w in range(1, P):
            ev = {L: ORD[order](lands(P, base + r, w, L)) for L in range(1, N + 1)}
            tot["dict"] += first_cover_dict(ev, N)
            tot["iter"] += stream(ev, N, cov_iter)
            tot["heap"] += stream(ev, N, cov_heap)
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (7, 8):
    res = {}
    for o in ORD:
        res[o] = {N: avgs(P, 3709, N, o) for N in (P - 1, P, 2 * P - 1, 2 * P)}
    asc_same = all(len(set(v.values())) == 1 for v in res["asc"].values())
    flats = [N for N in (P, 2 * P) if res["asc"][N]["dict"] == res["asc"][N - 1]["dict"]]
    dict_free = all(len({res[o][N]["dict"] for o in ORD}) == 1 for N in res["asc"])
    rev_breaks = res["rev"][P]["iter"] != res["rev"][P]["dict"] or res["rev"][P]["heap"] != res["rev"][P]["dict"]
    rot_breaks = res["rot"][P]["iter"] != res["rot"][P]["dict"] or res["rot"][P]["heap"] != res["rot"][P]["dict"]
    print(P, flats, asc_same, dict_free, res["rev"][P], res["rot"][P], flush=True)
    ok = ok and asc_same and flats == [P, 2 * P] and dict_free and rev_breaks and rot_breaks
    out.append(f"P{P} asc_agree={asc_same} flats={flats} dict_order_free={dict_free} rev_breaks={rev_breaks} rot_breaks={rot_breaks} rev_avgP={dict(res['rev'][P])}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
