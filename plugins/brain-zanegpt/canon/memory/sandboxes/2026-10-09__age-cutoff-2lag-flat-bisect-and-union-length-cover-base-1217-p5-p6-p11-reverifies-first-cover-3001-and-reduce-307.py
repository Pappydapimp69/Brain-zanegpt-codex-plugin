"""Prediction (before run): bisect-membership and union-length covers at offset 1217 reproduce the recorded averages:
P5 2 and 26/5, P6 7/2 and 17/2 (set/reduce entry, base 307) and P11 215/11 and 460/11 (dict entry, base 3001),
with averages flat exactly at N=P and N=2P. Built to break: base-0 control differs at N=P; an any-for-all rule differs at N=P.
Deterministic, stdlib only."""
from fractions import Fraction as F
from bisect import bisect_left

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_bisect(b, a):
    def has(x):
        i = bisect_left(a, x); return i < len(a) and a[i] == x
    return all(has(x) for x in b)

def cov_union(b, a):
    return len(set(a) | set(b)) == len(a)

def cov_any(b, a):
    s = set(a); return any(x in s for x in b)

def avg(P, base, N, cov):
    tot = 0
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    tot += last != cut
    return F(tot, P)

REC = {5: (F(2), F(26, 5)), 6: (F(7, 2), F(17, 2)), 11: (F(215, 11), F(460, 11))}
ok = True; out = []
for P in (5, 6, 11):
    A = {N: avg(P, 1217, N, cov_bisect) for N in (P - 1, P, 2 * P - 1, 2 * P)}
    agree = A[P] == avg(P, 1217, P, cov_union) and A[2 * P] == avg(P, 1217, 2 * P, cov_union)
    flats = [N for N in (P, 2 * P) if A[N] == A[N - 1]]
    rec = (A[P], A[2 * P]) == REC[P]
    ctrl = avg(P, 0, P, cov_bisect) != A[P]
    anyr = avg(P, 1217, P, cov_any) != A[P]
    ok = ok and agree and flats == [P, 2 * P] and rec and ctrl and anyr
    out.append(f"P{P} flats={flats} avgP={A[P]} avg2P={A[2*P]} union_agrees={agree} recorded={rec} ctrl_differs={ctrl} any_differs={anyr}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
