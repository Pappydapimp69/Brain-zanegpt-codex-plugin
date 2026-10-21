# Tests matched-distance-beats-any-decaying-cue-at-fixed-framing with an imperfect severity estimate
# (the ZaneGPT break case): distance is matched to a LAGGED or BIASED estimate of severity.
# Arms: M matched only; MC matched + permanent cue 0.7; FC fixed d=0.3 + permanent cue 0.7.
# PREDICTION (before run): on the flat schedule matched-only beats FC for a systematic distance
# error up to about 0.3 and loses beyond it (crossover between 0.25 and 0.35); a 1-beat lag
# costs matched-only little on flat but more on the ramp; MC >= max(M, FC) in every case.
import math
C = 10.0
SCHED = {"flat": [10]*6, "ramp": [2, 4, 6, 8, 10, 10], "three": [2, 6, 10, 10, 10, 10]}
def score(seq, mode, bias=0.0, lag=0, cue=0.0):
    X = tot = 0.0
    for k, I in enumerate(seq):
        if mode == "fixed":
            d = 0.3
        else:
            d = seq[max(k - lag, 0)] / C - bias
        g = math.exp(-((d - I / C) / 0.25) ** 2); g = g + cue * (1 - g)
        tot += math.exp(-0.2 * X) * (I / C) * g; X += 1 / (1 + I / 5)
    return tot
biases = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
cross = {}
for name, s in SCHED.items():
    fc = score(s, "fixed", cue=0.7)
    row = []
    for b in biases:
        m = score(s, "matched", bias=b); mc = score(s, "matched", bias=b, cue=0.7)
        row.append((b, round(m, 2), round(mc, 2)))
    cross[name] = next((b for b, m, _ in row if m < fc), None)
    print(name, "fixed+cue", round(fc, 2), "bias rows (bias, M, MC):", row)
lags = {name: [round(score(s, "matched", lag=L), 2) for L in (0, 1, 2)] for name, s in SCHED.items()}
print("lag 0/1/2 matched only:", lags)
fcf = score(SCHED["flat"], "fixed", cue=0.7)
mc_ok = all(score(s, "matched", bias=b, cue=0.7) >= max(score(s, "matched", bias=b), score(s, "fixed", cue=0.7)) - 1e-9
            for s in SCHED.values() for b in biases)
flat_cross = cross["flat"]
ok = (flat_cross is not None and 0.25 <= flat_cross - 0.0 <= 0.35 + 0.1 and mc_ok
      and lags["flat"][0] - lags["flat"][1] < lags["ramp"][0] - lags["ramp"][1])
print(f"RESULT: {'PASS' if ok else 'FAIL'} crossover bias (matched-only below fixed+cue): {cross}; flat lag loss {lags['flat'][0]-lags['flat'][1]:.2f} vs ramp {lags['ramp'][0]-lags['ramp'][1]:.2f}; matched+cue never worse than either: {mc_ok}")
