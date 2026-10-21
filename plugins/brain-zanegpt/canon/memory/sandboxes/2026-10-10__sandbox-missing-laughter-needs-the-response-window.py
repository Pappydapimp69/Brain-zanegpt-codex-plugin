"""Sandbox: does missing laughter reveal a failed joke only when the performer
knows the expected response window?

Structural model only (measurement / scoring / dynamics under stated assumptions).
It says nothing about real audiences or real people.

PREDICTIONS (written BEFORE the first run; each could come out wrong):
 P1 baseline room (n=20, p_resp=0.6, latency median 1.0s sigma 0.5, quiet,
    threshold 2 audible laughs, prior fail 0.3), window = true 95th percentile:
    balanced accuracy >= 0.95 AND posterior(fail | silence) >= 0.95.
 P2 window 0.25x the true one: miss rate on landed jokes >= 0.30 AND
    posterior(fail | silence) < 0.85.
 P3 window 4x too long: still posterior >= 0.90 when quiet, but at high
    ambient noise (nu=2) its balanced accuracy is below the known-window one.
 P4 small room n=3 (p_resp 0.6, theta 2): balanced accuracy < 0.80 even with
    the window known; BUT a reliable single partner (n=1, p_resp 0.95, narrow
    latency, theta 1) keeps posterior >= 0.95 (smallness alone is not the cause).
 P5 text channel (median 8s, sigma 0.9, p_resp 0.08, n=20): miss rate >= 0.40
    even with the window known; and a live-room window (2.4s) applied to it
    misses >= 0.95 of landed jokes.
 P6 late-laugh audience (median 2.5s, sigma 0.8) read with a window tuned to a
    live room (median 1.0s): miss rate >= 0.30.
 P7 BREAK scenario, polite laughter on a failed joke (power gap, 50% of the
    room): silence stays high-precision (posterior >= 0.95) but is RARE
    (P(silence | failed) < 0.20), so missing laughter is not the dependable
    reveal there -- the reveal becomes low-recall.
 P8 'only when known' is too strong: in a quiet room every assumed window >= the
    true one (1x, 2x, 4x) keeps posterior >= 0.90; only too-short windows fail.
    (Expected to HOLD as stated, i.e. refine the claim to 'window not too short'.)
Deterministic: exact binomial/Poisson sums and closed-form latency CDF; no RNG,
no real timing.
"""
import math

PRIOR_FAIL = 0.3
LAMBDA0 = 0.1  # ambient false 'laugh-like' events per second at nu=1


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def ln_cdf(t, median, sigma):
    if t <= 0:
        return 0.0
    return phi((math.log(t) - math.log(median)) / sigma)


def ln_quantile(q, median, sigma):
    # inverse normal by bisection (deterministic)
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if phi(mid) < q:
            lo = mid
        else:
            hi = mid
    return median * math.exp(sigma * lo)


def binom_pmf(n, p, kmax):
    out = []
    for k in range(kmax + 1):
        if k > n:
            out.append(0.0)
        else:
            out.append(math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k)))
    return out


def pois_pmf(lam, kmax):
    return [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(kmax + 1)]


def p_below(n, p, lam, theta):
    """P(binomial(n,p)+poisson(lam) < theta)"""
    b = binom_pmf(n, p, theta)
    q = pois_pmf(lam, theta)
    tot = 0.0
    for i in range(theta):
        for j in range(theta - i):
            tot += b[i] * q[j]
    return tot


def read(cfg, window, theta):
    """returns (P(silence|landed), P(silence|failed)) under assumed window."""
    a = 1.0 / (1.0 + cfg["nu"])           # masking: audibility of a real laugh
    lam = LAMBDA0 * cfg["nu"] * window    # noise events falling in the window
    f = ln_cdf(window, cfg["median"], cfg["sigma"])
    sil_landed = p_below(cfg["n"], cfg["p_resp"] * f * a, lam, theta)
    sil_failed = p_below(cfg["n"], cfg["p_polite"] * f * a, lam, theta)
    return sil_landed, sil_failed


def score(cfg, window, theta):
    sl, sf = read(cfg, window, theta)
    miss = sl                              # landed joke read as failed
    recall = sf                            # failed joke produces silence
    bal = 0.5 * ((1 - sl) + sf)            # balanced accuracy of 'silence => failed'
    post = PRIOR_FAIL * sf / (PRIOR_FAIL * sf + (1 - PRIOR_FAIL) * sl) if (sf + sl) > 0 else float("nan")
    return dict(miss=miss, recall=recall, bal=bal, post=post)


def base(**kw):
    c = dict(n=20, p_resp=0.6, p_polite=0.0, median=1.0, sigma=0.5, nu=0.0)
    c.update(kw)
    return c


def true_w(cfg):
    return ln_quantile(0.95, cfg["median"], cfg["sigma"])


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(f"  [{'HELD' if ok else 'REFUTED'}] {name}: {detail}")


print("== A. window multiplier c x noise nu (n=20, baseline, theta=2) ==")
print("   c     nu=0 bal/post/miss        nu=0.5 bal      nu=1 bal      nu=2 bal")
for c in (0.25, 0.5, 1, 2, 4, 8):
    row = []
    for nu in (0, 0.5, 1, 2):
        cfg = base(nu=nu)
        s = score(cfg, c * true_w(cfg), 2)
        row.append(s)
    s0 = row[0]
    print(f"  {c:>4}  {s0['bal']:.3f}/{s0['post']:.3f}/{s0['miss']:.3f}      "
          f"{row[1]['bal']:.3f}          {row[2]['bal']:.3f}         {row[3]['bal']:.3f}")

print("== B. n x p_resp (window known, quiet, theta=2) ==  bal / miss")
for n in (1, 2, 3, 5, 10, 20, 50):
    cells = []
    for p in (0.95, 0.6, 0.3, 0.1):
        cfg = base(n=n, p_resp=p)
        s = score(cfg, true_w(cfg), 2 if n >= 2 else 1)
        cells.append(f"{s['bal']:.2f}/{s['miss']:.2f}")
    print(f"  n={n:>3}  p=.95 {cells[0]}  p=.6 {cells[1]}  p=.3 {cells[2]}  p=.1 {cells[3]}")

print("== C. detection threshold theta x n (known window, quiet, p=.6) ==  bal")
for n in (3, 10, 20, 50):
    cells = []
    for th in (1, 2, 3, 5, 8):
        cfg = base(n=n)
        cells.append(f"{score(cfg, true_w(cfg), th)['bal']:.2f}")
    print(f"  n={n:>3}  theta 1,2,3,5,8: {' '.join(cells)}")

print("== D. latency tail (late laugh): window tuned to median 1.0/sigma .5 ==")
tuned = true_w(base())
for med, sg in ((1.0, 0.5), (1.5, 0.5), (2.5, 0.8), (4.0, 0.8)):
    cfg = base(median=med, sigma=sg)
    s = score(cfg, tuned, 2)
    k = score(cfg, true_w(cfg), 2)
    print(f"  median {med} sigma {sg}: tuned-window miss {s['miss']:.3f} post {s['post']:.3f} | known-window miss {k['miss']:.3f} post {k['post']:.3f}")

print("== E. polite laughter on failed jokes (fraction of room) ==  recall P(sil|fail) / post / miss")
for q in (0.0, 0.05, 0.1, 0.2, 0.3, 0.5):
    cfg = base(p_polite=q)
    s = score(cfg, true_w(cfg), 2)
    print(f"  polite {q:.2f}: recall {s['recall']:.3f} post {s['post']:.3f} miss {s['miss']:.3f} bal {s['bal']:.3f}")

print("== F. channel presets (window known vs live-tuned window) ==")
live_w = tuned
presets = {
    "live n=20": base(),
    "small n=3": base(n=3),
    "partner n=1": base(n=1, p_resp=0.95, sigma=0.25),
    "text n=20": base(median=8.0, sigma=0.9, p_resp=0.08),
    "text n=200": base(n=200, median=8.0, sigma=0.9, p_resp=0.08),
}
for name, cfg in presets.items():
    th = 1 if cfg["n"] == 1 else 2
    k = score(cfg, true_w(cfg), th)
    l = score(cfg, live_w, th)
    print(f"  {name:<12} known: bal {k['bal']:.3f} miss {k['miss']:.3f} post {k['post']:.3f} | live-tuned window: miss {l['miss']:.3f} bal {l['bal']:.3f}")

print("== PREDICTION CHECKS ==")
cfg = base(); s = score(cfg, true_w(cfg), 2)
check("P1 baseline known window", s["bal"] >= 0.95 and s["post"] >= 0.95, f"bal {s['bal']:.3f} post {s['post']:.3f}")

s = score(cfg, 0.25 * true_w(cfg), 2)
check("P2 window 0.25x", s["miss"] >= 0.30 and s["post"] < 0.85, f"miss {s['miss']:.3f} post {s['post']:.3f}")

q4 = score(cfg, 4 * true_w(cfg), 2)
cn = base(nu=2)
k2 = score(cn, true_w(cn), 2); l2 = score(cn, 4 * true_w(cn), 2)
check("P3 window 4x", q4["post"] >= 0.90 and l2["bal"] < k2["bal"], f"quiet post {q4['post']:.3f}; noisy bal long {l2['bal']:.3f} vs known {k2['bal']:.3f}")

c3 = base(n=3); s3 = score(c3, true_w(c3), 2)
c1 = base(n=1, p_resp=0.95, sigma=0.25); s1 = score(c1, true_w(c1), 1)
check("P4 small room vs reliable partner", s3["bal"] < 0.80 and s1["post"] >= 0.95, f"n=3 bal {s3['bal']:.3f}; n=1 post {s1['post']:.3f}")

ct = presets["text n=20"]; st = score(ct, true_w(ct), 2); sl = score(ct, live_w, 2)
check("P5 text channel", st["miss"] >= 0.40 and sl["miss"] >= 0.95, f"known miss {st['miss']:.3f}; live-window miss {sl['miss']:.3f}")

cl = base(median=2.5, sigma=0.8); s6 = score(cl, tuned, 2)
check("P6 late laugh vs tuned window", s6["miss"] >= 0.30, f"miss {s6['miss']:.3f}")

cp = base(p_polite=0.5); s7 = score(cp, true_w(cp), 2)
check("P7 polite laughter break", s7["post"] >= 0.95 and s7["recall"] < 0.20, f"post {s7['post']:.3f} recall {s7['recall']:.4f}")

okc = all(score(cfg, c * true_w(cfg), 2)["post"] >= 0.90 for c in (1, 2, 4))
bad = [c for c in (0.25, 0.5) if score(cfg, c * true_w(cfg), 2)["post"] < 0.90]
check("P8 only too-short windows fail (quiet)", okc and len(bad) >= 1, f"c>=1 pass={okc}; failing short c={bad}")

print("== POST-HOC (added AFTER seeing the P4/P6/P7 refutations; not pre-registered) ==")
print(" H1 late laugh x room size: miss rate with a live-tuned window (2.3s), p_resp .6, theta 2")
for med, sg in ((1.0, 0.5), (2.5, 0.8), (4.0, 0.8), (6.0, 1.0)):
    cells = []
    for n in (3, 5, 10, 20):
        cfg = base(n=n, median=med, sigma=sg)
        cells.append(f"n={n}:{score(cfg, tuned, 2)['miss']:.2f}")
    print(f"   median {med} sigma {sg}: " + "  ".join(cells))
cfg_a = base(n=3, median=4.0, sigma=0.8)
cfg_b = base(n=20, median=4.0, sigma=0.8)
h1_small = score(cfg_a, tuned, 2)["miss"]; h1_big = score(cfg_b, tuned, 2)["miss"]
print(f"   late laugh (median 4.0): n=3 miss {h1_small:.3f} vs n=20 miss {h1_big:.3f}; window known n=3 miss {score(cfg_a, true_w(cfg_a), 2)['miss']:.3f}")

print(" H2 posterior(fail | silence) vs prior-of-failure and the channel's miss rate")
print("   prior fail:   0.05   0.15   0.30   0.60")
for label, cfg, th in (("partner n=1 p=.95", base(n=1, p_resp=0.95, sigma=0.25), 1),
                       ("live n=20", base(), 2),
                       ("text n=20", presets["text n=20"], 2)):
    cells = []
    for pr in (0.05, 0.15, 0.30, 0.60):
        sl, sf = read(cfg, true_w(cfg), th)
        cells.append(f"{pr*sf/(pr*sf+(1-pr)*sl):.3f}")
    print(f"   {label:<18} " + "  ".join(cells))
sl, sf = read(base(n=1, p_resp=0.95, sigma=0.25), true_w(base(n=1, p_resp=0.95, sigma=0.25)), 1)
h2_low = 0.05 * sf / (0.05 * sf + 0.95 * sl)
print(f"   partner at prior 0.05: posterior {h2_low:.3f} (a rare silence from a reliable partner is mostly a skipped laugh, not a verdict)")

print(" H3 repeat hook decay (n=1, theta 1, window known): likelihood ratio of silence for 'valve changed' vs 'valve intact'")
cfg_r = base(n=1, p_resp=0.95, sigma=0.25)
w_r = true_w(cfg_r)
sil_intact = read(cfg_r, w_r, 1)[0]
for step, p in enumerate((0.95, 0.6, 0.3, 0.05), 1):
    c2 = dict(cfg_r, p_resp=p)
    sil = read(c2, w_r, 1)[0]
    print(f"   repeat {step}: p_resp {p:.2f} P(silence) {sil:.3f}  LR vs intact {sil / sil_intact:.1f}")
lr_last = read(dict(cfg_r, p_resp=0.05), w_r, 1)[0] / sil_intact
print(f"   single silence after the pattern was established: LR {lr_last:.1f}; one silence at the first repeat: LR {read(cfg_r, w_r, 1)[0] / sil_intact:.1f}")

print(" H4 'window known' is not sufficient: known-window balanced accuracy < 0.80 in these cells")
insuff = [(n, p) for n in (1, 2, 3, 5, 10, 20) for p in (0.95, 0.6, 0.3, 0.1)
          if score(base(n=n, p_resp=p), true_w(base(n=n, p_resp=p)), 2 if n >= 2 else 1)["bal"] < 0.80]
print(f"   {len(insuff)} of 24 cells; examples {insuff[:6]}")

ph = []
ph.append(h1_small > 0.30 and h1_big < 0.30)
ph.append(h2_low < 0.5)
ph.append(lr_last > 5)
ph.append(len(insuff) >= 8)
print("   post-hoc checks (late laugh bites only in small rooms; rare silence from reliable partner < .5 at low prior; decayed valve LR > 5; >= 8 insufficient cells):", ph)

held = sum(checks)
print(f"RESULT: {'PASS' if all(checks) else 'FAIL'} {held}/{len(checks)} pre-registered predictions held (P4 P6 P7 refuted in detail); post-hoc {sum(ph)}/{len(ph)} held")
