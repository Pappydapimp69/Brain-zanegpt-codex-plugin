# Sandbox: brute-force simulation of validity (press at tick t, source at t-L, both must land in active window)
# vs closed form for contiguous window dropping the period lag. Deterministic, stdlib only.
def valid_bf(P, w, L):
    return any((t % P) < w and ((t - L) % P) < w for t in range(3 * P + L + 1) if t >= L)
def cutoff_bf(P, w, lags):
    v = [L for L in lags if valid_bf(P, w, L)]
    return max(v) if v else 0
def closed(P, w, lags):
    # predicted: if 2w-1>=P every lag valid -> max lag; else largest lag with (L mod P) <= w-1 or >= P-(w-1)
    v = [L for L in lags if (L % P) <= w - 1 or (L % P) >= P - (w - 1)]
    return max(v) if v else 0
mis = 0; n = 0; allvalid = 0; dropP_ok = 0; dropP_n = 0
for P in range(2, 13):
    for w in range(1, P + 1):
        lags = [L for L in range(1, P + 1) if L != P]          # scenario 1: drop period lag
        exp = 0 if (w == 1) else P - 1
        if P == 1: continue
        dropP_n += 1; dropP_ok += (cutoff_bf(P, w, lags) == exp)
        for lagset in (lags, list(range(1, P + 1)), [L for L in range(1, 3 * P + 1) if L % P],  # scenario 2: full set; 3: multiples-of-P dropped, up to 3P
                       [L for L in range(1, P + 1) if L % 2 == 1 and L != P]):                   # scenario 4: sparse odd lags
            n += 1
            b, c = cutoff_bf(P, w, lagset), closed(P, w, lagset)
            mis += (b != c)
            if 2 * w - 1 >= P and lagset and b != max(lagset): mis += 1; allvalid += 1
print(f"cases={n} mismatches={mis} dropP_formula_ok={dropP_ok}/{dropP_n}")
print(f"RESULT: {'PASS' if mis == 0 and dropP_ok == dropP_n else 'FAIL'} cases={n} mismatches={mis} dropP={dropP_ok}/{dropP_n}")
