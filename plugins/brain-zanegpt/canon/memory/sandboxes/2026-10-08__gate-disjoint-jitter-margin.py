# Prediction (before run): an age gate g is error-free iff V+j <= g < I0-j, i.e. exists a
# zero-error g exactly when the nominal gap I0-V > 2j (integer lags, unit steps);
# with gap == 2j (breaker) no gate is error-free. Best-gate total error at gap<2j is >0.
def errs(g, V, I0, I1, j, q=1):
    lost = wrong = 0
    for lag in range(0, V + 1):
        for jit in range(-j, j + 1):
            m = max(0, lag + jit)
            if -(-m // q) > g: lost += 1
    for lag in range(I0, I1 + 1):
        for jit in range(-j, j + 1):
            m = max(0, lag + jit)
            if -(-m // q) <= g: wrong += 1
    return lost, wrong
fails = []; V, I1 = 10, 60
for j in (0, 2, 4):
    for gap in (2*j - 2 if j else -1, 2*j, 2*j + 1, 2*j + 4):
        if gap < 1: continue
        I0 = V + gap
        best = min(((sum(errs(g, V, I0, I1, j)), g) for g in range(0, I1 + 5)))
        clean = best[0] == 0
        pred = gap > 2*j
        print(f"j={j} gap={gap:2d} best_gate={best[1]:2d} total_err={best[0]:3d} clean={clean} predicted={pred}")
        if clean != pred: fails.append((j, gap))
print("RESULT: " + ("PASS" if not fails else "FAIL") + f" zero-error gate exists iff gap>2j; mismatches={fails}")
