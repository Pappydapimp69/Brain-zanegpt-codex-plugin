"""Prediction (before run): at base 811, P8: avg at N=8 is 8, N=16 is 18; P11: 215/11 at N=11, 460/11 at N=22;
all four covers equal the dict reference everywhere; flats at N=P and 2P; any-for-all gives 196 (P8) and 550 (P11) at N=P.
My own fixture: landing sets as frozensets built by direct per-tick simulation (not list comprehension of formula),
different N grid (P-2..2P+2), and extra control base 1."""
from fractions import Fraction as F

def landing_set(P, T, w, L):
    out = set()
    for t in range(T):
        issued = (t % P) >= w          # request issued outside the blocked window
        arrives_ok = ((t + L) % P) < w # or arrival lands inside the open window
        if issued or arrives_ok:
            out.add(t + L)
    return out

def c_dict(b, a):
    d = {x: 1 for x in a}
    return all(x in d for x in b)
def c_bitmask(b, a):
    mb = 0
    ma = 0
    for x in b: mb |= 1 << x
    for x in a: ma |= 1 << x
    return (mb & ~ma) == 0
def c_sorted_inter(b, a):
    sb, sa = sorted(b), sorted(a)
    i = j = 0; common = []
    while i < len(sb) and j < len(sa):
        if sb[i] == sa[j]: common.append(sb[i]); i += 1; j += 1
        elif sb[i] < sa[j]: i += 1
        else: j += 1
    return common == sb
def c_dictpop(b, a):
    d = {x: 1 for x in a}
    try:
        for x in b: d.pop(x, None) if x in d else (_ for _ in ()).throw(KeyError)
    except KeyError:
        return False
    return True
def c_fsle(b, a):
    return frozenset(b) <= frozenset(a)
def c_any(b, a):
    s = set(a); return any(x in s for x in b)

COVS = {"dict": c_dict, "bitmask": c_bitmask, "sortinter": c_sorted_inter, "dictpop": c_dictpop, "fsle": c_fsle, "any": c_any}

def avg(P, base, N):
    tot = {k: 0 for k in COVS}
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = {L: sorted(landing_set(P, T, w, L)) for L in range(1, N + 1)}
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    for k, c in COVS.items():
                        cut = b if not c(V[b], V[a]) else (a if V[a] else 0)
                        tot[k] += (last != cut)
    return {k: F(v, P) for k, v in tot.items()}

exp = {8: (F(8), F(18), F(196)), 11: (F(215, 11), F(460, 11), F(550))}
ok = True; out = []
for P in (8, 11):
    A = {N: avg(P, 811, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    real = ("dict", "bitmask", "sortinter", "dictpop", "fsle")
    agree = all(len({A[N][k] for k in real}) == 1 for N in A)
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 1, P)["dict"] != A[P]["dict"]
    eP, e2P, eAny = exp[P]
    match = A[P]["dict"] == eP and A[2 * P]["dict"] == e2P and A[P]["any"] == eAny
    ok = ok and agree and flats == [P, 2 * P] and ctrl and match
    out.append(f"P{P} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} any={A[P]['any']} agree={agree} flats={flats} ctrl1_differs={ctrl}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
