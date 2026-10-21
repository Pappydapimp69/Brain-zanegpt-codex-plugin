"""Prediction (before run): at base 1213 the two-pointer sorted-list subset rule (lag b covered when every landing of b
is also a landing of a, walked with two indices) and the first-cover dict rule give identical cumulative period-average
curves over N=1..2P+2 for P9, P10 and P11 (beyond the P8 limit of the two-pointer entry), flat exactly at N=P and N=2P
and nowhere else in 2..2P+2; a base-0 control differs at N=P; the sizes-only rule differs. Built to break: P9-P11 are
unseen by the two-pointer source entry, and a two-pointer off-by-one at list ends would show as a dict mismatch."""
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

def subset_2ptr(sb, sa):
    i = 0
    for x in sb:
        while i < len(sa) and sa[i] < x: i += 1
        if i == len(sa) or sa[i] != x: return False
        i += 1
    return True

def cut_set(sa, sb, a, b):
    return (a if sa else 0) if subset_2ptr(sb, sa) else b

def cut_sloppy(ea, eb, a, b):
    return b if len(eb) > len(ea) else (a if ea else 0)

def by_b(P, T, NMAX):
    out = {k: [0] * (NMAX + 1) for k in ("dict", "set", "sloppy")}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, NMAX + 1)]
        S = V
        for b in range(2, NMAX + 1):
            for a in range(1, b):
                last = b if V[b] else (a if V[a] else 0)
                out["dict"][b] += last != cut_dict(V[a], V[b], a, b)
                out["set"][b] += last != cut_set(S[a], S[b], a, b)
                out["sloppy"][b] += last != cut_sloppy(V[a], V[b], a, b)
    return out

def curves(P, base, NMAX):
    tot = {k: [0] * (NMAX + 1) for k in ("dict", "set", "sloppy")}
    for r in range(P):
        c = by_b(P, base + r, NMAX)
        for k in tot:
            for b in range(NMAX + 1): tot[k][b] += c[k][b]
    res = {}
    for k in tot:
        run, cum = 0, []
        for b in range(NMAX + 1):
            run += tot[k][b]; cum.append(F(run, P))
        res[k] = cum
    return res

ok = True; out = []
for P in (9, 10, 11):
    cur = curves(P, 1213, 2 * P + 2)
    d, s, z = cur["dict"], cur["set"], cur["sloppy"]
    agree = d == s
    flat = [N for N in range(2, 2 * P + 3) if d[N] == d[N - 1]]
    ctrl = curves(P, 0, P)["dict"][P] != d[P]
    print(P, "agree", agree, "flats", flat, "base0 differs", ctrl, "sloppy differs", z != d, flush=True)
    ok = ok and agree and flat == [P, 2 * P] and ctrl and z != d
    out.append(f"P{P} agree={agree} flats={flat}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
