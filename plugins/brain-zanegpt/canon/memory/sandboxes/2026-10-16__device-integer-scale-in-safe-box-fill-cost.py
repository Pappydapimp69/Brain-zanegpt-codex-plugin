# Sandbox: a 320x180 pixel-art frame must sit inside a 90% safe box. Compare two ways to
# pick an integer scale: floor in CSS px vs floor in device px. Count (a) devices where the
# resulting device-px scale is non-integer (breaks equal pixel blocks), (b) fill of the safe box.
import math
FW, FH = 320, 180
SAFE = 0.90
# (css width, css height, device pixel ratio) -- real common viewport/dpr pairs
DEV = [("phone-3x", 390, 844, 3.0), ("phone-2.625", 412, 915, 2.625), ("tablet-2x", 768, 1024, 2.0),
       ("laptop-1.25", 1536, 864, 1.25), ("desktop-1x", 1920, 1080, 1.0), ("small-1.5", 360, 640, 1.5)]
def fit(dev, mode):
    n, w, h, r = dev
    sw, sh = w * SAFE, h * SAFE           # safe box in css px
    if mode == "css":
        s_css = max(1, math.floor(min(sw / FW, sh / FH)))
        s_dev = s_css * r
    else:
        s_dev = max(1, math.floor(min(sw * r / FW, sh * r / FH)))
        s_css = s_dev / r
    fill = (FW * s_css) / sw if (FW * s_css) / sw > (FH * s_css) / sh else (FH * s_css) / sh
    return s_dev, fill, abs(s_dev - round(s_dev)) > 1e-9, FW * s_css > sw + 1e-9 or FH * s_css > sh + 1e-9
bad = {"css": 0, "dev": 0}; over = {"css": 0, "dev": 0}
for d in DEV:
    for m in ("css", "dev"):
        s, fill, frac, ov = fit(d, m)
        bad[m] += frac; over[m] += ov
        print("%-12s %-3s device-scale=%7.3f fill=%5.1f%% non-integer=%s overflows-safe=%s" % (d[0], m, s, 100 * fill, frac, ov))
# Prediction (before run): CSS-floor gives a non-integer device scale on 3 of 6 devices
# (dpr 2.625, 1.25, 1.5); device-floor on 0; neither overflows the safe box; the cost of
# device-floor is a lower fill on at least one device (the 1x desktop is equal).
print("non-integer css=%d dev=%d; overflow css=%d dev=%d" % (bad["css"], bad["dev"], over["css"], over["dev"]))
ok = bad["css"] == 3 and bad["dev"] == 0 and over["css"] == 0 and over["dev"] == 0
print("RESULT: %s css-floor non-integer on %d of 6, device-floor on %d of 6, overflow %d/%d"
      % ("PASS" if ok else "FAIL", bad["css"], bad["dev"], over["css"], over["dev"]))
