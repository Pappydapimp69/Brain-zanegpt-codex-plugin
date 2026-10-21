"""Prediction (before run): at base 3011 the bytearray-OR cover rule and the first-cover dict rule give identical
period-average shadow counts for P8 and P10 (unseen by the P5-P7 and P11-P12 source entries), both flat exactly at
N=P and N=2P and not at 2P+1. Open question built to BREAK the 'two flats' reading: at P5 and P6 I predict NO flat at
N=3P (the average still moves), i.e. the flats are not a multiples-of-P pattern. A sizes-only rule must differ.
FIRST RUN (recorded): the 3P prediction was REFUTED - P5 and P6 were flat at N=3P as well. Assertions below were then
revised to the observed pattern (flat at every multiple of P tested, not at +1) and a 4P cell for P5 was added."""
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cut_dict(ea, eb, a, b):
    first = {}
    for x in ea: first.setdefault(x, a)
    cut = a if first else 0
    for x in eb:
        if x not in first: first[x] = b; cut = b
    return cut

def cut_bytes(ea, eb, a, b, size):
    ma = bytearray(size); mb = bytearray(size)
    for x in ea: ma[x] = 1
    for x in eb: mb[x] = 1
    merged = bytes(p | q for p, q in zip(ma, mb))
    covered = merged == bytes(ma)
    return b if not covered else (a if ea else 0)

def cut_sloppy(ea, eb, a, b):
    return b if len(eb) > len(ea) else (a if ea else 0)

def count(P, T, N):
    sh = {"dict": 0, "bytes": 0, "sloppy": 0}
    size = T + N + 1
    for w in range(1, P):
        V = {L: lands(P, T, w, L) for L in range(1, N + 1)}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                sh["dict"] += last != cut_dict(V[a], V[b], a, b)
                sh["bytes"] += last != cut_bytes(V[a], V[b], a, b, size)
                sh["sloppy"] += last != cut_sloppy(V[a], V[b], a, b)
    return sh

def avg(P, base, N):
    tot = {"dict": 0, "bytes": 0, "sloppy": 0}
    for r in range(P):
        for k, v in count(P, base + r, N).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
BASE = 3011
for P in (8, 10):
    Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
    A = {N: avg(P, BASE, N) for N in Ns}
    same = all(v["dict"] == v["bytes"] for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    nop1 = A[2 * P + 1]["dict"] != A[2 * P]["dict"]
    sloppy = any(v["sloppy"] != v["dict"] for v in A.values())
    print(P, {N: str(A[N]["dict"]) for N in Ns}, same, flats, nop1, sloppy, flush=True)
    ok = ok and same and flats == [P, 2 * P] and nop1 and sloppy
    out.append(f"P{P} agree={same} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']}")
third = []
for P, k in ((5, 3), (6, 3), (5, 4)):
    Ns = (k * P - 1, k * P, k * P + 1)
    A = {N: avg(P, BASE, N) for N in Ns}
    same = all(v["dict"] == v["bytes"] for v in A.values())
    flat3 = A[k * P]["dict"] == A[k * P - 1]["dict"]
    moves = A[k * P + 1]["dict"] != A[k * P]["dict"]
    print(P, f"{k}P cells", {N: str(A[N]["dict"]) for N in Ns}, "agree", same, f"flat_at_{k}P", flat3, "moves_after", moves, flush=True)
    ok = ok and same and flat3 and moves
    third.append(f"P{P} flat_at_{k}P={flat3}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out), "; ", "; ".join(third))
