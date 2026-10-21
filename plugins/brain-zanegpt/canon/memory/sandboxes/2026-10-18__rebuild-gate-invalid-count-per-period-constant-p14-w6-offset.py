# Own fixture: P=14, W=6, phase offset 4 (legal(t) = (t+4) % 14 < 6), bases 0 and 5.
# Prediction (before running): at N=kP (k=1..3), both bases, lags 1..13, invalid == (N/P)*min(L,W,P-L,P-W)
# in all 78 cells; a partial tail N=kP+5 breaks the formula in >=1 lag; cumulative invalid by cutoff is nondecreasing.
P, W, OFF = 14, 6, 4
legal = lambda t: (t + OFF) % P < W
def inv(L, N, base): return sum(1 for t in range(base, base + N) if legal(t - L) and not legal(t))
def f(L, N): return (N // P) * min(L, W, P - L, P - W)
bad = cells = 0
for base in (0, 5):
    for k in (1, 2, 3):
        for L in range(1, P):
            cells += 1
            bad += inv(L, k * P, base) != f(L, k * P)
tail = sum(1 for L in range(1, P) if inv(L, 2 * P + 5, 5) != f(L, 2 * P + 5))
cum, run = [], 0
for c in range(1, P):
    run += inv(c, 3 * P, 5); cum.append(run)
mono = all(a <= b for a, b in zip(cum, cum[1:]))
print("cells", cells, "mismatches", bad, "tail-broken lags", tail, "cumulative", cum)
print("RESULT: %s %d/%d cells exact at N=kP on bases 0 and 5, tail kP+5 breaks %d of %d lags, cumulative monotone %s" % ("PASS" if bad == 0 and tail > 0 and mono else "FAIL", cells - bad, cells, tail, P - 1, mono))
