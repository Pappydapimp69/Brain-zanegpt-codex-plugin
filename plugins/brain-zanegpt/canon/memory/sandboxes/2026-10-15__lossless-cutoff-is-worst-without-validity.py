"""Compose: (1) age-cutoff-lossless-threshold-exceeds-period-p12/E1 - an age cutoff
stacked on a validity check is lossless exactly at the largest lag with a valid
press; (2) sandbox-one-sided-formula-explains-gate-invalid-counts/E1 - an age gate
WITHOUT validity executes (N/P)*lag invalid presses for one-sided legality (scope
lag <= min(W, P-W) per its rebuild). Composed claim: the same cutoff c has opposite
costs under the two policies: with validity, raising c to the largest valid lag
costs nothing; without it, every lag admitted below c adds its invalid presses, so
the 'lossless' cutoff is the WORST cutoff for a gate that skips validity.
Model: legal(t) = t mod P < W (role B available). A hint issued at t-L names B if B
was available then, else A (always legal). Used at t: invalid iff it names B and B
is unavailable at t (one-sided). Each lag L in the set gets its own N-use stream.
Deterministic, no RNG.
PREDICTION (written before running): for P=10, W=3, N=600, lags {1,2,4,6,9}:
combined policy lossless first at c = 9 (largest valid lag); gate-only invalid count
rises monotonically with c and equals sum (N/P)*min(L, W) over admitted lags for
L <= P-W = 7, but the formula is off for L = 9 (beyond P-W)."""
P, W, N = 10, 3, 600
LAGS = [1, 2, 4, 6, 9]
legal = lambda t: t % P < W
def stream(L):
    inv = val = 0
    for t in range(L, L + N):
        names_b = legal(t - L)
        bad = names_b and not legal(t)
        inv += bad; val += not bad
    return inv, val
per = {L: stream(L) for L in LAGS}
max_valid_lag = max(L for L in LAGS if per[L][1] > 0)
rows = []
for c in range(0, 11):
    lost = sum(per[L][1] for L in LAGS if L > c)                 # combined vs validity alone
    gate_inv = sum(per[L][0] for L in LAGS if L <= c)            # gate-only: execute if L <= c
    rows.append((c, lost, gate_inv))
    print(f"cutoff {c:2d}: validity+cutoff loses {lost:4d} valid presses | gate-only executes {gate_inv:4d} invalid")
lossless = min(c for c, lost, _ in rows if lost == 0)
mono = all(rows[i][2] <= rows[i + 1][2] for i in range(len(rows) - 1))
formula = {L: (N // P) * min(L, W) for L in LAGS}
match = {L: per[L][0] == formula[L] for L in LAGS}
print("per-lag invalid:", {L: per[L][0] for L in LAGS}, " formula (N/P)*min(L,W):", formula)
# iteration 2: candidate closed form for any lag below the period, checked on every
# L in 1..P-1 for three (P, W) shapes, not just the lag set above
def inv_count(P_, W_, L):
    return sum((t - L) % P_ < W_ and not t % P_ < W_ for t in range(L, L + 60 * P_))
refined_ok = all(inv_count(P_, W_, L) == 60 * min(L, W_, P_ - L, P_ - W_)
                 for P_, W_ in ((10, 3), (12, 5), (15, 7)) for L in range(1, P_))
print("refined (N/P)*min(L, W, P-L, P-W) matches every lag 1..P-1 on P10W3, P12W5, P15W7:", refined_ok)
worst = max(r[2] for r in rows)
gate_at_lossless = dict((c, g) for c, _, g in rows)[lossless]
ok = (lossless == max_valid_lag == 9 and mono and gate_at_lossless == worst
      and all(match[L] for L in LAGS if L <= P - W) and not match[9] and refined_ok)
print(f"RESULT: {'PASS' if ok else 'FAIL'} lossless cutoff {lossless} (max valid lag {max_valid_lag}) is the worst "
      f"gate-only cutoff ({gate_at_lossless} invalid = max {worst}); monotonic {mono}; formula matches "
      f"{[L for L in LAGS if match[L]]}, misses {[L for L in LAGS if not match[L]]}; refined min(L,W,P-L,P-W) exact on 3 shapes: {refined_ok}")
