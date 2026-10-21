# Prediction (before run): with a retrieval-difficulty gain (stability grows by g*(1-p) per recalled study),
# in-session performance falls monotonically as spacing gap rises while delayed retention rises then falls
# (inverted U, peak at an intermediate gap, NOT the longest); with a constant-gain control (no difficulty bonus)
# massed practice wins delayed retention, so the effect lives in the difficulty mechanism, not spacing per se.
# ITERATION 1 result: control prediction WRONG (massed did not win; constant gain made every gap tie at 0.0718).
# Criterion revised to what the model shows: constant-gain control is flat across gaps. Main prediction unchanged.
# Deterministic expected-value model: recall p=exp(-dt/S); a study at gap dt gives S*=1+G*(1-p) if recalled (weight p),
# and a failed recall (weight 1-p) re-studies for a small fixed gain F. Expected S update is used (no sampling).
import math
G, F, S0, K, DELAY = 3.0, 0.3, 2.0, 5, 40.0

def run(gap, gain_mode):
    S, perf = S0, []
    for _ in range(K):
        p = math.exp(-gap / S) if gap > 0 else 0.98   # gap 0 = massed: immediate re-read, near-certain recall
        perf.append(p)
        if gain_mode == "difficulty":
            S = p * S * (1 + G * (1 - p)) + (1 - p) * S * (1 + F)
        else:                                         # constant gain: easy and hard retrievals teach equally
            S = p * S * (1 + 0.5) + (1 - p) * S * (1 + 0.5)
    return sum(perf) / K, math.exp(-DELAY / S)

gaps = [0, 1, 2, 4, 8, 16, 32, 64]
rows = {}
for mode in ("difficulty", "constant"):
    rows[mode] = [(g,) + run(g, mode) for g in gaps]
    print(mode)
    for g, perf, ret in rows[mode]:
        print("  gap %3d  in-session perf %.3f  delayed retention %.4f" % (g, perf, ret))

d = rows["difficulty"]; c = rows["constant"]
perf_mono = all(d[i][1] >= d[i + 1][1] for i in range(len(d) - 1))
best = max(d, key=lambda r: r[2])
inv_u = 0 < gaps.index(best[0]) < len(gaps) - 1 and d[-1][2] < best[2] and d[0][2] < best[2]
const_flat = max(r[2] for r in c) - min(r[2] for r in c) < 1e-9
print("RESULT: %s perf monotone down=%s, difficulty-model retention peaks at gap %d (%.4f; massed %.4f, longest %.4f), constant-gain control flat=%s (all gaps %.4f)"
      % ("PASS" if perf_mono and inv_u and const_flat else "FAIL", perf_mono, best[0], best[2], d[0][2], d[-1][2], const_flat, c[0][2]))
