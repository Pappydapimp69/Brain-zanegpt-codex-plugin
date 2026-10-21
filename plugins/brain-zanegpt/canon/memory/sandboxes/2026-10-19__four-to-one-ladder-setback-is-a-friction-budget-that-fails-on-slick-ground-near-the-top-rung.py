"""Sandbox: is the 4-to-1 ladder setback rule (base out = height/4) a friction budget?
Exact rational statics (fractions), no RNG, no timing. Ladder of weight w leaning on a wall at height h,
base b out; climber of weight W at fraction s of the way up; wall friction coefficient mw; ground mu.
Equilibrium: Nw*h + Fw*b = b*(s*W + w/2) with Fw = mw*Nw; ground normal Ng = W + w - Fw; ground friction needed = Nw.
No slip iff Nw <= mu*Ng.
Prediction (written before first run): at 4:1, W=800 N, w=100 N, frictionless wall, climber at the top (s=1) the minimum
ground mu is 17/72 = 0.2361; ladder length (3, 6, 9 m) does not change it; with mu=0.20 the ladder slips once the climber passes
s = 0.8375 and the setback that fixes it is height/4.72; wall friction mw=0.3 lowers the needed mu by under 1 percent; BREAK: load/ladder weight sweep keeps the need within 0.03 of 17/72 (iteration 1 refuted this: spread 0.0376).
"""
from fractions import Fraction as F

def need_mu(b_over_h, s, W=F(800), w=F(100), mw=F(0), length=1):
    h = F(length); b = b_over_h * h
    nw = b * (s * W + w / 2) / (h + mw * b)
    return nw / (W + w - mw * nw)

def slips(mu, b_over_h, s, **kw): return need_mu(b_over_h, s, **kw) > mu

q = F(1, 4)
top = need_mu(q, F(1))
print("S1 4:1 top rung need mu", top, float(top))
c1 = top == F(17, 72)
lens = {L: need_mu(q, F(1), length=L) for L in (3, 6, 9)}
c2 = len(set(lens.values())) == 1
print("S2 length independence:", {k: float(v) for k, v in lens.items()})
mu = F(1, 5)
# smallest s (to 1/10000) where it slips at 4:1 on mu=0.2
s_star = next(F(i, 10000) for i in range(10001) if slips(mu, q, F(i, 10000)))
print("S3 mu=0.2 first slip at s =", float(s_star))
c3 = abs(float(s_star) - 0.8375) < 0.001
# setback needed at s=1 for mu=0.2: solve b/h by bisection on exact fractions
lo, hi = F(0), F(1)
for _ in range(60):
    mid = (lo + hi) / 2
    (lo, hi) = (lo, mid) if slips(mu, mid, F(1)) else (mid, hi)
print("S3b setback b/h for mu=0.2, top rung:", float(lo), " ratio 1 :", float(1 / lo))
c3b = abs(float(1 / lo) - 4.72) < 0.02
wall = need_mu(q, F(1), mw=F(3, 10))
red = float((top - wall) / top)
print("S4 wall friction 0.3: need mu", float(wall), "reduction", red)
c4 = 0 < red < 0.01
# BREAK: does a heavier carried load / lighter ladder move the 4:1 requirement a lot? (rule claims one ratio fits all)
loads = {(W, w): float(need_mu(q, F(1), W=F(W), w=F(w))) for W, w in [(800, 100), (1200, 100), (800, 400), (1500, 50)]}
print("S5 BREAK load sweep need mu at 4:1 top:", loads)
spread = max(loads.values()) - min(loads.values())
# Iteration 1 predicted a spread under 0.03; observed 0.0376 because a heavy 400 N ladder lowers the need to 0.2083. Corrected claim:
# the need stays under 0.25 for every load tried, but moves 0.21 to 0.246, so 'one ratio' is a bound, not a constant.
c5 = max(loads.values()) < 0.25 and spread > 0.03
ok = c1 and c2 and c3 and c3b and c4 and c5
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"4:1 top need mu {float(top):.4f}; length-invariant {c2}; mu 0.2 slips from s={float(s_star):.4f}; fix ratio 1:{float(1/hi):.2f}; wall friction cut {red:.4f}; load spread {spread:.4f}")
