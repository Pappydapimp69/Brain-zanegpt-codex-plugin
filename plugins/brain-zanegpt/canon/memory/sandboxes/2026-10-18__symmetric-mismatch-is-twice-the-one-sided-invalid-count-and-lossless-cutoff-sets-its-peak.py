# Composes: age-cutoff-lossless-threshold-exceeds-period-p12 (lossless cutoff = largest valid lag),
# lossless-cutoff-is-worst-without-validity (gate-only invalid = (N/P)*min(L,W,P-L,P-W)),
# sandbox-symmetric-and-one-sided-agreement-share-min-term (symmetric and one-sided counts
# share the min term). Legal(t) = t mod P < W. over N = kP ticks.
# one-sided invalid(L): legal at t, illegal at t+L. symmetric mismatch(L): legality differs.
# Prediction (before run): for P in {10,12,15}, every W in 2..P-2 (including W > P/2) and every
# L in 1..P-1, symmetric = 2 * one-sided exactly and one-sided = (N/P)*min(L,W,P-L,P-W)
# (0 mismatches over all cells); BREAK: a lag L>=P with L mod P = r gives the value for r, and
# L a multiple of P gives 0, so a cutoff derived from the period's min term fails above P.
def one(P, W, L, N):
    return sum(1 for t in range(N) if (t % P) < W and not ((t + L) % P) < W)
def sym(P, W, L, N):
    return sum(1 for t in range(N) if ((t % P) < W) != (((t + L) % P) < W))
cells = bad_sym = bad_formula = 0
for P in (10, 12, 15):
    N = 8 * P
    for W in range(2, P - 1):
        for L in range(1, P):
            cells += 1
            o, s = one(P, W, L, N), sym(P, W, L, N)
            if s != 2 * o: bad_sym += 1
            if o != (N // P) * min(L, W, P - L, P - W): bad_formula += 1
P, W, N = 12, 5, 96
over = [(L, one(P, W, L, N), one(P, W, L % P, N)) for L in (13, 14, 20, 24, 25, 36)]
over_ok = all(a == b for _, a, b in over)
zero_ok = one(P, W, 24, N) == 0 and one(P, W, 36, N) == 0
print("cells=%d symmetric!=2*one-sided in %d, formula mismatches %d" % (cells, bad_sym, bad_formula))
print("lags above period (L, value, value at L mod P):", over)
ok = bad_sym == 0 and bad_formula == 0 and over_ok and zero_ok
print("RESULT: %s symmetric = 2 x one-sided and formula exact in %d cells (P 10/12/15, all W 2..P-2, L 1..P-1, incl. W>P/2); lags above the period repeat L mod P, multiples of P give 0"
      % ("PASS" if ok else "FAIL", cells - bad_sym - bad_formula if bad_sym == bad_formula else cells))
