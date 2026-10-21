"""Prediction (before run): at base 1303, P in [7,10], N=P: (1) first-cover dict form equals dict-membership and the order-sensitive two-pointer
stream cover on ASCENDING landing lists (same shadow totals); (2) when the landing lists are fed DESCENDING, the two-pointer stream cover
diverges from the dict (different total at N=P) while dict, bytes-find and heap-pop (heapify) stay equal to ascending. Break case: descending input. Deterministic, stdlib only."""
from fractions import Fraction as F
import heapq

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_two_pointer(b, a):
    it = iter(a); return all(any(y == x for y in it) for x in b)
def cov_heap(b, a):
    h = list(a); heapq.heapify(h)
    for x in b:
        while h and h[0] < x: heapq.heappop(h)
        if not h or h[0] != x: return False
    return True
def cov_find(b, a):
    S = "," + ",".join(map(str, a)) + ","
    return all(("," + str(x) + ",") in S for x in b)

def first_cover_cut(vb, va, a, b):
    """first-cover dict form: cut lag = last lag that adds a new landing time."""
    D = {}
    for lag, v in ((1, va), (2, vb)):
        for t in v: D.setdefault(t, lag)
    if any(l == 2 for l in D.values()): return b
    return a if va else 0

COVS = {"dict": cov_dict, "two_pointer": cov_two_pointer, "heap": cov_heap, "find": cov_find}

def total(P, base, N, descending):  # descending: False | True (all lists) | 'mixed' (a-side lists only)
    tot = {k: 0 for k in list(COVS) + ["first_cover"]}
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            if descending is True: V = [None] + [v[::-1] for v in V[1:]]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    Va = V[a][::-1] if descending == 'mixed' else V[a]
                    for k, c in COVS.items():
                        cut = b if not c(V[b], Va) else (a if Va else 0)
                        tot[k] += last != cut
                    tot["first_cover"] += last != first_cover_cut(V[b], V[a], a, b)
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (7, 10):
    asc = total(P, 1303, P, False); desc = total(P, 1303, P, True); mix = total(P, 1303, P, 'mixed')
    asc_same = len(set(asc.values())) == 1
    # observed (prediction half-refuted): consistent reversal keeps relative order, so two-pointer is unchanged; heap-pop breaks
    desc_tp_stable = desc["two_pointer"] == asc["dict"]
    heap_breaks = desc["heap"] != asc["dict"]
    mixed_tp_breaks = mix["two_pointer"] != asc["dict"]
    order_free_ok = all(desc[k] == asc["dict"] and mix[k] == asc["dict"] for k in ("dict", "find", "first_cover"))
    ok = ok and asc_same and desc_tp_stable and heap_breaks and mixed_tp_breaks and order_free_ok
    out.append(f"P{P} asc_all_equal={asc_same} avg={asc['dict']} desc_two_pointer={desc['two_pointer']} desc_heap={desc['heap']} mixed_two_pointer={mix['two_pointer']} order_free_ok={order_free_ok}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
