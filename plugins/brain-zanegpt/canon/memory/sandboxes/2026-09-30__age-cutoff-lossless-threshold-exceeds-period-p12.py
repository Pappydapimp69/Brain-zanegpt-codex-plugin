# Prediction (written before run): on P12 W4 wave, N=600 ticks, hint = B when B available at t else A,
# press lands at t+L. Lags set S1={1,3,7,20}: valid presses exist at L=20, so the lossless cutoff is 20 (> period 12);
# cutoff 12 must lose >0 presses. Lags S2={1,2,3}: lossless cutoff is 3 (< period 12), cutoff 2 loses >0.
# Lag set S3={5,12,24}: L=12 and 24 always valid (multiples of period) -> lossless cutoff 24.
P, W, N = 12, 4, 600
def avail(t): return t % P < W
def run(lags, cutoff):
    valid = combined = 0
    for L in lags:
        for t in range(N):
            hint_B = avail(t)
            legal = avail(t + L) if hint_B else True
            if legal:
                valid += 1
                if L <= cutoff: combined += 1
    return valid, combined
def lossless_cutoff(lags):
    tot = run(lags, 10**9)[0]
    return min(c for c in range(0, 40) if run(lags, c)[1] == tot)
res = {}
for name, lags in (("S1", [1,3,7,20]), ("S2", [1,2,3]), ("S3", [5,12,24])):
    v = run(lags, 10**9)[0]
    res[name] = (lossless_cutoff(lags), v - run(lags, P)[1], v - run(lags, 2)[1])
    print(name, lags, "lossless_cutoff=%d lost_at_period=%d lost_at_2=%d" % res[name])
ok = res["S1"][0] > P and res["S1"][1] > 0 and res["S2"][0] < P and res["S2"][2] > 0 and res["S3"][0] == 24 and res["S3"][1] > 0
print("RESULT: %s lossless cutoff = max valid lag: S1 %d, S2 %d, S3 %d vs period %d; period cutoff loses %d in S1"
      % ("PASS" if ok else "FAIL", res["S1"][0], res["S2"][0], res["S3"][0], P, res["S1"][1]))
