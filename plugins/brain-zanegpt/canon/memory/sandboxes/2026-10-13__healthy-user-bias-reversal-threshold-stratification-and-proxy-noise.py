"""Prediction (before run): population of 10000 with health score h in 0..99 (uniform grid, no RNG). Baseline event risk
falls linearly with h (0.20 at h=0 to 0.02 at h=99). Treatment multiplies risk by 1.29 (the WHI CHD hazard ratio).
Uptake probability rises with h: p = lo + (hi-lo)*h/99. (1) Randomized RR recovers 1.29 exactly. (2) Observational RR
crosses below 1.0 once the uptake spread (hi-lo) exceeds roughly 0.5; (3) stratifying on h recovers 1.29 in every stratum
(Simpson-style: crude <1, every stratum >1); (4) stratifying on a noisy proxy of h (error +-30 on the grid) leaves
residual confounding, RR stays below the true 1.29 but above crude. Deterministic expected-value arithmetic, no RNG."""
HR = 1.29
def risk0(h): return 0.20 - 0.18 * h / 99
def uptake(h, lo, hi): return lo + (hi - lo) * h / 99
def crude(lo, hi, proxy=None, bins=1):
    # expected counts per group; strata by proxy bins (proxy(h) -> value 0..99)
    strata = {}
    for h in range(100):
        key = 0 if proxy is None else min(bins - 1, int(proxy(h) * bins / 100))
        w = 100  # people per h level
        p = uptake(h, lo, hi)
        t = strata.setdefault(key, [0, 0, 0, 0])  # treated n, treated events, control n, control events
        t[0] += w * p; t[1] += w * p * min(1, risk0(h) * HR)
        t[2] += w * (1 - p); t[3] += w * (1 - p) * risk0(h)
    return strata
def rr(s): return (s[1] / s[0]) / (s[3] / s[2])
def pooled(strata):  # Mantel-Haenszel style RR
    num = sum(s[1] * s[2] / (s[0] + s[2]) for s in strata.values()); den = sum(s[3] * s[0] / (s[0] + s[2]) for s in strata.values())
    return num / den
# s1 randomized: uptake independent of h
r1 = rr(crude(0.5, 0.5)[0]); print("s1 randomized RR", round(r1, 3))
# s2 sweep uptake spread
cross = None
for k in range(0, 51):
    spread = k / 50
    lo, hi = 0.5 - spread / 2, 0.5 + spread / 2
    v = rr(crude(lo, hi)[0])
    if cross is None and v < 1.0: cross = spread
print("s2 crude RR at spread 0.0/0.5/1.0:", [round(rr(crude(.5 - s / 2, .5 + s / 2)[0]), 3) for s in (0.0, 0.5, 1.0)], "crosses below 1 at spread", cross)
lo, hi = 0.1, 0.9
cr = rr(crude(lo, hi)[0])
st = crude(lo, hi, proxy=lambda h: h, bins=10); per = [round(rr(v), 3) for v in st.values()]
print("s3 crude", round(cr, 3), "10 strata on true h", per, "pooled", round(pooled(st), 3))
# s4 noisy proxy: person with true h is assigned bin of proxy = clamp(h +- 30 alternating by h%2)
noisy = lambda h: max(0, min(99, h + (30 if h % 2 else -30)))
sn = crude(lo, hi, proxy=noisy, bins=10); print("s4 noisy-proxy pooled", round(pooled(sn), 3))
# s5 Bayes: P(h>=50 | treated) vs prior 0.5
tr = sum(100 * uptake(h, lo, hi) for h in range(100)); trh = sum(100 * uptake(h, lo, hi) for h in range(50, 100))
post = trh / tr; print("s5 prior P(healthy)=0.5 posterior given treated", round(post, 3))
ok = abs(r1 - HR) < 1e-9 and cross is not None and 0.1 < cross < 0.9 and cr < 1 and all(x > 1.2 for x in per) and abs(pooled(st) - HR) < 0.02 and cr < pooled(sn) < pooled(st) and post > 0.5
print("RESULT: %s randomized=%.3f crude=%.3f crosses_below_1_at_spread=%.2f strata_min=%.3f pooled_true=%.3f pooled_noisy=%.3f posterior_healthy_given_treated=%.3f" % ("PASS" if ok else "FAIL", r1, cr, cross or -1, min(per), pooled(st), pooled(sn), post))
