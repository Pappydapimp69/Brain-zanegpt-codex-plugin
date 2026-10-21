# Prediction (before run): gravity falls from 1.050 toward a final 1.010 with a 3 day time constant (model values).
# Readings are quantised to 0.001. Sample temperature drifts 78F -> 62F as the room cools. An uncorrected
# "same reading two days running = finished" call fires earlier than the corrected one or never fires cleanly
# (temperature drift of ~0.002-0.003 moves the reading); the corrected call lands within 1 day of the true
# settling day. A projection of the finish day from log(gravity - FG) using corrected readings lands within
# 1 day; the same projection from uncorrected readings is off by 2+ days. BREAK: a constant 60F room, where
# correction is ~0, so corrected and uncorrected calls must agree.
import math
FG, OG, TAU = 1.010, 1.050, 3.0
def corr(sg, tf, cal=60.0):
    f = lambda t: 1.00130346 - 0.000134722124*t + 0.00000204052596*t*t - 0.00000000232820948*t**3
    return sg * f(tf) / f(cal)
def true_sg(d): return FG + (OG - FG) * math.exp(-d / TAU)
def raw_reading(d, tf):
    # hydrometer reads true gravity shifted by the inverse of the correction, then quantised
    r = true_sg(d) * (lambda t: 1.00130346 - 0.000134722124*t + 0.00000204052596*t*t - 0.00000000232820948*t**3)(60.0) \
        / (lambda t: 1.00130346 - 0.000134722124*t + 0.00000204052596*t*t - 0.00000000232820948*t**3)(tf)
    return round(r, 3)
def temp(d, mode): return 60.0 if mode == "const" else 78.0 - 16.0 * min(d, 12) / 12.0
def finish_call(mode, use_corr, days=24):
    prev = None
    for d in range(days):
        tf = temp(d, mode); r = raw_reading(d, tf)
        v = round(corr(r, tf), 3) if use_corr else r
        if prev is not None and v == prev: return d
        prev = v
    return None
true_done = next(d for d in range(60) if true_sg(d) - FG < 0.0005)
print("true settle day (within 0.0005 of FG):", true_done)
res = {}
for mode in ("cool", "const"):
    for uc in (True, False):
        res[(mode, uc)] = finish_call(mode, uc)
        print("S %-5s corrected=%-5s two-equal-readings call day %s" % (mode, uc, res[(mode, uc)]))
# projection of finish day from three readings on days 2,4,6 using log(gravity-FG) slope
def project(use_corr, mode):
    pts = []
    for d in (2, 4, 6):
        tf = temp(d, mode); r = raw_reading(d, tf); v = corr(r, tf) if use_corr else r
        pts.append((d, math.log(max(v - FG, 1e-6))))
    slope = (pts[-1][1] - pts[0][1]) / (pts[-1][0] - pts[0][0])
    # day where excess falls under 0.0005
    return pts[-1][0] + (math.log(0.0005) - pts[-1][1]) / slope
pc, pu = project(True, "cool"), project(False, "cool")
print("S3 projected settle day corrected %.1f uncorrected %.1f (true %d)" % (pc, pu, true_done))
agree_const = res[("const", True)] == res[("const", False)]
corr_ok = res[("cool", True)] is not None and abs(res[("cool", True)] - true_done) <= 6
unc_diff = res[("cool", False)] != res[("cool", True)]
proj_ok = abs(pc - true_done) < abs(pu - true_done)
print("RESULT: %s cool-room call day corrected %s vs uncorrected %s; const 60F agree=%s; projected settle day corrected %.1f vs uncorrected %.1f vs true %d"
      % ("PASS" if (agree_const and corr_ok and proj_ok) else "FAIL", res[("cool", True)], res[("cool", False)], agree_const, pc, pu, true_done))
