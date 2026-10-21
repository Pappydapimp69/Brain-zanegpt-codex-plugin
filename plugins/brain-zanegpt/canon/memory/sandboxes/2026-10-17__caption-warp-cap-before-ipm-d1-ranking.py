# Run 1 prediction (missed): uncapped IPM x D1 picks warp>1.5 recuts in >=2/4 sheets and capping never loses.
# Run 1 observed: weak penalty (0.12 D1 per unit warp over 1.5) -> 1/4 and the cap LOST in sheet 2 (2.352 vs 2.502).
# Run 2 prediction (written after run 1): the cap pays only when the real D1 penalty is steep. Sweeping the
# D1 loss per +0.1 warp over 1.5 over 0.005,0.02,0.05,0.1,0.2: capped total beats uncapped total only from
# a slope between 0.02 and 0.1 upward, and at the weakest slope the cap loses. BREAK: sheet 4 (short captions).
def run(slope):
    sheets = [[8, 14, 20, 26, 12], [10, 18, 24, 28, 16], [6, 22, 25, 27, 13], [6, 8, 10, 12, 14], [12, 30, 33, 16, 9]]
    tot_nocap = tot_cap = 0.0
    for s in sheets:
        vs = []
        for w in s:
            warp = max(1.0, w / 18.0); ipm = 3.0 + 0.12 * w
            d1 = max(0.0, 0.40 - slope * max(0.0, (warp - 1.5) / 0.1))
            vs.append(dict(w=w, warp=warp, ipm=ipm, val=ipm * d1))
        nominal = max(vs, key=lambda v: v["ipm"])
        capped = max([v for v in vs if v["warp"] <= 1.5], key=lambda v: v["ipm"])
        tot_nocap += nominal["val"]; tot_cap += capped["val"]
    return tot_nocap, tot_cap
cross = None
for slope in (0.005, 0.02, 0.05, 0.1, 0.2):
    a, b = run(slope)
    print("slope %.3f uncapped %.3f capped %.3f cap_wins %s" % (slope, a, b, b > a))
    if cross is None and b > a: cross = slope
lo = run(0.005); hi = run(0.2)
ok = lo[1] < lo[0] and hi[1] > hi[0] and cross is not None and 0.02 <= cross <= 0.1
print(f"RESULT: {'PASS' if ok else 'FAIL'} cap loses at slope 0.005 ({lo[1]:.2f} vs {lo[0]:.2f}), wins at 0.2 ({hi[1]:.2f} vs {hi[0]:.2f}); first winning slope {cross}")
