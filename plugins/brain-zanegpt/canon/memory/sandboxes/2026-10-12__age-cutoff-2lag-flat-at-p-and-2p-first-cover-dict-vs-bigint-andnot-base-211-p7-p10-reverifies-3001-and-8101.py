"""Prediction (before run): at new base 211 the first-cover dictionary rule and a Python big-integer and-not rule (a bit per landing tick,
b adds coverage iff mb & ~ma != 0, standing in for the recorded Ruby Bignum rule) give identical period-average shadow counts for P7 and P10
at N in {P-1,P,2P-1,2P,2P+1}, both flat exactly at N=P and N=2P and not at 2P+1. P7 and P10 were run by neither source entry for these
two rules together. Built to break: the base-0 control must differ at N=P; an and-rule that forgets the complement (mb & ma != 0) must differ."""
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

def tomask(e):
    m = 0
    for x in e: m |= 1 << x
    return m

def cut_andnot(ea, eb, a, b):
    ma, mb = tomask(ea), tomask(eb)
    return b if mb & ~ma else (a if ma else 0)

def cut_wrong(ea, eb, a, b):
    ma, mb = tomask(ea), tomask(eb)
    return b if mb & ma else (a if ma else 0)

RULES = {"dict": cut_dict, "andnot": cut_andnot, "wrong": cut_wrong}

def avg(P, base, N):
    tot = dict.fromkeys(RULES, 0)
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = {L: lands(P, T, w, L) for L in range(1, N + 1)}
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    for k, f in RULES.items():
                        tot[k] += last != f(V[a], V[b], a, b)
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
for P in (7, 10):
    Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
    A = {N: avg(P, 211, N) for N in Ns}
    same = all(v["dict"] == v["andnot"] for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    nop1 = A[2 * P + 1]["dict"] != A[2 * P]["dict"]
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    wrong = any(v["wrong"] != v["dict"] for v in A.values())
    print(P, {N: str(A[N]["dict"]) for N in Ns}, same, flats, nop1, ctrl, wrong, flush=True)
    ok = ok and same and flats == [P, 2 * P] and nop1 and ctrl and wrong
    out.append(f"P{P} agree={same} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} ctrl_differs={ctrl} wrong_rule_differs={wrong}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
