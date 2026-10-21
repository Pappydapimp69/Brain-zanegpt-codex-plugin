# Rebuild of: agreement (symmetric mismatch) loss = 2*(N/P)*m and one-sided loss = (N/P)*m, m = min(lag,W,P-W,P-lag).
# Own fixture: sweep every lag 0..P and every W 1..P-1 for P in {8, 11, 16}, N = 4*P*? chosen as a multiple of P,
# plus a BREAK sweep with lag in (P, 2P] using the formula as written (no reduction mod P).
def legal(t, P, W): return ((t * 1 + 5) % P) < W
def losses(N, P, W, lag):
    sym = sum(1 for t in range(N) if legal(t, P, W) != legal(t + lag, P, W))
    one = sum(1 for t in range(N) if legal(t, P, W) and not legal(t + lag, P, W))
    return sym, one
ok = True; n = 0; bad = []
for P in (8, 11, 16):
    N = 60 * P
    for W in range(1, P):
        for lag in range(0, P + 1):
            m = min(lag, W, P - W, P - lag); sym, one = losses(N, P, W, lag); n += 1
            if not (sym == 2 * (N // P) * m and one == (N // P) * m): ok = False; bad.append((P, W, lag, sym, one, m))
brk_fail = 0; brk_n = 0
for P in (8, 11):
    N = 60 * P
    for W in range(1, P):
        for lag in range(P + 1, 2 * P + 1):
            m = min(lag, W, P - W, P - lag); sym, one = losses(N, P, W, lag); brk_n += 1
            if sym != 2 * (N // P) * m: brk_fail += 1
print("in-scope cases", n, "mismatches", len(bad), bad[:3])
print("break sweep lag in (P,2P]:", brk_fail, "of", brk_n, "disagree with formula as written (P-lag goes negative)")
print("RESULT: %s sym=2*(N/P)*m and one-sided=(N/P)*m on all %d (P,W,lag) with 0<=lag<=P; formula as written fails %d/%d for lag>P unless lag is reduced mod P" % ("PASS" if ok else "FAIL", n, brk_fail, brk_n))
