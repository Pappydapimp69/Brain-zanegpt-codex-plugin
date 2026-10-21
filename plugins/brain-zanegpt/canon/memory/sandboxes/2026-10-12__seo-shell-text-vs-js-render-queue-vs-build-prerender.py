"""Sandbox: three DISTRIBUTION/seo kernels on a toy crawler. Deterministic day-stepped model, no RNG, no clock.
 K1 googlebot-two-phase-crawl-put-text-in-the-shell  K2 prerender-at-build-not-dynamic-render
 K3 dont-overinvest-at-hobby-scale (canonical tag worth it when one page has several URLs; sitemap marginal for 1 URL)
Model (all numbers are ASSUMED parameters, the sandbox shows structure, not Google's real queue):
 phase 1 (day 1): every discovered page is fetched, raw-HTML text is indexed at once.
 phase 2: JS pages enter a FIFO render queue; R pages rendered per day after a fixed lag L days.
PREDICTION (written before run 1):
 P1 200-page JS-only site, R=5/day, L=0: full coverage on day 40 (ceil(200/5)); shell/prerender text on day 1; median JS page waits ~20 days.
 P2 single-page hobby site: JS text is indexed after L=7 days, shell text on day 1; BREAK: with L=0 and R>=1 the gap is 1 day (the render happens in the next day's pass), i.e. the kernel's advantage is the lag, not JS itself.
 P3 a crawler that never executes JS (GPTBot-style) indexes 0% of JS-only text at any horizon, 100% of shell and prerender text.
 P4 prerender is not free: content changing every 1 day with a 7-day build gives a stale snapshot on ~86% of days; changing every 30 days gives a stale share in 8%..16%; B=1 gives 0%.
 P5 one page reachable at 4 URL variants: 4 indexed duplicates without a canonical, 1 with it; a sitemap changes nothing for a 1-page site (discovery already day 1).
"""
import math
ok = True
def render_day(page_idx, R, L):  # page_idx 0-based in discovery order, rendered FIFO R/day after lag L, available next day
    return 1 + L + page_idx // R + 1   # phase 2 completes the day after its slot, phase 1 text is day 1
# S1
P, R, L = 200, 5, 0
days = [render_day(i, R, L) for i in range(P)]
full = max(days); med = sorted(days)[P // 2]
print("S1 200 JS pages R=5 L=0: full coverage day %d, median page day %d ; shell/prerender: day 1" % (full, med))
ok &= 40 <= full <= 42 and 18 <= med <= 23
# S2
d7, d0 = render_day(0, 1, 7), render_day(0, 5, 0)
print("S2 single page: JS day %d at L=7 vs shell day 1 ; at L=0 JS day %d (gap %d)" % (d7, d0, d0 - 1))
ok &= d7 - 1 >= 7 and d0 - 1 == 1
# S3
def indexed(kind, executes_js): return 1.0 if kind in ("shell", "prerender") else (1.0 if executes_js else 0.0)
res = {(k, js): indexed(k, js) for k in ("js", "shell", "prerender") for js in (True, False)}
print("S3 no-JS crawler indexes: js %.0f%% shell %.0f%% prerender %.0f%% ; JS-capable on js-only %.0f%%" % (100 * res[("js", False)], 100 * res[("shell", False)], 100 * res[("prerender", False)], 100 * res[("js", True)]))
ok &= res[("js", False)] == 0 and res[("shell", False)] == 1 and res[("prerender", False)] == 1
# S4
def stale_share(B, c, horizon=3600):
    stale = 0
    for t in range(horizon):
        last_build = (t // B) * B
        last_change = (t // c) * c
        stale += last_change > last_build   # the live content changed after the snapshot was built
    return stale / horizon
s1, s7a, s7b, s30 = stale_share(1, 1), stale_share(7, 1), stale_share(7, 30), stale_share(30, 1)
print("S4 stale-snapshot share: B=1,c=1 %.3f ; B=7,c=1 %.3f ; B=7,c=30 %.3f ; B=30,c=1 %.3f" % (s1, s7a, s7b, s30))
ok &= s1 == 0 and .83 <= s7a <= .89 and .08 <= s7b <= .16
# S5
urls = ["https://a.github.io/g/", "https://a.github.io/g", "https://a.dev/g/", "https://a.dev/g"]
no_canon = len(set(urls)); with_canon = len({"https://a.dev/g/" for _ in urls})
disc_nositemap, disc_sitemap = 1, 1
print("S5 URL variants indexed: no canonical %d, canonical %d ; discovery day single page: no sitemap %d, sitemap %d" % (no_canon, with_canon, disc_nositemap, disc_sitemap))
ok &= no_canon == 4 and with_canon == 1
print("RESULT: %s JS-only text lags by queue (200 pages: day %d vs day 1) and never appears for no-JS bots; the gap is just the lag at one page (L=0 -> 1 day); build prerender goes stale %.0f%%/%.0f%% of days at a 7-day build; canonical cuts 4 duplicates to 1" % ("PASS" if ok else "FAIL", full, 100 * s7a, 100 * s7b))
