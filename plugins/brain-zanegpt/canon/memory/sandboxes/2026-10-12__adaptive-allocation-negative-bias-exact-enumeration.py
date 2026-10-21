"""Prediction (before run), two Bernoulli arms, T=12 pulls, exact enumeration of every outcome sequence (Fractions,
no RNG, no sampling):
 P1 fixed alternating allocation (6+6): per-arm sample-mean bias is exactly 0 for both arms.
 P2 greedy allocation (2 pulls each, then pull the arm with the higher running mean, ties to arm 0): the sample-mean
    bias is NEGATIVE for BOTH arms at p=(0.6,0.4) and at p=(0.5,0.5) (conditioning on the arm having >=1 pull).
 P3 greedy has lower expected cumulative regret than fixed at p=(0.6,0.4) (the reason to use it) but a larger
    expected squared error of the worse arm's estimate than fixed.
 P4 BREAK: choosing the apparent winner (higher final mean) and reading its in-test mean OVERSTATES its true p
    (positive, winner's curse) even though every arm mean is biased down; a fresh fixed holdout re-estimate of the
    chosen arm has bias exactly 0.
"""
from fractions import Fraction as F
from itertools import product
T = 12
def tree(p, policy):
    # depth-first over states: (t, n0, s0, n1, s1) with probability; policy picks the arm from state
    res = dict(m0=F(0), m1=F(0), q0=F(0), q1=F(0), reg=F(0), se1=F(0), selm=F(0), selp=F(0), qsel=F(0))
    best = 0 if p[0] >= p[1] else 1
    def rec(t, n, s, prob, pulls_worse):
        if t == T:
            for a in (0, 1):
                if n[a] >= 1:
                    res["m%d" % a] += prob * (F(s[a], n[a]) - p[a]); res["q%d" % a] += prob
            res["reg"] += prob * pulls_worse
            if n[1] >= 1:
                res["se1"] += prob * (F(s[1], n[1]) - p[1]) ** 2 * 1
            mean = [F(s[a], n[a]) if n[a] else F(0) for a in (0, 1)]
            win = 0 if mean[0] >= mean[1] else 1
            res["selm"] += prob * (mean[win] - p[win]); res["selp"] += prob * p[win]; res["qsel"] += prob
            return
        a = policy(t, n, s)
        for o, po in ((1, p[a]), (0, 1 - p[a])):
            if po == 0: continue
            n2 = list(n); s2 = list(s); n2[a] += 1; s2[a] += o
            rec(t + 1, tuple(n2), tuple(s2), prob * po, pulls_worse + (1 if a != best else 0))
    rec(0, (0, 0), (0, 0), F(1), 0)
    return {k: res[k] for k in res}
def fixed(t, n, s): return t % 2
def greedy(t, n, s):
    if n[0] < 2: return 0
    if n[1] < 2: return 1
    return 0 if F(s[0], n[0]) >= F(s[1], n[1]) else 1
out = {}
for name, pol in (("fixed", fixed), ("greedy", greedy)):
    for p in ((F(6, 10), F(4, 10)), (F(1, 2), F(1, 2))):
        r = tree(p, pol)
        bias0 = r["m0"] / r["q0"]; bias1 = r["m1"] / r["q1"]
        out[(name, p)] = (bias0, bias1, r["reg"], r["se1"] / r["q1"], r["selm"])
        print(name, "p=%s/%s" % (p[0], p[1]), "bias arm0 %.5f arm1 %.5f  E[worse-arm pulls] %.3f  MSE arm1 %.5f  winner in-test overstatement %.5f"
              % (float(bias0), float(bias1), float(r["reg"]), float(r["se1"] / r["q1"]), float(r["selm"])))
P = (F(6, 10), F(4, 10)); H = (F(1, 2), F(1, 2))
ok = True
ok &= out[("fixed", P)][0] == 0 and out[("fixed", P)][1] == 0 and out[("fixed", H)][0] == 0
ok &= out[("greedy", P)][0] < 0 and out[("greedy", P)][1] < 0 and out[("greedy", H)][0] < 0 and out[("greedy", H)][1] < 0
ok &= out[("greedy", P)][2] < out[("fixed", P)][2] and out[("greedy", P)][3] > out[("fixed", P)][3]
ok &= out[("greedy", P)][4] > 0 and out[("fixed", P)][4] > 0
# holdout: fresh fixed sample of the chosen arm has expectation p -> bias 0 by linearity; check exactly with 6 fresh pulls
hold = F(0)
for outs in product((0, 1), repeat=6):
    pr = F(1)
    for o in outs: pr *= P[0] if o else 1 - P[0]
    hold += pr * (F(sum(outs), 6) - P[0])
print("holdout re-estimate bias (arm0, 6 fresh pulls):", hold)
ok &= hold == 0
g = out[("greedy", P)]; f = out[("fixed", P)]
print("RESULT: %s greedy arm means biased low (%.4f, %.4f at p=.6/.4; %.4f, %.4f at .5/.5) vs fixed 0; worse-arm pulls %.2f vs %.2f; MSE arm1 %.4f vs %.4f; winner in-test overstatement +%.4f (greedy) +%.4f (fixed); holdout bias 0"
      % ("PASS" if ok else "FAIL", float(g[0]), float(g[1]), float(out[("greedy", H)][0]), float(out[("greedy", H)][1]), float(g[2]), float(f[2]), float(g[3]), float(f[3]), float(g[4]), float(f[4])))
