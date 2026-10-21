# How big is an art-pixel sprite on a phone, in points, vs Apple's 44 pt minimum tap target?
# Portrait phone 390 pt wide (iPhone 14/15 class, 3x). Canvas fills the width; integer-scale variant snaps to whole device px.
PT_W, DPR = 390, 3
def pt_per_art_px(canvas_w, integer):
    if not integer: return PT_W / canvas_w
    k = (PT_W * DPR) // canvas_w; return k / DPR          # device px per art px, as points
def need(canvas_w, integer): return 44 / pt_per_art_px(canvas_w, integer)
res = []
rows = []
for name, cw in (("stonewake portrait 180", 180), ("320 wide", 320), ("640x360 sideways", 640)):
    for integ in (False, True):
        p = pt_per_art_px(cw, integ); rows.append((name, integ, p, need(cw, integ)))
        print(f"{name:24s} integer={integ!s:5s}: 1 art px = {p:.2f} pt; 12px tile {12*p:5.1f} pt, 16px {16*p:5.1f} pt, 18x32 hero {18*p:.0f}x{32*p:.0f} pt; 44 pt needs {need(cw, integ):.1f} art px")
s180 = pt_per_art_px(180, True)
# 1) Stonewake's 12 px tile at 180 wide misses 44 pt  2) 16 px tile also misses (BREAK: 'a 16x16 tile is a fine tap target')
res.append(12 * s180 < 44); res.append(16 * s180 < 44)
# 3) integer snapping shrinks the pixel (6 dev px = 2.00 pt vs 2.17 pt fill) so the needed size grows
res.append(need(180, True) > need(180, False))
# 4) on a 640-wide canvas an 18x32 sprite is under 15 pt wide: unreadable as a tap target
res.append(18 * pt_per_art_px(640, True) < 15)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" at 180 wide integer x6: 1 art px = {s180:.2f} pt; 12px tile {12*s180:.0f} pt, 16px {16*s180:.0f} pt, both < 44; need {need(180, True):.0f} art px (fill: {need(180, False):.1f}); 640 wide: 18px sprite {18*pt_per_art_px(640, True):.1f} pt")
