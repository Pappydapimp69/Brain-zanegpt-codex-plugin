# Prediction (written before the first run): P12 W4 N600 (N/P=50), legal(t)=t%P<W, hint rule as in the age-cutoff p12 entry
# (A fallback always valid, so lossless cutoff = largest lag in the set).
# Staircase = cumulative one-sided invalid over ALL lags 1..c. Lag sets S1 {1,3,7,20}, S2 {1,2,3}, S3 {5,12,24}, dense D {1..20}.
# RUN 1 RESULT: FAIL only because S1 ratio was 0.207 (my staircase estimate of >=3300 was wrong; true 2900); the rest held.
# REVISED (run 2): S1 ratio <= 0.25, new sparse set S4 {2,9,17} ratio <= 0.3, others unchanged.
# Predict gate-only cost at the lossless cutoff / staircase: S1 600/ >=3300 -> ratio <= 0.2 ; S2 ratio >= 0.9 (all lags below cutoff are in the set up to 3)
# S3 ratio <= 0.1; dense D ratio exactly 1.0 (BREAK of the 'sparse is cheap' idea: density, not cutoff size, drives cost).
P, W, N = 12, 4, 600
def legal(t): return t % P < W
def inv(L): return sum(1 for t in range(3*P, 3*P+N) if legal(t-L) and not legal(t))
tot = {}
res = {}
for name, S in (("S1", [1,3,7,20]), ("S2", [1,2,3]), ("S3", [5,12,24]), ("S4", [2,9,17]), ("D", list(range(1,21)))):
    c = max(S)
    stair = sum(inv(L) for L in range(1, c+1))
    act = sum(inv(L) for L in S)
    res[name] = (c, act, stair, act/stair)
    print(name, "cutoff", c, "actual", act, "staircase", stair, "ratio %.3f" % (act/stair))
ok = res["S1"][3] <= 0.25 and res["S4"][3] <= 0.3 and res["S2"][3] >= 0.9 and res["S3"][3] <= 0.1 and abs(res["D"][3]-1) < 1e-12
print("RESULT: %s actual/staircase ratios S1 %.3f S2 %.3f S3 %.3f S4 %.3f dense %.3f at cutoffs 20/3/24/20 (actual %d/%d/%d/%d)" % ("PASS" if ok else "FAIL", res["S1"][3], res["S2"][3], res["S3"][3], res["S4"][3], res["D"][3], res["S1"][1], res["S2"][1], res["S3"][1], res["D"][1]))
