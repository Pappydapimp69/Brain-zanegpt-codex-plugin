"""Prediction (before run): three cover implementations (dict, shared-iterator two-pointer, int bitmask) run at FRESH offset 503 reproduce the values recorded
at other offsets by two earlier entries: P7 38/7 & 88/7, P10 15 & 65/2 (offset 709), P11 215/11 & 460/11 (offset 3001), i.e. averages are offset-independent;
flats exactly at N=P and N=2P. Built to break: base-0 control must differ at N=P; an any-instead-of-all cover must differ. Deterministic, stdlib only."""
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)

def cov_two_pointer(b, a):
    it = iter(a); return all(any(y == x for y in it) for x in b)

def cov_bitmask(b, a):
    ma = 0
    for x in a: ma |= 1 << x
    mb = 0
    for x in b: mb |= 1 << x
    return mb & ~ma == 0

def cov_any(b, a):
    D = dict.fromkeys(a); return any(x in D for x in b)

IMPLS = (("dict", cov_dict), ("two_pointer", cov_two_pointer), ("bitmask", cov_bitmask), ("any_bug", cov_any))

def count(P, T, N):
    sh = {n: 0 for n, _ in IMPLS}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for name, cov in IMPLS:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[name] += last != cut
    return sh

def avg(P, base, N):
    tot = {n: 0 for n, _ in IMPLS}
    for r in range(P):
        for k, v in count(P, base + r, N).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

RECORDED = {7: (F(38, 7), F(88, 7)), 10: (F(15), F(65, 2)), 11: (F(215, 11), F(460, 11))}
ok = True; out = []
for P, (rp, r2) in RECORDED.items():
    A = {N: avg(P, 503, N) for N in (P - 1, P, 2 * P)}
    agree = all(A[N]["dict"] == A[N]["two_pointer"] == A[N]["bitmask"] for N in A)
    matches = A[P]["dict"] == rp and A[2 * P]["dict"] == r2
    flats = [N for N in (P, 2 * P) if N == P and A[P]["dict"] == A[P - 1]["dict"]]
    flat2 = A[2 * P]["dict"] == avg(P, 503, 2 * P - 1)["dict"]
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    anyd = A[P]["any_bug"] != A[P]["dict"]
    ok = ok and agree and matches and flats == [P] and flat2 and ctrl and anyd
    out.append(f"P{P} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} recorded_match={matches} impls_agree={agree} flatP={bool(flats)} flat2P={flat2} ctrl_differs={ctrl} any_bug_differs={anyd}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
