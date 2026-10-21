# Rebuild from the claim only. Own fixture: P=9, W=4, phase offset 2, lags {1,3,5,7,8},
# 5 periods, cutoff scanned 0..9. legal(t) = (t+2) % 9 < 4.
# PREDICTION (before run): validity+cutoff loses 0 only from cutoff 8 (largest lag with any
# valid hint); gate-only invalid executions rise non-decreasingly in the cutoff and are
# maximal at cutoff 8 (and 9); per-lag invalid = (N/P)*min(L,W,P-L,P-W) exactly, with lag 8
# giving 5*1 = 5, not 5*4.
P, W, OFF, REPS = 9, 4, 2, 5
LAGS = [1, 3, 5, 7, 8]
BASE = 3 * P
N = REPS * P
legal = lambda t: ((t + OFF) % P) < W
def counts(L):
    ts = range(BASE, BASE + N)
    hints_B = [t for t in ts if legal(t - L)]       # hint names B
    valid = sum(1 for t in hints_B if legal(t))
    invalid = len(hints_B) - valid
    return valid, invalid
tot_valid = {L: counts(L)[0] for L in LAGS}
lost = {c: sum(v for L, v in tot_valid.items() if L > c) for c in range(0, 10)}
gate = {c: sum(counts(L)[1] for L in LAGS if L <= c) for c in range(0, 10)}
lossless = min(c for c in lost if lost[c] == 0)
mono = all(gate[c] <= gate[c + 1] for c in range(9))
mx = max(gate.values())
formula_ok = all(counts(L)[1] == REPS * min(L, W, P - L, P - W) for L in range(1, P))
print("valid per lag", tot_valid); print("lost by cutoff", lost); print("gate invalid by cutoff", gate)
print("lag8 invalid", counts(8)[1], "formula-no-pminus", REPS * min(8, W))
ok = lossless == 8 and mono and gate[lossless] == mx and formula_ok and counts(8)[1] == 5
print("RESULT: %s lossless cutoff %d, gate-only invalid at it %d (max %d), monotone %s, closed form exact on lags 1..8 %s"
      % ("PASS" if ok else "FAIL", lossless, gate[lossless], mx, mono, formula_ok))
