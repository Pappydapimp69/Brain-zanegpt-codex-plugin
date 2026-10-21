# Sandbox: written vs verbal commitment (Cialdini consistency kernel) composed with the
# BATNA kernel (the counterparty walks when its new alternative beats the deal by more
# than its walk-back cost). Deterministic: temptation gains are taken from an exact
# lognormal quantile grid, no random draws. Costs are ASSUMED units (verbal 1, written 2).
from statistics import NormalDist
import math

N = 2000
Z = [NormalDist().inv_cdf((i + 0.5) / N) for i in range(N)]
C_VERBAL, C_WRITTEN = 1.0, 2.0

def gains(median, sigma=0.75):
    return [median * math.exp(sigma * z) for z in Z]

def renege_rate(median, cost):
    return sum(g > cost for g in gains(median)) / N

def compare(median):
    v, w = renege_rate(median, C_VERBAL), renege_rate(median, C_WRITTEN)
    rel = (v - w) / v if v else 0.0
    return v, w, v - w, rel

# S1 moderate BATNA shocks, S2 large BATNA shocks
s1 = compare(0.5)
s2 = compare(5.0)
print("S1 moderate shocks (median 0.5): verbal %.3f written %.3f abs %.3f rel %.2f" % s1)
print("S2 large shocks (median 5.0):    verbal %.3f written %.3f abs %.3f rel %.2f" % s2)

# S3 partial recap: deal has 3 terms, the recap email writes terms A and B, not C.
# Each term gets its own temptation to reopen it (gain per term = total/3, rotated
# quantiles so terms are not identical); retreat on a term if its gain > its cost.
def partial(median, written=("A", "B")):
    g = gains(median)
    terms = "ABC"
    retreats = {t: 0 for t in terms}
    for i in range(N):
        for k, t in enumerate(terms):
            gi = g[(i + k * 677) % N] / 3.0
            cost = C_WRITTEN if t in written else C_VERBAL
            if gi > cost:
                retreats[t] += 1
    tot = sum(retreats.values())
    return retreats, tot
r_part, tot_part = partial(1.5)
r_full, tot_full = partial(1.5, written=("A", "B", "C"))
r_none, tot_none = partial(1.5, written=())
share_c = r_part["C"] / tot_part if tot_part else 0.0
print("S3 partial recap (median 1.5): retreats", r_part, "share on unwritten C %.2f" % share_c,
      "| all written", tot_full, "| none written", tot_none)

# S4 BREAK: sweep the shock size and find where the written premium stops mattering
sweep = []
for m in [0.25, 0.5, 1, 1.5, 2, 3, 5, 8, 13]:
    v, w, a, rel = compare(m)
    sweep.append((m, v, w, a, rel))
    print("  sweep median %5.2f verbal %.3f written %.3f abs %.3f rel %.2f" % (m, v, w, a, rel))
peak = max(sweep, key=lambda r: r[3])
fade = [r for r in sweep if r[0] > peak[0] and r[3] < 0.05]
first_fade = fade[0][0] if fade else None
print("S4 abs premium peaks at median %.2f (%.3f); first median past peak with abs < 0.05: %s"
      % (peak[0], peak[3], first_fade))

# Pass criteria written before the first run (see proposal Prediction)
ok = (s1[3] > 0.5 and s2[3] < 0.2 and s2[2] < 0.10 and share_c > 0.7 and first_fade is not None)
print("RESULT: %s moderate rel cut %.2f (%.3f->%.3f), large rel cut %.2f abs %.3f, partial recap %.2f of retreats on the unwritten term, premium <0.05 from median %s"
      % ("PASS" if ok else "FAIL", s1[3], s1[0], s1[1], s2[3], s2[2], share_c, first_fade))
