"""Sandbox: a named style's rule list, run as a linter on the final framebuffer.

Sources composed:
 - path:  Bayer 4x4 ordered dither anchored to world space (pattern must not swim on pan)
 - path:  render at native low resolution, then nearest-neighbour blit at an integer scale
 - companion: a style is a short list of rules (Game Boy: exactly 4 shades on one pixel grid)
Question: if the Game Boy rules are written as checks on the final screen image, does each
pipeline-order mistake trip a distinct rule (so the lint localizes the bug), and does the
pixel-art kernel's own example (Shovel Knight at 4.5x) pass the integer-scale rule?

Rules checked on the final framebuffer:
 R1 palette : every screen pixel is one of 4 shades {0, 1/3, 2/3, 1}
 R2 grid    : every art pixel is drawn as an identical, uniform block (equal widths/heights)
 R3 world   : panning the camera 2 art px shifts the screen image exactly 2*scale px
              (no pixel of overlapping world content changes)
Pure stdlib, deterministic.
"""
import math

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
SHADES = [0.0, 1 / 3, 2 / 3, 1.0]
NW, NH = 48, 24          # native resolution

def world(wx, wy):
    """Scene in world coordinates: a sky gradient plus a dark 6x6 crate."""
    if 20 <= wx < 26 and 12 <= wy < 18:
        return 0.1
    return (wx % 96) / 95.0

def dither4(v, x, y):
    """4-shade ordered dither: base shade plus Bayer threshold on the fractional part."""
    t = v * 3
    base = min(int(t), 2)
    frac = t - base
    up = frac > (BAYER[y & 3][x & 3] + 0.5) / 16
    return SHADES[base + (1 if up else 0)]

def native(cam, anchor="world"):
    img = []
    for y in range(NH):
        row = []
        for x in range(NW):
            wx = x + cam
            ax = wx if anchor == "world" else x
            row.append(dither4(world(wx, y), ax, y))
        img.append(row)
    return img

def blit_nearest(img, s):
    H, W = len(img), len(img[0])
    SW, SH = int(W * s), int(H * s)
    return [[img[min(int(y / s), H - 1)][min(int(x / s), W - 1)] for x in range(SW)] for y in range(SH)]

def blit_bilinear(img, s):
    H, W = len(img), len(img[0])
    out = []
    for y in range(int(H * s)):
        fy = (y + 0.5) / s - 0.5; y0 = max(0, min(H - 1, math.floor(fy))); y1 = min(H - 1, y0 + 1); ty = min(max(fy - y0, 0), 1)
        row = []
        for x in range(int(W * s)):
            fx = (x + 0.5) / s - 0.5; x0 = max(0, min(W - 1, math.floor(fx))); x1 = min(W - 1, x0 + 1); tx = min(max(fx - x0, 0), 1)
            a = img[y0][x0] * (1 - tx) + img[y0][x1] * tx
            b = img[y1][x0] * (1 - tx) + img[y1][x1] * tx
            row.append(a * (1 - ty) + b * ty)
        out.append(row)
    return out

def screen_res_dither(cam, s):
    """Upscale the continuous scene first, then dither per SCREEN pixel (screen-anchored)."""
    SW, SH = int(NW * s), int(NH * s)
    return [[dither4(world(int(x / s) + cam, int(y / s)), x, y) for x in range(SW)] for y in range(SH)]

def r1_palette(fb):
    # (run 1 compared 6-decimal rounded values against exact thirds with 1e-9 and flagged every
    #  frame; tolerance is now 1e-6)
    vals = {round(v, 6) for row in fb for v in row}
    bad = [v for v in vals if all(abs(v - s) > 1e-6 for s in SHADES)]
    return len(bad) == 0, len(vals)

def r2_grid(fb, s):
    """Each art pixel must map to the same screen width and height, and be uniform inside."""
    widths = {}
    for x in range(len(fb[0])):
        ax = int(x / s); widths[ax] = widths.get(ax, 0) + 1
    wset = set(widths.values())
    nonuniform = 0
    for ay in range(NH):
        for ax in range(NW):
            ys = [y for y in range(len(fb)) if int(y / s) == ay]
            xs = [x for x in range(len(fb[0])) if int(x / s) == ax]
            if len({fb[y][x] for y in ys for x in xs}) > 1:
                nonuniform += 1
    return (len(wset) == 1 and nonuniform == 0), sorted(wset), nonuniform

def r3_world(fb0, fb1, s, pan=2):
    """fb1 is rendered with camera + pan. World content must be fb0 shifted left by pan*s px."""
    sh = pan * s
    if sh != int(sh):
        return None, None
    sh = int(sh); diff = tot = 0
    m = int(math.ceil(s))  # skip one art pixel at each screen edge (filter clamping, run 1 artifact)
    for y in range(len(fb0)):
        for x in range(m, len(fb0[0]) - sh - m):
            tot += 1; diff += fb0[y][x + sh] != fb1[y][x]
    return diff == 0, diff / tot

def lint(name, make, s):
    fb0, fb1 = make(0), make(2)
    p1, nshades = r1_palette(fb0)
    p2, widths, nonuni = r2_grid(fb0, s)
    p3, flip = r3_world(fb0, fb1, s)
    if p3 is None:  # half-integer scale: pan by 4 art px instead so the screen shift is whole
        fb2 = make(4); p3, flip = r3_world(fb0, fb2, s, pan=4)
    fails = [r for r, p in (("R1", p1), ("R2", p2), ("R3", p3)) if not p]
    print(f"  {name:34s} R1 {'ok ' if p1 else 'BAD'} ({nshades} values)  R2 {'ok ' if p2 else 'BAD'} "
          f"(widths {widths}, non-uniform art px {nonuni})  R3 {'ok ' if p3 else 'BAD'} (changed {flip:.3f})")
    return fails, nshades, widths, nonuni, flip

print("Game Boy rule lint on the final framebuffer (scale 4 unless noted):")
P = {}
P["P0 native world dither, nearest x4"] = lint("P0 native world dither, nearest x4", lambda c: blit_nearest(native(c), 4), 4)
P["P1 native world dither, BILINEAR x4"] = lint("P1 native world dither, BILINEAR x4", lambda c: blit_bilinear(native(c), 4), 4)
P["P2 dither at SCREEN res after x4"] = lint("P2 dither at SCREEN res after x4", lambda c: screen_res_dither(c, 4), 4)
P["P3 native SCREEN-anchored dither, x4"] = lint("P3 native SCREEN-anchored dither, x4", lambda c: blit_nearest(native(c, "screen"), 4), 4)
P["P4 BREAK Shovel-Knight nearest x4.5"] = lint("P4 BREAK Shovel-Knight nearest x4.5", lambda c: blit_nearest(native(c), 4.5), 4.5)

# S6 (added after run 1) the pan size itself: a pan equal to the Bayer period hides swimming
fa, fb_ = blit_nearest(native(0, "screen"), 4), blit_nearest(native(4, "screen"), 4)
p3_pan4 = r3_world(fa, fb_, 4, pan=4)[1]
fa, fb_ = blit_nearest(native(0, "screen"), 4), blit_nearest(native(1, "screen"), 4)
p3_pan1 = r3_world(fa, fb_, 4, pan=1)[1]
fa, fb_ = screen_res_dither(0, 4), screen_res_dither(1, 4)
p2_pan1 = r3_world(fa, fb_, 4, pan=1)[1]
print(f"  S6 screen-anchored native dither: pan 1 art px changed {p3_pan1:.3f}, pan 4 (= Bayer period) changed {p3_pan4:.3f}; "
      f"screen-res dither at x4, pan 1 art px (4 screen px) changed {p2_pan1:.3f}")

# 17-level sanity of the 2-colour Bayer (kernel claim)
levels = {sum(1 for y in range(4) for x in range(4) if v > (BAYER[y][x] + 0.5) / 16) for v in [i / 64 for i in range(65)]}
print(f"  two-colour Bayer 4x4 distinct coverage levels: {len(levels)}")

f = {k: v[0] for k, v in P.items()}
checks = {
    "P0 passes all rules": f["P0 native world dither, nearest x4"] == [],
    "P1 fails R1 only": f["P1 native world dither, BILINEAR x4"] == ["R1"],
    "P2 fails R2 (and R3)": "R2" in f["P2 dither at SCREEN res after x4"] and "R1" not in f["P2 dither at SCREEN res after x4"],
    "P3 fails R3 only, >30% changed": f["P3 native SCREEN-anchored dither, x4"] == ["R3"] and P["P3 native SCREEN-anchored dither, x4"][4] > 0.30,
    "P4 fails R2 only, widths {4,5}": f["P4 BREAK Shovel-Knight nearest x4.5"] == ["R2"] and P["P4 BREAK Shovel-Knight nearest x4.5"][2] == [4, 5],
    "Bayer 17 levels": len(levels) == 17,
}
for k, v in checks.items():
    print(f"  {'ok ' if v else 'MISS'} {k}")
summary = "; ".join(f"{k.split()[0]} fails {v[0] or 'none'}" for k, v in P.items())
print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} {summary}; bilinear {P['P1 native world dither, BILINEAR x4'][1]} values, "
      f"screen-anchored pan changed {P['P3 native SCREEN-anchored dither, x4'][4]:.3f}, x4.5 widths {P['P4 BREAK Shovel-Knight nearest x4.5'][2]}; pan of 4 art px hides swim ({p3_pan4:.3f}); Bayer {len(levels)} levels")
