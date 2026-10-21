"""Own-fixture rebuild (bitmask arithmetic, bases 77 and 250, moduli 8..14, lag ranges 1..N, N 4..10).
Claim: the contiguous always-on 2-lag shadow count profile (keyed by T mod P) has minimal cyclic period
exactly P in all 49 cells and is identical across bases.
My reading of the model: window B(t) = t % P < w for each width w in 1..P-1; the landing set of lag L by
tick T is {t+L : t < T and (t not in B or t+L in B)}; for each unordered lag pair in 1..N, process lags in
order, cut = the last lag that added a new landing time, 'lg' = the largest lag with any landing; shadow
count increments when lg != cut; counts are summed over widths and pairs.
Prediction (before running): minimal period equals P in all 49 cells; profiles match across bases 77 and 250
(both written fresh); the hardest cell is N=4 at composite P (9, 10, 12, 14) where a divisor period could
appear, but none does. Own breaker: the same count with a lag set of multiples of 2 only at even P (expected
to shorten the period) to prove the period detector can fail."""
from itertools import combinations
def count(P, T, lags):
    tot = 0
    for w in range(1, P):
        B = 0
        for t in range(T + max(lags) + 1):
            if t % P < w: B |= 1 << t
        landing = {}
        for L in lags:
            m = 0
            for t in range(T):
                if not (B >> t) & 1 or (B >> (t + L)) & 1: m |= 1 << (t + L)
            landing[L] = m
        for a, b in combinations(lags, 2):
            cov = 0; cut = 0
            for L in (a, b):
                if landing[L] & ~cov: cut = L
                cov |= landing[L]
            lg = max((L for L in (a, b) if landing[L]), default=0)
            tot += lg != cut
    return tot
def profile(P, base, lags):
    return [count(P, base + ((r - base) % P), lags) for r in range(P)]   # entry r is T with T%P == r
def minimal_period(v):
    n = len(v)
    for d in range(1, n + 1):
        if n % d == 0 and all(v[i] == v[(i + d) % n] for i in range(n)): return d
cells = 0; per_ok = 0; base_ok = 0; bad = []
for N in range(4, 11):
    lags = list(range(1, N + 1))
    for P in range(8, 15):
        a = profile(P, 77, lags); b = profile(P, 250, lags)
        cells += 1
        mp = minimal_period(a)
        per_ok += mp == P
        base_ok += a == b
        if mp != P or a != b: bad.append((N, P, mp, a == b))
print(f"cells {cells}; minimal period == P in {per_ok}; profiles equal across bases in {base_ok}; exceptions {bad}")
# breaker: detector must fail on a period-d profile
fake = [1, 2, 3, 4] * 3
print("detector on a synthetic period-4 profile of length 12:", minimal_period(fake))
ev = [count(10, 300 + r, [2, 4, 6, 8, 10]) for r in range(10)]
print("even-lag-only set at P10 profile:", ev, "minimal period", minimal_period(ev))
ok = per_ok == cells and base_ok == cells and minimal_period(fake) == 4
print(f"RESULT: {'PASS' if ok else 'FAIL'} minimal period == P in {per_ok}/{cells} cells, base-invariant in {base_ok}/{cells}, detector finds period 4 on a fake, even-lag P10 period {minimal_period(ev)}")
