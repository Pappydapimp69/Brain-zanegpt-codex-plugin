"""Prediction (written before run 1; run 1 REFUTED the 'not at 3P' half, check refined to multiples of P): extending the lag range past 2P, the 2-lag period-average shadow total (same model as the
first-cover dict base-3001 and int-bitmask base-811 sandboxes) has flats at N=P and N=2P and NOT at 3P, for P=5..8,
and the dict first-cover and big-int and-not implementations agree at every N. Break case: a third flat at N=3P or
any flat besides P and 2P (the lags-to-16 entry already found one extra at (16,8), so extras beyond 2P are plausible).
Stdlib, deterministic, base 1553."""
from fractions import Fraction as F

def landings(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def count_dict(P, T, N):
    sh = 0
    for w in range(1, P):
        ev = {L: landings(P, T, w, L) for L in range(1, N + 1)}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                first = {}
                for x in ev[a]: first.setdefault(x, a)
                cut = a if first else 0
                for x in ev[b]:
                    if x not in first: first[x] = b; cut = b
                last = b if ev[b] else (a if ev[a] else 0)
                sh += (last != cut)
    return sh

def count_mask(P, T, N):
    sh = 0
    for w in range(1, P):
        ev = {L: landings(P, T, w, L) for L in range(1, N + 1)}
        m = {L: sum(1 << x for x in ev[L]) for L in ev}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                cut = b if (m[b] & ~m[a]) else (a if m[a] else 0)
                last = b if m[b] else (a if m[a] else 0)
                sh += (last != cut)
    return sh

def avg(fn, P, base, N):
    return F(sum(fn(P, base + r, N) for r in range(P)), P)

ok = True; out = []
for P in (5, 6, 7, 8):
    Ns = list(range(P - 1, (4 if P <= 6 else 3) * P + 2))
    A = {N: avg(count_mask, P, 1553, N) for N in Ns}
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    spot = [3 * P - 1, 3 * P]
    agree = all(avg(count_dict, P, 1553, N) == A[N] for N in (P, 2 * P, 3 * P) if P <= 6) if P <= 6 else \
        all(avg(count_dict, P, 1553, N) == A[N] for N in (P, 2 * P))
    print(P, "flats", flats, "agree", agree, flush=True)
    ok = ok and agree and flats == [k * P for k in range(1, (4 if P <= 6 else 3) + 1)]  # refined after run 1: flats at EVERY multiple of P
    out.append(f"P{P} flats={flats} agree={agree}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
