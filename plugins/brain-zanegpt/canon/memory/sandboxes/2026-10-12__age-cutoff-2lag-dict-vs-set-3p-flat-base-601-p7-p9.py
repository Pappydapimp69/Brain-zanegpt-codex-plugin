"""Prediction (before run): at base 601 the dict and set-inclusion cover rules give identical cumulative period-average
curves over N=1..3P+2 for P7, P8, P9; each curve is flat at N=P and N=2P (as for P15-P17) AND ALSO at N=3P, the flat
earlier P5/P6 runs saw, with no other flat in 2..3P+2. Built to break: if 3P is a small-P artefact, P9 shows no 3P flat."""
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

def cut_set(sa, sb, a, b):
    return (a if sa else 0) if sb <= sa else b

def cut_sloppy(ea, eb, a, b):
    return b if len(eb) > len(ea) else (a if ea else 0)

def by_b(P, T, NMAX):
    out = {k: [0] * (NMAX + 1) for k in ("dict", "set", "sloppy")}
    for w in range(1, P):
        V = [None] + [lands(P, T, w, L) for L in range(1, NMAX + 1)]
        S = [None] + [set(v) for v in V[1:]]
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
for P in (7, 8, 9):
    cur = curves(P, 601, 3 * P + 2)
    d, s, z = cur["dict"], cur["set"], cur["sloppy"]
    agree = d == s
    flat = [N for N in range(2, 3 * P + 3) if d[N] == d[N - 1]]
    print(P, "agree", agree, "flats", flat, "sloppy differs", z != d, flush=True)
    ok = ok and agree and flat == [P, 2 * P, 3 * P] and z != d
    out.append(f"P{P} agree={agree} flats={flat}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
