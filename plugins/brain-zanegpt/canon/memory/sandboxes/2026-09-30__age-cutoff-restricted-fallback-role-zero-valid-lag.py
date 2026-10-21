# Prediction (written before first run): P12 wave, N=600 ticks, no RNG. Role B available when t%12<4.
# Hint = B if B available at t else A. Press at t+L legal if the hinted role is available at t+L.
# Earlier sandboxes kept role A always available, so the lossless cutoff equalled the largest lag in the set by
# construction. Here role A is restricted. Predict: (1) lossless cutoff == largest lag with a valid press in every
# case (4 cases with periodic A, where I expect max lag == max valid lag); (2) in a breaker with A never available
# and lags {1,6,7} (lags 6 and 7 never land in the B window) the lossless cutoff is 1 while max lag is 7;
# (3) a cutoff at the period 12 is lossy whenever the set holds a valid lag above 12.
P, N = 12, 600
def availB(t): return t % P < 4
def run(lags, cutoff, availA):
    valid = comb = 0
    for L in lags:
        for t in range(N):
            ok = availB(t + L) if availB(t) else availA(t + L)
            if ok:
                valid += 1
                if L <= cutoff: comb += 1
    return valid, comb
def lossless(lags, availA):
    tot = run(lags, 10**9, availA)[0]
    return min(c for c in range(0, 60) if run(lags, c, availA)[1] == tot)
def max_valid(lags, availA):
    best = 0
    for L in lags:
        if any((availB(t + L) if availB(t) else availA(t + L)) for t in range(N)): best = max(best, L)
    return best
A_always = lambda t: True
A_low6 = lambda t: t % P < 6
A_low4 = lambda t: t % P < 4
A_none = lambda t: False   # breaker: A never available -> only B-hint ticks can be legal
cases = [("always", A_always, [1, 3, 7, 20]),
         ("low6", A_low6, [2, 5, 9, 14]),
         ("low4", A_low4, [1, 6, 12, 18]),
         ("none", A_none, [1, 5, 12, 13]),
         ("none-break", A_none, [1, 6, 7])]
good = True; rows = []
for name, A, lags in cases:
    lc, mv, ml = lossless(lags, A), max_valid(lags, A), max(lags)
    tot = run(lags, 10**9, A)[0]; lost_period = tot - run(lags, P, A)[1]
    rows.append((name, lc, mv, ml, lost_period))
    print(name, lags, "lossless=%d max_valid=%d max_lag=%d lost_at_period=%d" % (lc, mv, ml, lost_period))
    good &= (lc == mv)
diff = [r for r in rows if r[1] != r[3]]
print("cases where max lag in set != lossless cutoff:", [r[0] for r in diff])
brk = [r for r in rows if r[0] == "none-break"][0]
good &= (brk[1] == 1 and brk[3] == 7)
print("RESULT: %s lossless cutoff == max VALID lag in all %d cases; max-lag-in-set wrong in %d (none-break: cutoff %d vs max lag %d), period cutoff lossy in %d"
      % ("PASS" if good else "FAIL", len(cases), len(diff), brk[1], brk[3], sum(1 for r in rows if r[4] > 0)))
