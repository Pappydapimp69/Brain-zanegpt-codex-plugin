"""Sandbox for three TIME-MANAGEMENT kernels:
 K1 planning-fallacy/estimation-bias: even worst-case estimates underestimate how long things take.
 K2 decision-fatigue/replication-crisis: a parole-order effect can be a scheduling artifact (favorable rulings take longer).
 K3 multitasking/switch-cost: switching tasks costs time even when predictable.
Exact discrete arithmetic, no RNG, stdlib only."""
from itertools import product
from fractions import Fraction as F

# ---------- Part A: estimates vs actual totals ----------
D = {1: F(1,2), 2: F(3,10), 4: F(1,5)}        # per-task duration (days): median 1, P90 4, mean 1.9
G = {F(1): F(6,10), F(3,2): F(3,10), F(5,2): F(1,10)}   # shared delay factor (scope creep / dependency)
def convolve(n):
    dist = {0: F(1)}
    for _ in range(n):
        new = {}
        for a, pa in dist.items():
            for d, pd in D.items(): new[a+d] = new.get(a+d, 0) + pa*pd
        dist = new
    return dist
def p_finish(n, est, g_dist, s):
    tot = F(0)
    for g, pg in g_dist.items():
        for t, pt in convolve(n).items():
            if t*g + s*(n-1) <= est: tot += pg*pt
    return float(tot)
IND = {F(1): F(1)}
rows = {}
for n in (1, 3, 6, 12):
    med = 1*n; p90 = 4*n
    outside = float(sum(g*pg for g, pg in G.items()) * sum(t*p for t, p in convolve(n).items())) + 0.5*(n-1)   # mean total from past similar projects
    r = {"median_sum": p_finish(n, med, IND, 0), "worst_sum_indep": p_finish(n, p90, IND, 0),
         "worst_sum_shared_switch": p_finish(n, p90, G, F(1,2)), "outside_view_shared_switch": p_finish(n, outside, G, F(1,2)),
         "worst_sum_shared_noswitch": p_finish(n, p90, G, 0)}
    rows[n] = r
    print(f"A n={n:2d} P(finish by estimate): " + "  ".join(f"{k}={v:.3f}" for k, v in r.items()))
a1 = all(rows[n]["median_sum"] < 0.5 for n in (3, 6, 12))                        # typical-case plan fails
a2 = rows[12]["worst_sum_indep"] > 0.99 and rows[1]["worst_sum_indep"] >= 0.8   # independent worst-case ends up generous
a3 = all(rows[n]["worst_sum_shared_switch"] < rows[n]["worst_sum_indep"] for n in (6, 12)) and rows[12]["worst_sum_shared_switch"] < 0.95  # shared delay + switching: worst-case no longer safe
a4 = abs(rows[12]["outside_view_shared_switch"] - 0.5) < 0.25                    # reference-class total sits near the middle, no systematic miss
print("A checks:", a1, a2, a3, a4)

# ---------- Part B: order effect without any fatigue ----------
SESSION = 60
def cases(n=1200): return [((i*0.6180339887) % 1.0) < 0.5 for i in range(n)]          # True = favorable (~50%), merit fixed by the case
def run(policy, dur_fav, dur_unf):
    queue = list(enumerate(cases())); sess_pos = {}                   # position-in-session -> [favorable count, total]
    sessions = 0
    while queue and sessions < 100:
        t = 0; pos = 0; sessions += 1
        while queue:
            pick = None
            for k, (i, fav) in enumerate(queue):
                d = dur_fav if fav else dur_unf
                if t + d <= SESSION or policy == "fifo-overrun":
                    if policy == "fifo-overrun" and t >= SESSION: break
                    if policy == "defer-long" or policy == "fifo-overrun" or True:
                        pick = k; break
            if pick is None: break
            i, fav = queue.pop(pick); d = dur_fav if fav else dur_unf
            if policy == "fifo-overrun" and t >= SESSION: queue.insert(pick, (i, fav)); break
            c = sess_pos.setdefault(pos, [0, 0]); c[0] += fav; c[1] += 1
            t += d; pos += 1
    return sess_pos
def late_vs_early(sp):
    ks = sorted(sp); half = len(ks)//2
    e = [sp[k] for k in ks[:max(1,half//2)]]; l = [sp[k] for k in ks[-max(1,half//2):]]
    rate = lambda xs: sum(a for a,_ in xs)/max(1,sum(b for _,b in xs))
    return rate(e), rate(l)
# Scenario B1: favorable rulings take 12, unfavorable 4, scheduler picks the first queued case that still fits before the break.
e1, l1 = late_vs_early(run("fit", 12, 4))
# Scenario B2 (control): equal durations -> artifact should vanish
e2, l2 = late_vs_early(run("fit", 8, 8))
# Scenario B3: duration ratio sweep
sweep = {r: late_vs_early(run("fit", 4*r, 4)) for r in (1, 2, 3)}
print(f"B1 favorable early={e1:.2f} late={l1:.2f} (decisions follow merit only; no fatigue modelled)")
print(f"B2 equal durations early={e2:.2f} late={l2:.2f}")
print("B3 ratio sweep (early, late):", {r: (round(a, 2), round(b, 2)) for r, (a, b) in sweep.items()})
b1 = e1 - l1 >= 0.2; b2 = abs(e2 - l2) < 0.05; b3 = sweep[3][0]-sweep[3][1] >= sweep[2][0]-sweep[2][1] >= sweep[1][0]-sweep[1][1]
print("B checks:", b1, b2, b3)
checks = [a1, a2, a3, a4, b1, b2, b3]
print("RESULT:", "PASS" if all(checks) else "FAIL", f"A: sum-of-medians finish prob {rows[6]['median_sum']:.3f} at n=6; independent worst-case sum {rows[12]['worst_sum_indep']:.3f} at n=12 but shared delay plus switching {rows[12]['worst_sum_shared_switch']:.3f}; B: favorable rate early {e1:.2f} -> late {l1:.2f} with no fatigue, vanishes with equal durations ({e2:.2f} vs {l2:.2f}); checks {sum(checks)}/{len(checks)}")
