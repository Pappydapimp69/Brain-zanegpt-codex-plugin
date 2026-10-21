"""Loop 4 pass 2 (new half). Path: Bayer 4x4 world-anchored dither + tension-as-information-gap
(the reveal is rationed in 16 equal beats). Companion: broadcast safe zones applied to a letterboxed
viewport. Question: if the safe-title rule is applied the easy way - shrink the whole letterboxed
canvas to 90% so everything is title-safe - what happens to a world-anchored dither reveal?
Model: 320x180 source art, nearest-neighbour upscale to the screen at scale s with letterbox offset.
A clue patch (8x8 source px) is revealed by raising its Bayer level 0..16 (one beat per level).
Per beat we measure the SCREEN pixels newly lit; the discourse claim needs equal beats.
Swim = screen pixels of the patch that change when the camera scrolls 1 source px with the level fixed
(world anchor should give 0 at integer scale). Shimmer = spread of the patch's screen tone at one
level as the camera scrolls 0..7 source px (added after run 1: swim is counted in source px, which
a non-integer scale cannot disturb, so it alone could not show a screen-space effect). Pure stdlib, deterministic.
PREDICTION (written before running): integer scale 6: beat ratio max/min 1.00, tone error 0, swim 0
for world anchor (screen anchor swim > 0). Safe-shrink scale 5.4: beat ratio > 1.2 and tone error
> 0.01 for some camera offset, swim > 0 even world-anchored. Floor to integer scale 5 inside the
safe box restores ratio 1.00 / error 0 / swim 0. Phone fit s=1.21875: beat ratio >= 2."""
from fractions import Fraction as F
M = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
SW, SH = 320, 180
PATCH = (100, 60, 8, 8)            # world x, y, w, h of the clue (source px)

def lit_source(level, wx, wy, cam, anchor):
    """Is source pixel (world wx,wy) lit at this level? World anchor indexes M by world coords,
    screen anchor by camera-relative coords (sx = wx - cam)."""
    ax = wx if anchor == "world" else wx - cam
    return M[wy & 3][ax & 3] < level   # level k lights exactly k of 16 cells per tile

def screen_cols(s, ox, sx):
    """Screen columns that nearest-neighbour maps to source column sx: X with floor((X+0.5-ox)/s)==sx."""
    lo = s * sx + ox - F(1, 2); hi = s * (sx + 1) + ox - F(1, 2)
    import math
    a = math.ceil(lo); b = math.ceil(hi)       # X in [a, b)
    return b - a

def patch_screen(level, s, ox, oy, cam, anchor):
    """Set of lit screen pixels of the patch, as {(sx, sy): weight} -> total lit area and per-pixel map."""
    x0, y0, w, h = PATCH
    lit = {}
    for wy in range(y0, y0 + h):
        for wx in range(x0, x0 + w):
            sx = wx - cam                      # camera scroll in source px
            if lit_source(level, wx, wy, cam, anchor):
                lit[(sx, wy)] = screen_cols(s, ox, sx) * screen_cols(s, oy, wy)
    return lit

def area_total(s, ox, oy, cam):
    x0, y0, w, h = PATCH
    return sum(screen_cols(s, ox, wx - cam) * screen_cols(s, oy, wy) for wy in range(y0, y0 + h) for wx in range(x0, x0 + w))

def analyse(name, s, W, H, anchor="world"):
    s = F(s)
    ox = (W - s * SW) / 2; oy = (H - s * SH) / 2
    ratios, errs, swims = [], [], []
    tones = {}
    for cam in range(8):
        tot = area_total(s, ox, oy, cam)
        prev = 0; beats = []
        for k in range(1, 17):
            a = sum(patch_screen(k, s, ox, oy, cam, anchor).values())
            beats.append(a - prev); prev = a
            errs.append(abs(F(a, tot) - F(k, 16))); tones.setdefault(k, []).append(F(a, tot))
        ratios.append(F(max(beats), min(beats)))
        # swim: level 8 frozen, camera moves cam -> cam+1; compare lit pattern in WORLD terms
        p0 = patch_screen(8, s, ox, oy, cam, anchor); p1 = patch_screen(8, s, ox, oy, cam + 1, anchor)
        w0 = {(sx + cam, sy) for sx, sy in p0}; w1 = {(sx + cam + 1, sy) for sx, sy in p1}
        swims.append(len(w0 ^ w1))
    r = float(max(ratios)); e = float(max(errs)); sw = max(swims)
    sh = float(max(max(v) - min(v) for v in tones.values()))   # same level, camera scrolls 0..7 px
    print(f"{name:34s} s={float(s):7.4f} anchor={anchor:6s} beat max/min={r:5.2f} tone err={e:.4f} swim(src px)={sw:2d} shimmer={sh:.4f}")
    return r, e, sw, sh

res = {}
res["int6"] = analyse("1920x1080 integer fit", 6, 1920, 1080)
res["int6_screen"] = analyse("1920x1080 integer fit", 6, 1920, 1080, "screen")
res["safe54"] = analyse("1920x1080 shrunk to 90% title-safe", F(54, 10), 1920, 1080)
res["floor5"] = analyse("1920x1080 floor(5.4)=5 inside safe", 5, 1920, 1080)
res["laptop"] = analyse("1366x768 fit (768/180)", F(768, 180), 1366, 768)
res["phone"] = analyse("390x844 portrait fit", F(390, 320), 390, 844)
res["phone_safe"] = analyse("390x844 fit then 90%", F(390, 320) * F(9, 10), 390, 844)
ok = (res["int6"] == (1.0, 0.0, 0, 0.0) and res["int6_screen"][2] > 0 and res["safe54"][0] > 1.2 and res["safe54"][1] > 0.01
      and res["floor5"] == (1.0, 0.0, 0, 0.0) and res["safe54"][3] > 0 and res["phone"][0] >= 2)
print(f"RESULT: {'PASS' if ok else 'FAIL'} integer s6 beats 1.00/err 0/swim 0 (screen-anchor swim {res['int6_screen'][2]}); "
      f"90% safe-shrink s5.4 beats {res['safe54'][0]:.2f}x err {res['safe54'][1]:.4f} swim {res['safe54'][2]} shimmer {res['safe54'][3]:.4f}; "
      f"floor s5 {res['floor5'][0]:.2f}x; phone s1.22 beats {res['phone'][0]:.2f}x err {res['phone'][1]:.4f}")
