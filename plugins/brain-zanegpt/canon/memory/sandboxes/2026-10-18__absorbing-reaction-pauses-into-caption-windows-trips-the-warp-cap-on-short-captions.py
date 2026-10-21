# Composes brain-film-explainer/E2 (stretching a caption window slows every animation in it; keep per-scene warp near
# 1.5), reaction-cut-pause-placement/E1 (reaction pauses snap to the caption end) and caption-warp-cap-before-ipm-d1-
# ranking/E1 (cap warp at 1.5 before ranking; the cap pays only when the D1 loss per +0.1 warp over 1.5 is steep).
# Added: two ways to add a 2.0 s reaction pause after each of 7 caption ends in a 120 s film with 8 captions:
#   HOLD   - insert a still hold; warp stays 1.0 but the runtime grows by 14 s;
#   ABSORB - stretch the caption window by the pause; warp_i = (w_i + 2) / w_i, runtime unchanged.
# Value = IPM x D1. IPM falls 0.4% per second of runtime over 120 s; D1 = 0.40 - slope * max over captions of
# max(0, (warp - 1.5)/0.1). Windows (s): 2.5 3 4 6 8 10 14 18 (the last gets no pause).
# PREDICTION (before run): ABSORB pushes exactly 2 captions over warp 1.5 (the 2.5 s and the 3 s ones) with a worst warp
# of 1.8; HOLD adds 14 s (+11.7%) and no warp; at slope 0.005 ABSORB wins, at slope 0.05 HOLD wins, with the crossover
# between 0.02 and 0.05; BREAK: a pause of 0.5 s makes ABSORB's worst warp 1.2 so ABSORB wins at every slope tested.
W = [2.5, 3, 4, 6, 8, 10, 14, 18]
def worst_warp(pause): return max((w + pause) / w for w in W[:-1])
def n_over(pause): return sum(1 for w in W[:-1] if (w + pause) / w > 1.5 + 1e-9)
def value(mode, pause, slope):
    runtime = 120 + (7 * pause if mode == "hold" else 0)
    ipm = 6.0 * (1 - 0.004 * (runtime - 120))
    ww = 1.0 if mode == "hold" else worst_warp(pause)
    d1 = 0.40 - slope * max(0.0, (ww - 1.5) / 0.1)
    return ipm * d1
print(f"pause 2.0: ABSORB captions over 1.5 = {n_over(2.0)}, worst warp {worst_warp(2.0):.2f}; HOLD adds {7*2.0:.0f} s ({7*2.0/120*100:.1f}%)")
cross = None
for slope in (0.005, 0.01, 0.02, 0.03, 0.05, 0.1):
    h, a = value("hold", 2.0, slope), value("absorb", 2.0, slope)
    print(f"slope {slope}: hold {h:.3f} absorb {a:.3f} winner {'hold' if h > a else 'absorb'}")
    if cross is None and h > a: cross = slope
brk = [value("absorb", 0.5, s) >= value("hold", 0.5, s) for s in (0.005, 0.02, 0.05, 0.1)]
lo = value("absorb", 2.0, 0.005) > value("hold", 2.0, 0.005); hi = value("hold", 2.0, 0.05) > value("absorb", 2.0, 0.05)
ok = n_over(2.0) == 2 and abs(worst_warp(2.0) - 1.8) < 1e-9 and lo and hi and cross is not None and 0.02 < cross <= 0.05 and all(brk)
print(f"RESULT: {'PASS' if ok else 'FAIL'} ABSORB over-cap captions {n_over(2.0)} (worst warp {worst_warp(2.0):.2f}); ABSORB wins at slope 0.005 {lo}, HOLD wins at 0.05 {hi}; first HOLD win at slope {cross}; 0.5 s pause ABSORB wins at all slopes {all(brk)}")
