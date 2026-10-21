"""Sandbox: Bayer 4x4 world-anchored dither + one-grid integer scale (render low-res, nearest-neighbour blit) +
safe zones for a cropped / letterboxed viewport (safe-area-inset on notched screens, 90% title-safe).
Goes past 2026-10-15 safe-zone-shrink (E16), which left devicePixelRatio out: on the web the layout, the safe-area
insets and 'integer scale' are all in CSS px, while nearest-neighbour happens in DEVICE px.

Model: 320x180 source, clue patch 8x8 source px revealed by Bayer level 1..16. Device column widths for source
column x at device scale s and device origin o: number of device pixel centres k+0.5 in [s*x+o, s*(x+1)+o).
Camera scrolls 0..7 source px (world-anchored matrix). Metrics: column-width ratio max/min (mixels), beat ratio
max/min of newly lit device area per level, tone shimmer (spread of lit fraction at one level over camera offsets),
and the share of the safe rect the image fills. Device sizes and insets are stand-ins, not measured hardware.

Policies: A 'CSS integer': s_css = floor(fit in safe rect, CSS px), device scale = s_css * DPR.
          B 'device integer': s_dev = floor(fit in safe rect * DPR), image CSS size = 320*s_dev/DPR.
          C 'contain': fractional fit of the safe rect (CSS object-fit), device scale = fit * DPR.
Origin = safe-rect left/top inset in CSS px * DPR + centring, so it can be a fractional device pixel.

PREDICTION (written before the first run). Hidden assumption: an integer scale computed in layout (CSS) units is an
integer on the glass. Proof it is wrong: policy A shows mixels at DPR 1.25 / 1.5 / 2.625.
 P1 A at DPR 1 / 2 / 3 gives width ratio 1.00, beat ratio 1.00, shimmer 0 (control).
 P2 A at DPR 1.25 (Windows 125%, CSS 1536x864) gives width ratio >= 1.2 and nonzero shimmer; at DPR 2.625 too.
 P3 B gives width ratio 1.00 / beat 1.00 / shimmer 0 on every device, including a fractional device origin from
    the safe-area inset (built to BREAK B: a fractional origin might split columns unevenly).
 P4 B costs fill: on the portrait phone B and A fill the same; on DPR 1.25 B fills at least as much as A.
"""
from fractions import Fraction as Fr
import math
M = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
SW, SH = 320, 180
PX, PY, PW, PH = 100, 60, 8, 8

def width(s, o, x):
    lo, hi = s * x + o - Fr(1, 2), s * (x + 1) + o - Fr(1, 2)
    return math.ceil(hi) - math.ceil(lo)

def analyse(s, ox, oy):
    wr, br, tones = [], [], {}
    for cam in range(8):
        cols = {wx: width(s, ox, wx - cam) for wx in range(PX - 4, PX + PW + 4)}
        rows = {wy: width(s, oy, wy) for wy in range(PY, PY + PH)}
        ws = [width(s, ox, x) for x in range(SW)] + [width(s, oy, y) for y in range(SH)]
        wr.append(Fr(max(ws), min(ws)))
        tot = sum(cols[wx] * rows[wy] for wx in range(PX, PX + PW) for wy in range(PY, PY + PH))
        prev, beats = 0, []
        for k in range(1, 17):
            a = sum(cols[wx] * rows[wy] for wx in range(PX, PX + PW) for wy in range(PY, PY + PH) if M[wy & 3][wx & 3] < k)
            beats.append(a - prev); prev = a
            tones.setdefault(k, []).append(Fr(a, tot))
        br.append(Fr(max(beats), min(beats)))
    sh = max(max(v) - min(v) for v in tones.values())
    return float(max(wr)), float(max(br)), float(sh)

# name: CSS viewport w,h ; DPR ; safe insets CSS px (l, r, t, b) ; title-safe 90% applied on top?
DEV = [
    ("desktop 1920x1080 @1", 1920, 1080, Fr(1), (0, 0, 0, 0)),
    ("win laptop 125% 1536x864", 1536, 864, Fr(5, 4), (0, 0, 0, 0)),
    ("win laptop 150% 1280x720", 1280, 720, Fr(3, 2), (0, 0, 0, 0)),
    # added after run 1: at 1536x864 the CSS floor 4 times 1.25 happened to be the integer 5
    ("win 125% 1280x720 (1600x900 panel)", 1280, 720, Fr(5, 4), (0, 0, 0, 0)),
    # added after run 2: the 1600x900 panel also gave CSS scale 4 (4 x 1.25 = 5); a 1280x720 panel at 125% gives 3
    ("win 125% 1024x576 (1280x720 panel)", 1024, 576, Fr(5, 4), (0, 0, 0, 0)),
    ("retina 1440x900 @2", 1440, 900, Fr(2), (0, 0, 0, 0)),
    ("android land 891x411 @2.625", 891, 411, Fr(21, 8), (32, 32, 0, 0)),
    ("iphone land 844x390 @3", 844, 390, Fr(3), (47, 47, 0, 21)),
    ("iphone portrait 390x844 @3", 390, 844, Fr(3), (0, 0, 47, 34)),
    ("android portrait 411x891 @2.625", 411, 891, Fr(21, 8), (0, 0, 32, 24)),
]

def place(cssW, cssH, dpr, ins, scale_css):
    l, r, t, b = ins
    sw_, sh_ = cssW - l - r, cssH - t - b
    imgW, imgH = SW * scale_css, SH * scale_css
    ox_css = l + (sw_ - imgW) / 2; oy_css = t + (sh_ - imgH) / 2
    fill = float((imgW * imgH) / (sw_ * sh_))
    return ox_css * dpr, oy_css * dpr, fill

rows, out = [], {}
for name, W, H, dpr, ins in DEV:
    l, r, t, b = ins
    fit = min(Fr(W - l - r, SW), Fr(H - t - b, SH))
    sA = Fr(max(1, math.floor(fit)))
    sB_dev = Fr(max(1, math.floor(fit * dpr)))
    res = {}
    for pol, s_css in (("A", sA), ("B", sB_dev / dpr), ("C", fit)):
        ox, oy, fill = place(W, H, dpr, ins, s_css)
        s_dev = s_css * dpr
        m = analyse(s_dev, ox, oy)
        res[pol] = (float(s_dev), m, fill, float(ox) % 1 != 0 or float(oy) % 1 != 0)
        print("%-32s %s dev scale %7.4f  width ratio %.2f  beat %.2f  shimmer %.4f  fill %.2f%s"
              % (name, pol, float(s_dev), m[0], m[1], m[2], fill, "  (fractional device origin)" if res[pol][3] else ""))
    out[name] = res

g = lambda n, p: out[n][p][1]
ok = {}
ok["P1"] = all(g(n, "A") == (1.0, 1.0, 0.0) for n in ("desktop 1920x1080 @1", "retina 1440x900 @2", "iphone land 844x390 @3", "iphone portrait 390x844 @3"))
ok["P2"] = g("win laptop 125% 1536x864", "A")[0] >= 1.2 and g("win laptop 125% 1536x864", "A")[2] > 0 and g("android land 891x411 @2.625", "A")[0] >= 1.2
ok["P3"] = all(out[n]["B"][1] == (1.0, 1.0, 0.0) for n in out)
frac_origin_B = [n for n in out if out[n]["B"][3]]
ok["P4"] = abs(out["iphone portrait 390x844 @3"]["A"][2] - out["iphone portrait 390x844 @3"]["B"][2]) < 1e-12 and \
           out["win laptop 125% 1536x864"]["B"][2] >= out["win laptop 125% 1536x864"]["A"][2]
print("fractional device origin under B:", frac_origin_B)
print("checks", ok)
w125 = out["win laptop 125% 1536x864"]; a26 = out["android land 891x411 @2.625"]; p26 = out["android portrait 411x891 @2.625"]
x = out["win 125% 1280x720 (1600x900 panel)"]
print("added after run 1: 125%% on a 1600x900 panel: A s%.2f width %.2f beat %.2f shimmer %.4f fill %.2f | B s%.0f fill %.2f"
      % (x["A"][0], x["A"][1][0], x["A"][1][1], x["A"][1][2], x["A"][2], x["B"][0], x["B"][2]))
y = out["win 125% 1024x576 (1280x720 panel)"]
print("added after run 2: 125%% on a 1280x720 panel: A s%.2f width %.2f beat %.2f shimmer %.4f fill %.2f | B s%.0f fill %.2f"
      % (y["A"][0], y["A"][1][0], y["A"][1][1], y["A"][1][2], y["A"][2], y["B"][0], y["B"][2]))
print("RESULT: %s CSS-integer at DPR1/2/3 exact; 125%%: A s%.2f width %.2f beat %.2f shimmer %.4f fill %.2f vs B s%.0f exact fill %.2f; android 2.625 land A width %.2f shimmer %.4f; B exact on all %d devices incl %d with fractional device origin; portrait 2.625 B fill %.2f vs A %.2f; 125%% 1280x720 panel A s%.2f width %.2f beat %.2f shimmer %.4f"
      % ("PASS" if all(ok.values()) else "FAIL", w125["A"][0], w125["A"][1][0], w125["A"][1][1], w125["A"][1][2], w125["A"][2], w125["B"][0], w125["B"][2],
         a26["A"][1][0], a26["A"][1][2], len(out), len(frac_origin_B), p26["B"][2], p26["A"][2], y["A"][0], y["A"][1][0], y["A"][1][1], y["A"][1][2]))
