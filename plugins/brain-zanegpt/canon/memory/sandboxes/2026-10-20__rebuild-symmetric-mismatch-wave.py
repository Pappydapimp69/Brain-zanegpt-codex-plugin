# Own fixture: periods 7, 8, 9, 14, 21; window phase offset s; N = k*P ticks.
def legal(t, P, W, s): return (t - s) % P < W
def counts(P, W, L, N, s):
    one = sum(1 for t in range(N) if legal(t, P, W, s) and not legal(t + L, P, W, s))
    sym = sum(1 for t in range(N) if legal(t, P, W, s) != legal(t + L, P, W, s))
    return one, sym
bad = 0; cells = 0; wrap_bad = 0; zero_bad = 0
for P in (7, 8, 9, 14, 21):
    for W in range(1, P):                    # includes W=1 and W=P-1 beyond the claim's 2..P-2
        for s in (0, 3):
            for L in range(1, 3 * P + 1):
                k = 4; N = k * P
                one, sym = counts(P, W, L, N, s); cells += 1
                Lm = L % P
                f = k * min(Lm, W, P - Lm, P - W) if Lm else 0
                if not (sym == 2 * one and one == f): bad += 1
                if L > P and one != counts(P, W, Lm if Lm else P, N, s)[0] and Lm: wrap_bad += 1
                if L % P == 0 and one != 0: zero_bad += 1
# BREAK: N not a whole number of periods
brk = 0; brk_tot = 0
for P in (9, 14):
    for W in range(2, P - 1):
        for L in range(1, P):
            N = 4 * P + 3; brk_tot += 1
            one, sym = counts(P, W, L, N, 0)
            if sym != 2 * one: brk += 1
print(f"cells {cells} bad {bad} wrap_bad {wrap_bad} zero_bad {zero_bad}; partial-period N: sym!=2*one in {brk}/{brk_tot}")
ok = bad == 0 and wrap_bad == 0 and zero_bad == 0 and brk > 0
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"sym==2*one and one==(N/P)*min(L,W,P-L,P-W) in {cells - bad}/{cells} cells incl. phase offsets, W=1, P-1 and L up to 3P; breaks off whole periods in {brk}/{brk_tot}")
