def sim(P, W, N, off, LMAX):
    S = lambda t: (t + off) % P < W
    one = [sum(1 for t in range(N) if S(t) and not S(t + L)) for L in range(1, LMAX + 1)]
    sym = [sum(1 for t in range(N) if S(t) != S(t + L)) for L in range(1, LMAX + 1)]
    val = [sum(1 for t in range(N) if S(t) and S(t + L)) for L in range(1, LMAX + 1)]
    return one, sym, val
bad_cum = bad_sym = bad_lossless = cells = 0
rows = []
for P, W in ((10, 3), (12, 5), (15, 7), (8, 2)):
    N, LMAX = 840, 4 * P + 3          # N multiple of P for P in (10? no) -> use N = lcm-friendly below
    N = 120 * P // P * 7 * P // 7      # 120*P ticks: always a whole number of periods
    off = 3
    one, sym, val = sim(P, W, N, off, LMAX)
    per = (N // P) * W * (P - W)      # predicted invalid added per full period of lags
    cum = [sum(one[:c]) for c in range(LMAX + 1)]
    for k in (1, 2, 3, 4):
        cells += 1
        if cum[k * P - 1] != k * per: bad_cum += 1
    cells += 1
    if any(sym[i] != 2 * one[i] for i in range(LMAX)): bad_sym += 1
    lossless = max(L for L in range(1, LMAX + 1) if val[L - 1] > 0)
    cells += 1
    pred = max(L for L in range(1, LMAX + 1) if L % P < W or L % P > P - W)   # residue overlaps the window
    if lossless != pred: bad_lossless += 1
    rows.append((P, W, per, cum[P - 1], cum[4 * P - 1], lossless))
    print("P%d W%d N%d: per-period gate-only invalid %d, cum(P-1)=%d cum(4P-1)=%d lossless=%d/%d" % (P, W, N, per, cum[P - 1], cum[4 * P - 1], lossless, LMAX))
ok = bad_cum == 0 and bad_sym == 0 and bad_lossless == 0
print("RESULT: %s %d cells: cumulative gate-only invalid equals k*(N/P)*W*(P-W) at cutoff k*P-1 (mismatches %d), symmetric is exactly twice one-sided (mismatches %d), lossless cutoff is the largest lag whose residue mod P is under W or over P-W (mismatches %d), so no plateau exists"
      % ("PASS" if ok else "FAIL", cells, bad_cum, bad_sym, bad_lossless))
