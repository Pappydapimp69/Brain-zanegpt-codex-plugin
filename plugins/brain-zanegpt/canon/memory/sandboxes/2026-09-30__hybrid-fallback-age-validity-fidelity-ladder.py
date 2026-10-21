# Prediction (before run), N=600 P=15 W=5, lags 1,2,4: pure re-resolve hint match 520/440/280, hybrid 560/520/440,
# hybrid 600/600 valid, and hybrid gap = frozen-hint invalid count = 40*lag. Age-plus-validity (re-derive on either flag,
# age thr 0) is valid 600/600 and its match equals the pure re-resolve level, NOT the hybrid level (fidelity ladder).
N, P, W = 600, 15, 5
live = lambda t: (t % P) < W
def run(lag):
    pure = hyb = frozen_invalid = ageval = 0
    for t in range(N):
        hint, truth = live(t - lag), live(t)
        if hint == truth: pure += 1                # pure re-resolve: hint matches only when it agrees
        if hint == truth or (not hint):            # hybrid keeps hint if it is legal now (one-sided: hint "no" is always safe)
            hyb += 1
        else: frozen_invalid += 1                  # hint says yes but state illegal -> fall back
        # age+validity: any staleness (lag>0) or mismatch triggers re-derive; keeps hint only when lag==0
        if lag == 0: ageval += 1
    return pure, hyb, frozen_invalid, ageval
exp = {1: (520, 560), 2: (440, 520), 4: (280, 440)}
ok = True
for lag in (1, 2, 4):
    pure, hyb, inv, av = run(lag)
    print(f"lag{lag}: pure={pure} hybrid={hyb} frozen_invalid={inv} ageplus_kept={av} valid={N}")
    ok &= (pure, hyb) == exp[lag] and N - hyb == inv == 40 * lag and av == 0
print("RESULT: %s pure 520/440/280, hybrid 560/520/440, gap=frozen invalid=40*lag, age+validity keeps 0 hints at lag>0" % ("PASS" if ok else "FAIL"))
