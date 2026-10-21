# Deterministic sandbox: best age threshold = payload tolerance, on a NEW tolerance (4) and lag mix.
# PREDICTION (before run): lags 0..12 with counts 10 each (uniform) and a skewed mix (count = lag+1).
# A press with lag L is GOOD to run iff L <= TOL=4. Gate at t accepts iff L <= t.
# cost(t) = w*wrong + lost, wrong = accepted & L>TOL, lost = rejected & L<=TOL.
# Predict argmin t == 4 for w in {0.1, 1, 10} under BOTH mixes (per-lag decisions are independent, so the
# mix cannot move it); at w=0 every t in 4..12 ties at cost 0 and t<4 costs more.
TOL = 4
mixes = {"uniform": {l: 10 for l in range(13)}, "skewed": {l: l + 1 for l in range(13)}}

def cost(t, w, mix):
    wrong = sum(n for l, n in mix.items() if l <= t and l > TOL)
    lost = sum(n for l, n in mix.items() if l > t and l <= TOL)
    return w * wrong + lost

ok = True
for name, mix in mixes.items():
    for w in (0.1, 1, 10):
        costs = {t: cost(t, w, mix) for t in range(13)}
        best = min(costs.values())
        argmin = [t for t, c in costs.items() if c == best]
        print(name, "w", w, "argmin", argmin, "best cost", best, "cost at t=0", costs[0], "t=12", costs[12])
        ok &= argmin == [TOL]
    c0 = {t: cost(t, 0, mix) for t in range(13)}
    tie = [t for t, c in c0.items() if c == 0]
    print(name, "w 0 zero-cost thresholds", tie)
    ok &= tie == list(range(TOL, 13)) and all(c0[t] > 0 for t in range(TOL))
print("RESULT:", "PASS" if ok else "FAIL", "argmin t==4 for w in 0.1/1/10 under both mixes; w=0 ties 4..12")
