def run(P, W, N, off):
    S = lambda t: (t + off) % P < W
    lags = range(1, P)
    one = {L: sum(1 for t in range(N) if S(t) and not S(t + L)) for L in lags}
    rev = {L: sum(1 for t in range(N) if (not S(t)) and S(t + L)) for L in lags}
    val = {L: sum(1 for t in range(N) if S(t) and S(t + L)) for L in lags}
    m = {L: min(L, W, P - L, P - W) for L in lags}
    lossless = max(L for L in lags if val[L] > 0)
    cum = lambda c: sum(one[L] for L in lags if L <= c)
    return one, rev, m, lossless, cum
viol_bound = 0; exact_two_N_mult = 0; diffs = []; cum_ok = True; cells = 0
for P, W in ((10, 3), (12, 5), (15, 7), (9, 4)):
    for N in (600, 601, 607, 613, 625, 640):
        for off in (0, 2, 5):
            one, rev, m, lossless, cum = run(P, W, N, off)
            for L in one:
                cells += 1
                if abs(one[L] - (N / P) * m[L]) > m[L]: viol_bound += 1
                d = (one[L] + rev[L]) - 2 * one[L]
                diffs.append((N % P == 0 and True, abs(d)))
            if max(cum(c) for c in range(0, P)) != cum(lossless): cum_ok = False
mult = [d for f, d in diffs if f]; nonmult = [d for f, d in diffs if not f]
print("cells", cells, "bound violations", viol_bound, "max |rev-one| when N%P==0:", max(mult) if mult else None,
      "max when N%P!=0:", max(nonmult), "nonzero count", sum(1 for d in nonmult if d))
ok = viol_bound == 0 and cum_ok and max(nonmult) > 0 and (max(mult) if mult else 0) <= max(nonmult)
print("RESULT: %s %d cells: |one-sided - (N/P)*min| <= min everywhere (violations %d); rev-vs-one gap up to %d at N%%P!=0 vs %s at N multiple of P; max cumulative at lossless cutoff %s"
      % ("PASS" if ok else "FAIL", cells, viol_bound, max(nonmult), max(mult) if mult else 0, cum_ok))
