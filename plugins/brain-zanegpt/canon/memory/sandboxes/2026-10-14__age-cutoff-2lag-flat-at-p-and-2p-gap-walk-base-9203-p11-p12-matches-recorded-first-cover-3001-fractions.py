"""Prediction (before run): the gap-encoded walk cover at offset 9203 for P in [11, 12] equals the dict reference at N in (P-1,P,2P-1,2P,2P+1); averages at N=P and 2P equal the fractions recorded by the first-cover dict entry at base 3001 (P11 215/11 and 460/11; P12 25 and 53); flats exactly [P, 2P]; base-0 control and any-overlap cover must differ. Deterministic, stdlib only."""
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

def gaps(v):
    out, prev = [], 0
    for x in v:
        out.append(x - prev); prev = x
    return out

def cov_new(b, a):
    ga, gb = gaps(a), gaps(b)
    pa = 0; ia = 0
    pb = 0
    for g in gb:
        pb += g
        while pa < pb and ia < len(ga):
            pa += ga[ia]; ia += 1
        if pa != pb:
            return False
    return True

REC = {11: (F(215, 11), F(460, 11)), 12: (F(25), F(53))}
_old = print
def run2(NEW, base, Ps):
    run(NEW, base, Ps)
    ok = True
    for P in Ps:
        a, b = avg(P, base, P, NEW), avg(P, base, 2 * P, NEW)
        hit = (a, b) == REC[P]
        print('recorded match', P, hit, a, b)
        ok = ok and hit
    print('RESULT:', 'PASS' if ok else 'FAIL', 'recorded first-cover fractions reproduced by gap walk at base', base)
run2(cov_new, 9203, [11, 12])
