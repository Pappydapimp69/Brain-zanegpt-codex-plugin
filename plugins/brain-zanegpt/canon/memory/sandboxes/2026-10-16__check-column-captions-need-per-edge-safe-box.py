# Sandbox: does a game-of-the-scene check column (6 beats x X/F/J cells), shown as
# on-screen captions over 1080x1920 vertical video, stay readable under (a) the
# broadcast 90%/93% safe margins and (b) the strictest per-edge platform margins
# (120 sides, 240 top, 660 bottom) across 4 crop viewports? Deterministic, stdlib.
W, H = 1080, 1920
BEATS = 6
CELL_H = 90          # one caption row per beat
CELL_W = 700         # X cell label width
GAP = 10

def viewports():
    # visible window (x0,y0,x1,y1) of the 1080x1920 frame in each viewer
    return {
        "full_9x16": (0, 0, W, H),
        "feed_4x5": (0, 285, W, 285 + 1350),     # 1080x1350 centre crop
        "square_1x1": (0, 420, W, 420 + 1080),
        "wide_16x9_centre": (0, 656, W, 656 + 608),
    }

def overlay_ok(box, strict):
    x0, y0, x1, y1 = box
    sx, top, bot = strict
    return x0 >= sx and x1 <= W - sx and y0 >= top and y1 <= H - bot

def layout_pct(pct, anchor_bottom=True):
    m = (1 - pct) / 2
    left = int(W * m); right = W - left
    top = int(H * m); bottom = H - top
    h = BEATS * (CELL_H + GAP)
    y0 = bottom - h if anchor_bottom else top
    return [(left, y0 + i * (CELL_H + GAP), left + CELL_W, y0 + i * (CELL_H + GAP) + CELL_H) for i in range(BEATS)]

def layout_strict(strict, width=CELL_W):
    sx, top, bot = strict
    h = BEATS * (CELL_H + GAP)
    # centre vertically in the band left after the strictest top/bottom margins
    band_h = H - top - bot
    y0 = top + (band_h - h) // 2
    return [(sx, y0 + i * (CELL_H + GAP), sx + width, y0 + i * (CELL_H + GAP) + CELL_H) for i in range(BEATS)]

def score(boxes, strict):
    vps = viewports()
    shown_all = 0
    per_vp = {k: 0 for k in vps}
    ok_overlay = 0
    for b in boxes:
        ins = []
        for k, (vx0, vy0, vx1, vy1) in vps.items():
            inside = b[0] >= vx0 and b[2] <= vx1 and b[1] >= vy0 and b[3] <= vy1
            per_vp[k] += inside
            ins.append(inside)
        shown_all += all(ins)
        ok_overlay += overlay_ok(b, strict)
    return shown_all, ok_overlay, per_vp

STRICT = (120, 240, 660)
res = {}
res["title90_bottom"] = score(layout_pct(0.90), STRICT)
res["action93_bottom"] = score(layout_pct(0.93), STRICT)
res["strict_edges"] = score(layout_strict(STRICT), STRICT)
# BREAKER: strict margins but the X cell is too wide (900 px: right edge 1020 > 960)
res["strict_but_wide"] = score(layout_strict(STRICT, width=900), STRICT)
# the strict layout must also survive the crops: only central band 656..1264 for 16:9
for k, v in res.items():
    print(k, "visible_in_all_viewports=%d/6" % v[0], "clear_of_overlay=%d/6" % v[1], v[2])

# Prediction (written before run): title90 and action93 anchored at bottom show 0/6 clear
# of overlay; strict_edges clear overlay 6/6 but show in all 4 crops only for beats
# inside y 656..1264 (the 16:9 crop), so < 6/6 -> a strict margin alone is not enough.
ok = (res["title90_bottom"][1] == 0 and res["action93_bottom"][1] == 0
      and res["strict_edges"][1] == 6 and res["strict_but_wide"][1] == 0
      and res["strict_edges"][0] < 6)
print("RESULT: %s overlay-clear 90%%=%d 93%%=%d strict=%d wide=%d; strict all-crop=%d/6"
      % ("PASS" if ok else "FAIL", res["title90_bottom"][1], res["action93_bottom"][1],
         res["strict_edges"][1], res["strict_but_wide"][1], res["strict_edges"][0]))
