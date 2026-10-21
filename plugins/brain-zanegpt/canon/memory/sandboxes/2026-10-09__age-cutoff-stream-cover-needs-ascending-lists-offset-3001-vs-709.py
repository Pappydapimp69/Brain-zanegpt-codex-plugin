"""Prediction (before run): for P in [8, 10] the 2-lag period-average shadow count from the
dict cover is IDENTICAL at offsets 3001 and 709 (P10: 15 at N=P, 65/2 at N=2P, the values recorded
by both source entries), and the stream covers (shared-iterator two-pointer, heap-pop) equal dict on
ascending landing lists at both offsets. Built to BREAK: feed the same covers DESCENDING lists; the
stream covers must then DISAGREE with dict (dict/set stay order-free), so the 'stream = dict' rule
holds only for ascending input. Deterministic, stdlib only, no RNG."""
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

COVS = (("dict", cov_dict), ("two_pointer_gen", cov_two_pointer_gen), ("heap_pop", cov_heap_pop))

def avg(P, base, N, desc=False):
    tot = {n: 0 for n, _ in COVS}
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            if desc: V = [None] + [list(reversed(v)) for v in V[1:]]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    for name, cov in COVS:
                        cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                        tot[name] += last != cut
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (8, 10):
    Ns = (P - 1, P, 2 * P)
    asc = {base: {N: avg(P, base, N) for N in Ns} for base in (3001, 709)}
    offset_free = all(asc[3001][N]["dict"] == asc[709][N]["dict"] for N in Ns)
    stream_eq = all(len(set(asc[b][N].values())) == 1 for b in asc for N in Ns)
    flat = asc[3001][P]["dict"] == asc[3001][P - 1]["dict"]
    desc = avg(P, 709, P, desc=True)
    desc_breaks = desc["dict"] == asc[709][P]["dict"] and (desc["two_pointer_gen"] != desc["dict"] or desc["heap_pop"] != desc["dict"])
    ok = ok and offset_free and stream_eq and flat and desc_breaks
    out.append(f"P{P} offset_free={offset_free} stream_eq_asc={stream_eq} flatP={flat} avgP={asc[3001][P]['dict']} avg2P={asc[3001][2*P]['dict']} "
               f"desc[dict={desc['dict']} twoptr={desc['two_pointer_gen']} heap={desc['heap_pop']}] desc_breaks={desc_breaks}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
