"""Prediction (before run): bisect, string, regex cover tests, run at offset 1117 for P in [7, 8], give period-average shadow counts IDENTICAL to a dict-membership
reference at N in {P-1, P, 2P-1, 2P, 2P+1}, with averages flat exactly at N=P and N=2P (avg[N]==avg[N-1]).
Built to break: base-0 control must differ at N=P; a buggy any-landing-covered rule (any instead of all) and a buggy off-by-one-lag cover (compares
shifted landings) must NOT reproduce the dict average at N=P. Deterministic, stdlib only."""
from fractions import Fraction as F
from bisect import bisect_left
import re

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cov_dict(b, a):
    D = dict.fromkeys(a)
    return all(x in D for x in b)

def cov_bisect(b, a):
    for x in b:
        i = bisect_left(a, x)
        if i == len(a) or a[i] != x: return False
    return True

def cov_string(b, a):
    s = "," + ",".join(map(str, a)) + ","
    return all(("," + str(x) + ",") in s for x in b)

def cov_regex(b, a):
    if not a: return not b
    rx = re.compile("^(?:" + "|".join(str(x) for x in a) + ")$")
    return all(rx.match(str(x)) for x in b)

COVS = (("dict", cov_dict), ("bisect", cov_bisect), ("string", cov_string), ("regex", cov_regex))
NAMES = [n for n, _ in COVS]

def count(P, T, N):
    sh = {n: 0 for n in NAMES}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, N + 1)]
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                for name, cov in COVS:
                    cut = b if not cov(V[b], V[a]) else (a if V[a] else 0)
                    sh[name] += last != cut
    return sh

def avg(P, base, N):
    tot = {n: 0 for n in NAMES}
    for r in range(P):
        for k, v in count(P, base + r, N).items():
            tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

def cov_any(b, a):
    D = dict.fromkeys(a)
    return any(x in D for x in b)

def cov_shift(b, a):
    D = dict.fromkeys(a)
    return all((x + 1) in D for x in b)

def bug_rule(P, base, N, cov):
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

ok = True; out = []
for P in [7, 8]:
    A = {N: avg(P, 1117, N) for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)}
    same = all(len(set(v.values())) == 1 for v in A.values())
    flats = [N for N in (P, 2 * P) if A[N]["dict"] == A[N - 1]["dict"]]
    ctrl = avg(P, 0, P)["dict"] != A[P]["dict"]
    anyr = bug_rule(P, 1117, P, cov_any)
    shr = bug_rule(P, 1117, P, cov_shift)
    print(P, flats, same, ctrl, anyr, shr, flush=True)
    ok = ok and same and flats == [P, 2 * P] and ctrl and anyr != A[P]['dict'] and shr != A[P]['dict']
    out.append(f"P{P} flats={flats} avgP={A[P]['dict']} avg2P={A[2*P]['dict']} impls_agree={same} ctrl_differs={ctrl} any_rule_avgP={anyr} shift_rule_avgP={shr}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
