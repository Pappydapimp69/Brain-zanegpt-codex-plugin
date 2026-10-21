"""Prediction (before run): at fresh base 1409, P in 5 and 6, the first-cover streaming implementation and the symdiff, reduce and
tuple-index cover predicates all equal the dict reference at N in {P-1,P,2P-1,2P,2P+1}; averages are flat exactly at N=P and 2P
(P5: 2 and 26/5; P6: 7/2 and 17/2, as recorded at base 307). Built to break: a mutant cover that tests set EQUALITY instead of
subset must differ from the reference at N=P (so the comparison can detect a wrong predicate), and the base-0 control must differ.
Also checks the symdiff predicate against the plain subset test on every lag pair, directly. Deterministic, stdlib only."""
from fractions import Fraction as F
from functools import reduce

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]
def cov_dict(b, a):
    D = dict.fromkeys(a); return all(x in D for x in b)
def cov_symdiff(b, a):
    return not (set(a) ^ set(b)) & set(b) - set(a) and not (set(b) - set(a))
def cov_reduce(b, a):
    return reduce(lambda acc, x: acc and (x in frozenset(a)), b, True)
def cov_tuple(b, a):
    ta = tuple(a)
    for x in b:
        if x not in ta: return False
    return True
def cov_equal_mutant(b, a): return set(a) == set(b)
def first_cover(Va, Vb, a, b):
    first = {}
    for x in Va: first.setdefault(x, a)
    cut = a if first else 0
    for x in Vb:
        if x not in first:
            first[x] = b; cut = b
    return cut
COVS = (("dict", cov_dict), ("symdiff", cov_symdiff), ("reduce", cov_reduce), ("tuple", cov_tuple), ("mutant", cov_equal_mutant))
def count(P, T, N, st):
    sh = {n: 0 for n, _ in COVS}; sh["first"] = 0
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for n, cov in COVS:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[n] += last != cut
                sh["first"] += last != first_cover(V[a], V[b], a, b)
                st["pairs"] += 1
                st["sym_dis"] += cov_symdiff(V[b], V[a]) != cov_dict(V[b], V[a])
    return sh
def avg(P, base, N, st):
    tot = {}
    for r in range(P):
        for k, v in count(P, base + r, N, st).items(): tot[k] = tot.get(k, 0) + v
    return {k: F(v, P) for k, v in tot.items()}
REC = {5: (F(2), F(26, 5)), 6: (F(7, 2), F(17, 2))}
ok = True; out = []; st = {"pairs": 0, "sym_dis": 0}
for P in (5, 6):
    A = {N: avg(P, 1409, N, st) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    impls = ("dict", "symdiff", "reduce", "tuple", "first")
    agree = all(len({A[N][k] for k in impls}) == 1 for N in A)
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    rec = (A[P]["dict"], A[2 * P]["dict"]) == REC[P]
    ctrl = avg(P, 0, P, st)["dict"] != A[P]["dict"]
    mut = A[P]["mutant"] != A[P]["dict"]
    print(P, agree, flats, rec, ctrl, mut, A[P]["dict"], A[2 * P]["dict"], A[P]["mutant"], flush=True)
    ok = ok and agree and flats == [P, 2 * P] and rec and ctrl and mut
    out.append("P%d agree=%s flats=%s avgP=%s avg2P=%s rec=%s ctrl=%s mutant_avgP=%s" % (P, agree, flats, A[P]["dict"], A[2 * P]["dict"], rec, ctrl, A[P]["mutant"]))
print("symdiff vs dict disagreements on %d lag pairs: %d" % (st["pairs"], st["sym_dis"]))
ok = ok and st["sym_dis"] == 0
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out), "; symdiff_disagree=%d/%d" % (st["sym_dis"], st["pairs"]))
