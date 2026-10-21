"""Prediction (before run): at a fresh base 4007, the first-cover streaming implementation and four structurally different
cover predicates (dict, int-bitmask and-not, sorted-intersection, frozenset-le) all give identical 2-lag period-average
shadow counts for P in 8 and 11 at N in {P-1,P,2P-1,2P,2P+1}; averages are flat exactly at N=P and N=2P; P8 gives 8 and 18
(as recorded at 811) and P11 gives 215/11 and 460/11. Built to break: base-0 control must differ at N=P; an any-instead-of-all
cover rule must NOT reproduce the dict average. Deterministic, stdlib only."""
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_bits(b, a):
    A = 0
    for x in a: A |= 1 << x
    B = 0
    for x in b: B |= 1 << x
    return B & ~A == 0
def cov_sorted(b, a): return sorted(set(b) & set(a)) == sorted(set(b))
def cov_fs(b, a): return frozenset(b) <= frozenset(a)
def cov_any(b, a):
    D = dict.fromkeys(a); return any(x in D for x in b)
COVS = (("dict", cov_dict), ("bits", cov_bits), ("sorted", cov_sorted), ("fs", cov_fs))

def first_cover(Va, Vb, a, b):
    first = {}
    for x in Va: first.setdefault(x, a)
    cut = a if first else 0
    for x in Vb:
        if x not in first:
            first[x] = b; cut = b
    return cut

def count(P, T, N, extra=False):
    sh = {n: 0 for n, _ in COVS}; sh["first"] = 0; sh["any"] = 0
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for n, cov in COVS:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[n] += last != cut
                sh["first"] += last != first_cover(V[a], V[b], a, b)
                if extra:
                    cut = b if not cov_any(V[b], V[a]) else (a if V[a] else 0)
                    sh["any"] += last != cut
    return sh

def avg(P, base, N, extra=False):
    tot = {}
    for r in range(P):
        for k, v in count(P, base + r, N, extra).items():
            tot[k] = tot.get(k, 0) + v
    return {k: F(v, P) for k, v in tot.items()}

REC = {8: (F(8), F(18)), 11: (F(215, 11), F(460, 11))}
ok = True; out = []
for P in (8, 11):
    Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
    A = {N: avg(P, 4007, N, extra=(N == P)) for N in Ns}
    impls = ("dict", "bits", "sorted", "fs", "first")
    agree = all(len({A[N][k] for k in impls}) == 1 for N in Ns)
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    nonflat = [N for N in (2 * P + 1,) if A[N]["dict"] == A[N - 1]["dict"]]
    rec = A[P]["dict"] == REC[P][0] and A[2 * P]["dict"] == REC[P][1] if P in REC else True
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    anyr = A[P]["any"] != A[P]["dict"]
    print(P, agree, flats, nonflat, rec, ctrl, anyr, A[P]["dict"], A[2 * P]["dict"], A[P]["any"], flush=True)
    ok = ok and agree and flats == [P, 2 * P] and not nonflat and rec and ctrl and anyr
    out.append(f"P{P} agree={agree} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} rec_match={rec} ctrl_differs={ctrl} any_avgP={A[P]['any']}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
