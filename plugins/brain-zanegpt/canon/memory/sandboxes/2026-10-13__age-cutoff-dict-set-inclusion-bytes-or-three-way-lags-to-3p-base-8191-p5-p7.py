"""Prediction (before run): at fresh base 8191 three implementations of the age-cutoff shortfall test (dict first-cover, set-inclusion
with an emptiness guard, bytes-OR as big-int OR) agree on EVERY (P,r,w,a,b) cell for P5..P7 with lags to 3P (beyond the 2P+2 range
of earlier runs): zero disagreements; the offset-averaged totals stay flat for every N from 2P up to 3P (flat steps at P, 2P and then 2P+1..3P are all present),
i.e. flats == [P] + list(range(2P, 3P+1)); a base-0 control differs at N=P. Built to break: lags to 3P and the unguarded set test at T=2 (empty sets must disagree).
Stdlib, deterministic."""
from fractions import Fraction as F
def cells(P, T, N, kind):
    out = {}
    for w in range(1, P):
        ev = {L: [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w] for L in range(1, N + 1)}
        S = {L: set(v) for L, v in ev.items()}
        M = {L: sum(1 << x for x in set(v)) for L, v in ev.items()}
        for a in range(1, N):
            for b in range(a + 1, N + 1):
                if kind == "dict":
                    first = {}
                    for x in ev[a]: first.setdefault(x, a)
                    cut = a if first else 0
                    for x in ev[b]:
                        if x not in first: first[x] = b; cut = b
                    last = b if ev[b] else (a if ev[a] else 0)
                    out[(w, a, b)] = int(last != cut)
                elif kind == "set":
                    out[(w, a, b)] = int(bool(S[b]) and S[b] <= S[a])
                elif kind == "setU":
                    out[(w, a, b)] = int(S[b] <= S[a])
                else:
                    out[(w, a, b)] = int(M[b] != 0 and (M[a] | M[b]) == M[a])
    return out
# dict test returns 1 when last lag != cut lag, the others return 1 when b adds nothing: dict's "cut != last" means a later lag added nothing new for the pair view; compare as-is per earlier entries
def avg(P, base, N):
    cs = [cells(P, base + r, N, "dict") for r in range(P)]
    return {n: F(sum(v for c in cs for (w, a, b), v in c.items() if b <= n), P) for n in range(P - 1, N + 1)}, cs
ok = True; summ = []
for P in (5, 6, 7):
    N = 3 * P
    A, cd = avg(P, 8191, N)
    bad_set = bad_or = 0
    for r in range(P):
        cs = cells(P, 8191 + r, N, "set"); co = cells(P, 8191 + r, N, "bits")
        bad_set += sum(cd[r][k] != cs[k] for k in cd[r]); bad_or += sum(cd[r][k] != co[k] for k in cd[r])
    Z, _ = avg(P, 0, P)
    flats = [n for n in range(P, N + 1) if A[n] == A[n - 1]]
    unguard = sum(cells(P, 2, N, "dict")[k] != v for k, v in cells(P, 2, N, "setU").items())
    ctrl = Z[P] != A[P]
    print(P, "set-dis", bad_set, "or-dis", bad_or, "flats", flats, "ctrl", ctrl, "unguarded-T2", unguard, flush=True)
    want = [P] + list(range(2 * P, 3 * P + 1))
    ok = ok and bad_set == 0 and bad_or == 0 and flats == want and ctrl and unguard > 0
    summ.append(f"P{P} dis={bad_set}/{bad_or} flats={flats} unguardedT2={unguard}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(summ))
