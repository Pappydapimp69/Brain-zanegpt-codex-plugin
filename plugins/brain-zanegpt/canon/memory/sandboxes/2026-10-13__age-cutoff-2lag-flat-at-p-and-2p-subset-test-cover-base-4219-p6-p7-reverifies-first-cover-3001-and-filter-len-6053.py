"""Prediction (before run): a subset-test cover (lag b cuts iff its landing set is NOT a subset of lag a's; no dict,
no first-cover stream, no bitmask) at fresh base 4219 gives P6 avg 7/2 at N=P and 17/2 at N=2P, P7 38/7 and 88/7,
flats exactly at N=P and N=2P and nowhere else for N in P-1..2P+1. Built to break: (a) base-0 control must differ at N=P,
(b) a mutated window predicate (> instead of >=) must lose the flats. Stdlib, deterministic, no RNG."""
from fractions import Fraction as F

def count(P, T, N, strict=False):
    sh = 0
    for w in range(1, P):
        ev = {}
        for L in range(1, N + 1):
            ev[L] = frozenset(t + L for t in range(T) if ((t % P) > w if strict else (t % P) >= w) or ((t + L) % P) < w)
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                cut = b if not ev[b] <= ev[a] else a
                last = b if ev[b] else (a if ev[a] else 0)
                sh += (last != cut)
    return sh

def avg(P, base, N, strict=False):
    return F(sum(count(P, base + r, N, strict) for r in range(P)), P)

REC = {6: (F(7, 2), F(17, 2)), 7: (F(38, 7), F(88, 7))}
ok = True; out = []
for P in (6, 7):
    Ns = list(range(P - 1, 2 * P + 2))
    A = {N: avg(P, 4219, N) for N in Ns}
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    match = (A[P], A[2 * P]) == REC[P]
    ctrl = avg(P, 0, P) != A[P]
    As = {N: avg(P, 4219, N, True) for N in Ns}
    mut_flats = [N for N in Ns[1:] if As[N] == As[N - 1]]
    mut_breaks = mut_flats != [P, 2 * P]
    print(P, flats, A[P], A[2 * P], match, ctrl, mut_flats, flush=True)
    ok = ok and flats == [P, 2 * P] and match and ctrl and mut_breaks
    out.append(f"P{P} flats={flats} avgP={A[P]} avg2P={A[2*P]} ctrl_differs={ctrl} mutant_flats={mut_flats}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
