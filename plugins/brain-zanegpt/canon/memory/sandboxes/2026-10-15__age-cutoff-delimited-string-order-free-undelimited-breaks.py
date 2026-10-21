"""Prediction (before run): at offset 4801 for P8 and P9, the comma-delimited-string substring cover (base-3359 entry) equals the
first-cover dict (base-4801 entry) at N in {P-1,P,2P-1,2P} AND stays equal when both landing lists are REVERSED (substring membership is order-free,
unlike the heap cover), flats at N=P and 2P. Built to BREAK: an UNDELIMITED substring cover must differ from the dict at small offsets (base 0,
where 5 matches inside 15) -- predicted to differ at base 0 for both moduli; at base 4801 it may or may not differ (unknown). Deterministic, stdlib only."""
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cut(vb, va, cov):
    return ('a' if va else 0) if cov(vb, va) else 'b'
def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_delim(b, a):
    s = "," + ",".join(map(str, a)) + ","; return all(("," + str(x) + ",") in s for x in b)
def cov_undelim(b, a):
    s = "".join(map(str, a)); return all(str(x) in s for x in b)
COVS = (("dict", cov_dict), ("delim", cov_delim), ("undelim", cov_undelim))

def count(P, T, N, rev):
    sh = {n: 0 for n, _ in COVS}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = 'b' if V[b] else ('a' if V[a] else 0)
                vb, va = (V[b][::-1], V[a][::-1]) if rev else (V[b], V[a])
                for n, c in COVS:
                    sh[n] += last != cut(vb, va, c)
    return sh

def avg(P, base, N, rev=False):
    tot = {n: 0 for n, _ in COVS}
    for r in range(P):
        for k, v in count(P, base + r, N, rev).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (8, 9):
    Ns = (P - 1, P, 2 * P - 1, 2 * P)
    A = {N: avg(P, 4801, N) for N in Ns}
    R = {N: avg(P, 4801, N, True) for N in Ns}
    agree = all(v["dict"] == v["delim"] for v in A.values())
    rev_ok = all(R[N]["delim"] == A[N]["delim"] for N in Ns)
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    u4801 = any(A[N]["undelim"] != A[N]["dict"] for N in Ns)
    B = {N: avg(P, 0, N) for N in (P, 2 * P)}
    u0 = any(B[N]["undelim"] != B[N]["dict"] for N in B)
    print(P, flats, agree, rev_ok, u4801, u0, flush=True)
    ok = ok and agree and rev_ok and flats == [P, 2 * P] and u0
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} delim_eq_dict={agree} delim_reversal_stable={rev_ok} undelim_differs_base4801={u4801} undelim_differs_base0={u0}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
