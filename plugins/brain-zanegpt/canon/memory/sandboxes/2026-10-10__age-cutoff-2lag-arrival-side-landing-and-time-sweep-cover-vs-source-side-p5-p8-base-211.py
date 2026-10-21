"""Prediction (before run): rewriting the landing predicate from the ARRIVAL side (for each arrival tick x, ask
whether source x-L qualifies) gives exactly the same landing sets as the source-side form, and a time-sweep cover
(walk ticks, track the latest lag to land a new tick) reproduces the recorded 2-lag totals at N=2P of 26, 51, 88, 144
for P5..P8 at base 211 with flats exactly at N=P and N=2P. Built to break: a landing rule with the closed-target
clause dropped must give different totals. Stdlib, deterministic, no RNG."""
from fractions import Fraction as F

def lands_src(P, T, w, L):
    return {t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w}

def lands_arr(P, T, w, L, closed_clause=True):
    out = set()
    for x in range(L, T + L):
        t = x - L
        if (t % P) >= w or (closed_clause and (x % P) < w):
            out.add(x)
    return out

def cnt_sweep(P, T, N, lands):
    sh = 0
    for w in range(1, P):
        ev = {L: lands(P, T, w, L) for L in range(1, N + 1)}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                seen = set(); cut = 0; last = 0
                for x in range(T + N + 2):
                    for L in (a, b):
                        if x in ev[L]:
                            if x not in seen: cut = L
                            seen.add(x); last = L if L == b or last == 0 else last
                # last = b if b has events else a
                last = b if ev[b] else (a if ev[a] else 0)
                sh += (last != cut)
    return sh

ok = True; out = []; rec = {5: 26, 6: 51, 7: 88, 8: 144}
same_sets = all(lands_src(P, 211 + r, w, L) == lands_arr(P, 211 + r, w, L)
                for P in range(5, 9) for r in range(P) for w in range(1, P) for L in range(1, 2 * P + 1))
print("landing sets identical source-side vs arrival-side:", same_sets)
ok &= same_sets
for P in range(5, 9):
    Ns = list(range(P - 1, 2 * P + 2))
    tot = {N: sum(cnt_sweep(P, 211 + r, N, lands_arr) for r in range(P)) for N in Ns}
    A = {N: F(tot[N], P) for N in Ns}
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    bad = sum(cnt_sweep(P, 211 + r, 2 * P, lambda p, t, w, L: lands_arr(p, t, w, L, False)) for r in range(P))
    print(P, "flats", flats, "tot2P", tot[2 * P], "recorded", rec[P], "noClosedClause", bad, flush=True)
    ok = ok and flats == [P, 2 * P] and tot[2 * P] == rec[P] and bad != tot[2 * P]
    out.append(f"P{P} flats={flats} tot2P={tot[2*P]} noClause={bad}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
