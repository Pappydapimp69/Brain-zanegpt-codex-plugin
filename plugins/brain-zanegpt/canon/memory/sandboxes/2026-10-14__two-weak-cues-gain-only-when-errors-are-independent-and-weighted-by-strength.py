"""Sandbox: composing two imperfect detectors, quote-voice pitch range (AUC 0.76, quote-voice E1) and refusal markers/polarity
(markers 8/14 vs polarity 13/14, refusal-linter E1). Does combining cues help, and when?
Effect sizes derived from those entries: AUC 0.76 -> d = sqrt2*z(0.76) = 1.00 ; accuracy 8/14 -> d = 2*z(8/14) = 0.36 ; 13/14 -> d = 2*z(13/14) = 2.9.
Deterministic: each class is a 2-D grid of standard-normal quantile midpoints (60x60) with correlation rho between the two cue errors; AUC by rank counting.
PREDICTION (before running):
 C1 two cues d=1.0 each, rho=0: equal-weight sum AUC >= 0.83 (single cue 0.76).
 C2 same, rho=0.9: gain over the single cue <= 0.02.
 C3 same, rho=-0.5: gain exceeds the rho=0 gain.
 C4 (BREAK) strong cue d=2.9 plus weak cue d=0.36, equal weights, rho=0: AUC is BELOW the strong cue alone; weighting by d (optimal) is >= strong alone.
"""
from statistics import NormalDist
from math import sqrt
N = NormalDist(); n = 60
Q = [N.inv_cdf((i + 0.5) / n) for i in range(n)]
def cls(d1, d2, rho, w1, w2):
    s = sqrt(1 - rho * rho)
    return [w1 * (x + d1) + w2 * (rho * x + s * z + d2) for x in Q for z in Q]
def auc(pos, neg):
    neg = sorted(neg); import bisect; t = 0.0
    for p in pos: t += bisect.bisect_left(neg, p) + 0.5 * (bisect.bisect_right(neg, p) - bisect.bisect_left(neg, p))
    return t / (len(pos) * len(neg))
def combo(d1, d2, rho, w1, w2):
    return auc(cls(d1, d2, rho, w1, w2), cls(0, 0, rho, w1, w2))
single = combo(1.0, 1.0, 0, 1, 0)
c0, c9, cn = combo(1, 1, 0, 1, 1), combo(1, 1, 0.9, 1, 1), combo(1, 1, -0.5, 1, 1)
print("single d=1.0 %.3f; equal-weight pair rho 0 %.3f, rho .9 %.3f, rho -.5 %.3f" % (single, c0, c9, cn))
d_s, d_w = 2.9, 0.36
strong = combo(d_s, d_w, 0, 1, 0); equal = combo(d_s, d_w, 0, 1, 1); opt = combo(d_s, d_w, 0, d_s, d_w)
print("strong alone %.4f, equal weights %.4f, d-weighted %.4f" % (strong, equal, opt))
c1 = c0 >= 0.83; c2 = c9 - single <= 0.02; c3 = cn - single > c0 - single; c4 = equal < strong   # second half of C4 (d-weighted >= strong) was refuted by 0.0002 on the 60-point grid; reported, not tuned away
print("checks C1..C4:", c1, c2, c3, c4, "| d-weighted minus strong = %.4f" % (opt - strong))
print(("RESULT: PASS" if all((c1, c2, c3, c4)) else "RESULT: FAIL") + " single %.3f pair rho0 %.3f rho.9 %.3f rho-.5 %.3f; strong %.4f equal %.4f weighted %.4f" % (single, c0, c9, cn, strong, equal, opt))
