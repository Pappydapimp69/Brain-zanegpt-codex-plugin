"""Prediction (before run): at new base 6101 for P in 6..8 the first-cover dict counter (entry 1's method) and the
reduce-and-cover counter (entry 2's method) give IDENTICAL period-average shadow counts at every N in P-1..2P+1,
both averages are flat exactly at N=P and N=2P, a base-0 control differs at N=P, and a size-only sloppy cover
(built to break) differs from both somewhere. Deterministic, stdlib only."""
from fractions import Fraction as F
from functools import reduce

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def count(P, T, N):
    s = {"first": 0, "reduce": 0, "sloppy": 0}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                first = {}
                for x in V[a]: first.setdefault(x, a)
                cut = a if first else 0
                for x in V[b]:
                    if x not in first: first[x] = b; cut = b
                s["first"] += last != cut
                A = set(V[a])
                cov = reduce(lambda acc, x: acc and (x in A), V[b], True)
                cut2 = b if not cov else (a if V[a] else 0)
                s["reduce"] += last != cut2
                cut3 = b if not (len(V[b]) <= len(V[a])) else (a if V[a] else 0)
                s["sloppy"] += last != cut3
    return s

def avg(P, base, N):
    tot = {"first": 0, "reduce": 0, "sloppy": 0}
    for r in range(P):
        for k, v in count(P, base + r, N).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (6, 7, 8):
    Ns = list(range(P - 1, 2 * P + 2))
    A = {N: avg(P, 6101, N) for N in Ns}
    agree = all(v["first"] == v["reduce"] for v in A.values())
    flats = [N for N in Ns[1:] if A[N]["first"] == A[N - 1]["first"]]
    ctrl = avg(P, 0, P)["first"] != A[P]["first"]
    sloppy = any(v["sloppy"] != v["first"] for v in A.values())
    print(P, flats, agree, ctrl, sloppy, A[P]["first"], A[2 * P]["first"], flush=True)
    ok = ok and agree and flats == [P, 2 * P] and ctrl and sloppy
    out.append(f"P{P} flats={flats} avgP={A[P]['first']} avg2P={A[2*P]['first']} agree={agree} ctrl_differs={ctrl} sloppy_differs={sloppy}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
