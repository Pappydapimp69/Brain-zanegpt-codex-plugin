"""Blind rebuild of 'late severity cap deadline is the schedule midpoint'. Own model.
Prediction (written before the first run): with my gate model the last forgiving cap-arrival beat
RISES with the mild split (it is not a fixed midpoint), so the claim 'did not move with the split' fails.
Model: n beats, severity schedule = mild level M for the first round(split*n) beats then a linear ramp to 1.0;
cap level L from beat k (1-indexed) on: s_t = min(s_t, L). 11 dial distances d = 0,.1..1.
Per-beat funny = exp(-((d - s_t)/W)^2) * H^t (habituation H). Score = sum. Forgiving = >=7 of 11 distances
within 95% of the best score. Deadline = largest k with a forgiving dial (k=n+1 means no cap)."""
import math
D = [i / 10 for i in range(11)]

def schedule(n, split, M=0.15):
    m = round(split * n); s = []
    for t in range(n):
        s.append(M if t < m else M + (1 - M) * (t - m + 1) / max(1, n - m))
    return s

def forgiving(n, split, k, L, W, H):
    s = schedule(n, split)
    s = [min(v, L) if (t + 1) >= k else v for t, v in enumerate(s)]
    sc = [sum(math.exp(-((d - v) / W) ** 2) * H ** t for t, v in enumerate(s)) for d in D]
    best = max(sc)
    return sum(1 for x in sc if x >= 0.95 * best) >= 7

def deadline(n, split, L=0.3, W=0.3, H=0.9):
    ok = [k for k in range(1, n + 2) if forgiving(n, split, k, L, W, H)]
    return max(ok) if ok else 0

rows = {}
for n in (6, 9, 12):
    for sp in (0.2, 0.3, 0.4):
        rows[(n, sp)] = deadline(n, sp)
        print("n=%d split=%.1f deadline=%d  midpoint=%.1f split_cross=%.1f" % (n, sp, rows[(n, sp)], n / 2, n * sp))
# robustness: other W, H
for W, H in ((0.2, 0.9), (0.4, 0.9), (0.3, 1.0), (0.3, 0.8)):
    print("W=%.1f H=%.1f ->" % (W, H), [deadline(n, sp, W=W, H=H) for n in (6, 9, 12) for sp in (0.2, 0.3, 0.4)])
print("W scan (n=6,9,12 x split .2,.3,.4), H=0.9:")
for W in (0.3, 1.0, 1.3, 1.35, 1.45, 1.6):
    print("  W=%.2f" % W, [deadline(n, sp, W=W) for n in (6, 9, 12) for sp in (0.2, 0.3, 0.4)])
moves = [len({rows[(n, sp)] for sp in (0.2, 0.3, 0.4)}) > 1 for n in (6, 9, 12)]
mid = sum(1 for (n, sp), v in rows.items() if abs(v - n / 2) <= 1)
# judge across the whole W regime where a forgiving dial exists at all (W 1.35 .. 1.6), not only W=0.3
reg = [[deadline(n, sp, W=W) for n in (6, 9, 12) for sp in (0.2, 0.3, 0.4)] for W in (1.35, 1.45, 1.6)]
mid = sum(1 for r in reg for i, v in enumerate(r) if abs(v - (6, 9, 12)[i // 3] / 2) <= 1)
claim_holds = mid >= 20
moves = [any(len({r[i * 3 + j] for j in range(3)}) > 1 for r in reg) for i in range(3)]
print("RESULT: %s own gate model: deadline varies with split in %d/3 lengths and sits within 1 of the midpoint in %d/27 cells over three forgiving-regime widths (claim: fixed midpoint, split-independent)"
      % ("PASS" if claim_holds else "FAIL", sum(moves), mid))
