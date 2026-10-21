"""Prediction (before run): an adjacent-duplicate count over the sorted concatenation decides cover at offset 8669 for P in [7, 8]; period-average shadow counts equal the dict-membership reference at N in P-1,P,2P-1,2P,2P+1 with flat exactly at N=P and 2P; built to break: base-0 control, any-overlap cover and length-only cover must differ. Deterministic, stdlib only."""

from fractions import Fraction as F
import sys

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_any(b, a):
    D = dict.fromkeys(a)
    return any(x in D for x in b)

def cov_sloppy(b, a):
    return len(b) <= len(a)

def shadows(P, T, N, cov):
    sh = 0
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                sh += last != cut
    return sh

def avg(P, base, N, cov):
    return F(sum(shadows(P, base + r, N, cov) for r in range(P)), P)

def run(NEW, base, Ps):
    ok = True; out = []
    for P in Ps:
        Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
        A = {N: avg(P, base, N, cov_dict) for N in Ns}
        B = {N: avg(P, base, N, NEW) for N in Ns}
        same = A == B
        flats = [N for N in (P, 2 * P) if B[N] == B[N - 1]]
        ctrl = avg(P, 0, P, NEW) != B[P]
        wrong = avg(P, base, P, cov_any)
        slop = avg(P, base, P, cov_sloppy) != B[P]
        print(P, flats, same, ctrl, wrong, slop, flush=True)
        ok = ok and same and flats == [P, 2 * P] and ctrl and wrong != B[P] and slop
        out.append(f"P{P} flats={flats} avgP={B[P]} avg2P={B[2*P]} impls_agree={same} ctrl_differs={ctrl} any_rule_avgP={wrong} sloppy_differs={slop}")
    print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))

def cov_new(b, a):
    s = sorted(list(a) + list(b))
    return sum(1 for i in range(1, len(s)) if s[i] == s[i - 1]) == len(b)
run(cov_new, 8669, [7, 8])
