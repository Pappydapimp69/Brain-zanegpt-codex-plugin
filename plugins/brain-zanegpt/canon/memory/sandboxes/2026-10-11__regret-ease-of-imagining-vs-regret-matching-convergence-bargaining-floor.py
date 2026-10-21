"""Sandbox for ideas:REGRET/regret-scales-with-how-EASILY..., ideas:REGRET/regret-minimisation-went-superhuman..., and
sandbox-negotiation-batna/E1 (the alternative sets deal existence).
PREDICTION (before first run):
 P1 (ease): with regret = gap * exp(-K*distance), a near miss (distance 1) at the SAME gap hurts more than a clear miss
    (distance 6) for every gap; but the ranking FLIPS once the far miss's gap exceeds the near miss's by a factor
    exp(K*(6-1)) - so ease beats size only inside a bounded ratio (the boundary is the lesson).
 P2 (regret matching): deterministic full-information regret matching on rock-paper-scissors (2-player zero-sum) has its
    time-average strategy within 0.01 of uniform by T=20000, while on Shapley's 3x3 game (general-sum) the average
    strategies stay more than 0.05 from the unique Nash (uniform) at T=20000 - no-regret is not convergence there.
 P3 (floor): when the buyer's ceiling is below the seller's alternative (no deal zone) the regret of a missed deal is 0 at
    every distance; the ease effect only exists inside a deal zone.
Stdlib only, no RNG."""
import math
K = 0.5
def regret(gap, dist, zone=True):
    return gap * math.exp(-K * dist) if zone else 0.0
# --- P1 ---
near_gt_far_equal_gap = all(regret(g, 1) > regret(g, 6) for g in range(1, 200))
flip_ratio = math.exp(K * 5)
# smallest integer far-gap multiple at which far-miss regret overtakes near-miss regret
ratio = next(r for r in range(1, 1000) if regret(10 * r, 6) >= regret(10, 1))
flip_ok = abs(ratio - math.ceil(flip_ratio)) <= 1
print("P1 near>far at equal gap:", near_gt_far_equal_gap, "flip ratio theory %.2f observed %d" % (flip_ratio, ratio))
# --- P3 --- bargaining: seller alternative (BATNA) 60; buyer ceiling 55 -> no zone; ceiling 80 -> zone [60,80]
def zone(ceiling, batna): return ceiling >= batna
p3_nozone = all(regret(g, d, zone(55, 60)) == 0 for g in (1, 10, 100) for d in (0, 1, 6))
p3_zone = all(regret(g, d, zone(80, 60)) > 0 for g in (1, 10, 100) for d in (0, 1, 6))
print("P3 no-zone regret zero:", p3_nozone, "zone regret positive:", p3_zone)
# --- P2 --- regret matching, full information
def rm_strategy(R):
    pos = [max(r, 0.0) for r in R]; s = sum(pos)
    return [p / s for p in pos] if s > 0 else [1 / len(R)] * len(R)
def play(A, B, T):
    n = 3; RA = [0.0] * n; RB = [0.0] * n; SA = [0.0] * n; SB = [0.0] * n
    # start from a non-uniform opening so the dynamics are not trivially at the fixed point
    RA[0] = 1.0; RB[1] = 1.0
    for _ in range(T):
        x = rm_strategy(RA); y = rm_strategy(RB)
        ua = [sum(A[i][j] * y[j] for j in range(n)) for i in range(n)]
        ub = [sum(B[i][j] * x[i] for i in range(n)) for j in range(n)]
        va = sum(x[i] * ua[i] for i in range(n)); vb = sum(y[j] * ub[j] for j in range(n))
        for i in range(n): RA[i] += ua[i] - va; RB[i] += ub[i] - vb; SA[i] += x[i]; SB[i] += y[i]
    ax = [s / T for s in SA]; ay = [s / T for s in SB]
    dist = max(max(abs(v - 1 / 3) for v in ax), max(abs(v - 1 / 3) for v in ay))
    # exploitability of the average profile (sum of both players' best-response gains)
    ua = [sum(A[i][j] * ay[j] for j in range(n)) for i in range(n)]
    ub = [sum(B[i][j] * ax[i] for i in range(n)) for j in range(n)]
    expl = (max(ua) - sum(ax[i] * ua[i] for i in range(n))) + (max(ub) - sum(ay[j] * ub[j] for j in range(n)))
    return dist, expl
RPS_A = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]; RPS_B = [[-v for v in r] for r in RPS_A]
SH_A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; SH_B = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
d_rps, e_rps = play(RPS_A, RPS_B, 20000)
d_sh, e_sh = play(SH_A, SH_B, 20000)
print("RPS avg-dist-from-uniform %.4f expl %.4f | Shapley dist %.4f expl %.4f" % (d_rps, e_rps, d_sh, e_sh))
p2 = d_rps < 0.01 and d_sh > 0.05
ok = near_gt_far_equal_gap and flip_ok and p3_nozone and p3_zone and p2
print("RESULT: %s ease: near>far at equal gap, flips at gap ratio %d (theory %.1f); no deal zone => regret 0; regret matching T=20000 RPS dist %.4f vs Shapley dist %.4f (expl %.3f)" % ("PASS" if ok else "FAIL", ratio, flip_ratio, d_rps, d_sh, e_sh))
