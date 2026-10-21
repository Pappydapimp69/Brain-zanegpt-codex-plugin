"""Sandbox: concept -> 18 variants (hook strength x gameplay fidelity x fail-ending kept/lost), ranked on IPM alone
vs IPM x D1 retention, then recut the winner by beat vs by clock.
Entries: ideas:GAME-ADS/iteration/concept-then-variants-ranked-on-ipm-times-early-retention (rank on IPM AND D1),
ad-length-crossover-depends-on-the-cut/E1 and fail-ad-cutdowns-keep-the-gap/E1 (a clock cut loses the fail ending).
ALL FUNCTIONS BELOW ARE MY ASSUMED MODEL, not measured ad data: IPM = 10*hook*(1.6-0.6*fidelity)*(1.3 if ending kept);
D1 = 0.15+0.25*fidelity (misleading ads convert more, retain less).
PREDICTION (before run): S1 IPM-only winner is a low-fidelity variant (fidelity 0.4) while IPM x D1 winner has
fidelity >= 0.7 and yields >= 15% more retained installs per 1000 impressions; S2 if D1 does not depend on
fidelity (flat 0.30) both rankings pick the same variant (kernel rule moot); S3 BREAK: ranking IPM x D1 with D1 read
from ~12 installs (1000 impressions) is fragile: Wilson lower bound changes the winner vs the point
estimate in at least 1 of 3 hook-matched pairs. [FIRST RUN: 0 flips at 1000 impressions, so this was WRONG;
the sweep over 1000/300/100/50 impressions was added after, to find where it starts to hold]; S4 recutting the winner by clock loses the ending and its score falls
by 1/1.3 (23%), by beat keeps it. Assumption: fidelity drives both IPM down and D1 up. Wrong if IPM-only winner has
fidelity >= 0.7 under the stated model."""
import itertools, math
H = {"weak": 0.7, "mid": 1.0, "strong": 1.4}; F = [0.4, 0.7, 1.0]
def ipm(h, f, end): return 10 * H[h] * (1.6 - 0.6 * f) * (1.3 if end else 1.0)
def d1(f, flat=False): return 0.30 if flat else 0.15 + 0.25 * f
V = [(h, f, e) for h in H for f in F for e in (True, False)]
def best(key): return max(V, key=key)
def retained(v, flat=False): return ipm(v[0], v[1], v[2]) * d1(v[1], flat)
s1_ipm = best(lambda v: ipm(*v)); s1_ret = best(lambda v: retained(v))
gain = retained(s1_ret) / retained(s1_ipm) - 1
print("S1 IPM-only winner", s1_ipm, "ipm %.1f retained %.2f" % (ipm(*s1_ipm), retained(s1_ipm)), "| IPM*D1 winner", s1_ret, "retained %.2f gain %.0f%%" % (retained(s1_ret), gain * 100))
s2a = best(lambda v: ipm(*v)); s2b = best(lambda v: retained(v, True))
print("S2 flat D1: IPM-only", s2a, "IPM*D1", s2b, "same", s2a == s2b)
def wilson_lb(p, n, z=1.64):
    if n == 0: return 0
    c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / (1 + z * z / n)
flips_by_n = {}
for N in (1000, 300, 100, 50):          # impressions per variant; installs = ipm * N / 1000
    flips = 0
    for h in H:
        pair = [(h, 0.7, True), (h, 1.0, True)]
        pt = max(pair, key=lambda v: ipm(*v) * d1(v[1]))
        lb = max(pair, key=lambda v: ipm(*v) * wilson_lb(d1(v[1]), max(1, int(ipm(*v) * N / 1000))))
        flips += pt != lb
    flips_by_n[N] = flips
    print("S3 impressions", N, "lower-bound winner differs from point winner in", flips, "of 3 hook pairs")
flips = flips_by_n[1000]; small = flips_by_n[100]
w = s1_ret; clock = (w[0], w[1], False); beat = w
drop = 1 - retained(clock) / retained(beat)
print("S4 winner", w, "clock-cut score drop %.0f%%, beat-cut drop 0%%" % (drop * 100))
ok = s1_ipm[1] == 0.4 and s1_ret[1] >= 0.7 and gain >= 0.15 and s2a == s2b and flips == 0 and small >= 1 and abs(drop - (1 - 1/1.3)) < 1e-9
print("RESULT: %s IPM-only picks fidelity %.1f, IPM*D1 picks %.1f (+%.0f%% retained installs); flat D1 same winner %s; lower-bound flips at 1000 impr %d/3, at 100 impr %d/3; clock cut loses %.0f%%"
      % ("PASS" if ok else "FAIL", s1_ipm[1], s1_ret[1], gain * 100, s2a == s2b, flips, small, drop * 100))
