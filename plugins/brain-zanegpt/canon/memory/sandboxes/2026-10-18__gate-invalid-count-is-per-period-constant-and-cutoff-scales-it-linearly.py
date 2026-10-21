# Sandbox: composes (1) lossless-cutoff-is-worst-without-validity: per-lag gate-only
# invalid count = (N/P)*min(L,W,P-L,P-W); (2) one-sided formula (N/P)*lag below
# threshold; (3) age-cutoff roll-up: counts are flat/periodic at every multiple of P
# once the horizon base is a few periods above 0 (base 0 breaks it).
# Legal(t) = t mod P < W. A hint issued at t-L naming B is invalid at use t iff
# legal(t-L) and not legal(t).
P, W = 12, 5

def invalid(L, N, base):
    return sum(1 for t in range(base, base + N)
               if ((t - L) % P) < W and (t % P) >= W)

def formula(L, N):
    return (N // P) * min(L, W, P - L, P - W)

# Prediction (before run): for every lag 1..P-1 and N = kP (k=1..4) at base 3P the
# count equals formula exactly (0 mismatches over 44 cells), so invalid/N is the same
# at every k (flat per period); at N = kP+3 the formula fails in at least one cell
# (BREAK); and the summed gate-only invalid over lags <= cutoff c is nondecreasing in c.
mism = 0
cells = 0
for k in range(1, 5):
    for L in range(1, P):
        cells += 1
        if invalid(L, k * P, 3 * P) != formula(L, k * P):
            mism += 1
rates = {k: [invalid(L, k * P, 3 * P) / (k * P) for L in range(1, P)] for k in range(1, 5)}
flat = all(rates[k] == rates[1] for k in rates)
brk = sum(1 for L in range(1, P) if invalid(L, 4 * P + 7, 3 * P) != formula(L, 4 * P + 7))
base0 = sum(1 for L in range(1, P) if invalid(L, P, 0) != formula(L, P))
cum, c_tot = 0, []
for c in range(1, P):
    cum += invalid(c, 4 * P, 3 * P)
    c_tot.append(cum)
mono = all(a <= b for a, b in zip(c_tot, c_tot[1:]))
print("cells=%d mismatches=%d flat_rate=%s break_nonmultiple_mismatch_lags=%d base0_mismatch_lags=%d" % (cells, mism, flat, brk, base0))
print("cumulative invalid by cutoff 1..%d: %s" % (P - 1, c_tot))
# Iteration 1 refuted the N=kP+3 break (extra ticks were all legal, phase luck) and showed
# base 0 does not break this count; iteration 2 uses an N=kP+7 tail that contains illegal ticks.
ok = mism == 0 and flat and brk > 0 and mono and base0 == 0
print("RESULT: %s formula exact at N=kP (%d/%d cells), per-period rate flat across k=1..4, N=kP+7 breaks %d of %d lags, base 0 breaks %d lags, cumulative invalid monotone in cutoff"
      % ("PASS" if ok else "FAIL", cells - mism, cells, brk, P - 1, base0))
