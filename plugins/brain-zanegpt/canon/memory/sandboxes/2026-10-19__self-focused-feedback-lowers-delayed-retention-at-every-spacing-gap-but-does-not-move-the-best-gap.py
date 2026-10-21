# Prediction (before run): reuse the desirable-difficulty spacing model (recall p=exp(-gap/S), difficulty gain G
# on success, fixed re-study gain F on failure; 5 studies, delayed retention exp(-40/S)). Feedback after each study:
# a share s of the learner's attention goes to the self. Task feedback boosts failed-recall re-study gain
# F*(1+1.0*(1-s)); self focus cuts the success gain G*(1-0.6*s).
#  - For s=0, 0.5, 1.0 delayed retention at EVERY gap is ordered s=0 > s=0.5 > s=1.0 (feedback focus matters at 8/8 gaps).
#  - The best gap stays at 4 for all three (focus rescales retention, does not move the optimum).
#  - BREAK: at massed practice (gap 0, p=0.98) the s effect is smallest (spread under 0.01), because few failures exist.
import math
G, F, S0, K, DELAY = 3.0, 0.3, 2.0, 5, 40.0
def run(gap, s):
    S = S0
    for _ in range(K):
        p = math.exp(-gap / S) if gap > 0 else 0.98
        g = G * (1 - 0.6 * s); f = F * (1 + 1.0 * (1 - s))
        S = p * S * (1 + g * (1 - p)) + (1 - p) * S * (1 + f)
    return math.exp(-DELAY / S)
gaps = [0, 1, 2, 4, 8, 16, 32, 64]
R = {s: [run(g, s) for g in gaps] for s in (0.0, 0.5, 1.0)}
for s in R: print("s", s, " ".join("%.4f" % v for v in R[s]), "best gap", gaps[R[s].index(max(R[s]))])
ordered = sum(R[0.0][i] > R[0.5][i] > R[1.0][i] for i in range(len(gaps)))
bests = [gaps[R[s].index(max(R[s]))] for s in R]
spread = [R[0.0][i] - R[1.0][i] for i in range(len(gaps))]
print("gaps with s=0 > s=.5 > s=1:", ordered, "/8; best gaps", bests, "; spread at gap0", round(spread[0], 4), "max spread", round(max(spread), 4), "at gap", gaps[spread.index(max(spread))])
ok = ordered == 8 and len(set(bests)) == 1 and spread[0] < 0.01
print("RESULT:", "PASS" if ok else "FAIL", f"ordered at {ordered}/8 gaps, best gaps {bests}, massed spread {spread[0]:.4f}, max spread {max(spread):.4f}")
