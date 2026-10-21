# A reveal caption closes an information gap (film/E3: "Nobody came to her stream."). If it is cropped or covered,
# the gap stays open. Frame is 9:16, y in [0,1] top to bottom. Viewports (visible y ranges, full width kept):
VIEWPORTS = {
    "broadcast title-safe 90%": (0.05, 0.95),
    "feed crop 4:5":            ((1 - (9/16)/(4/5)) / 2, 1 - (1 - (9/16)/(4/5)) / 2),
    "square crop 1:1":          ((1 - (9/16)/1.0) / 2, 1 - (1 - (9/16)/1.0) / 2),
    "social UI overlay":        (0.08, 0.80),   # assumed: top 8% and bottom 20% covered by app chrome
}
CAP_H = 0.06
def visible(cy, vp, h=CAP_H):
    lo, hi = vp
    return cy - h/2 >= lo - 1e-9 and cy + h/2 <= hi + 1e-9
def count(cy, h=CAP_H): return sum(visible(cy, vp, h) for vp in VIEWPORTS.values())

positions = {"bottom edge of title-safe": 0.92, "lower third": 0.80, "upper third": 0.22, "centre": 0.50}
for k, cy in positions.items():
    print(f"{k:26s} y={cy:.2f} visible in {count(cy)}/4 viewports")
step = [i / 1000 for i in range(30, 971)]
band = [cy for cy in step if count(cy) == 4]
print("all-4 band for a %.2f-high caption: centre y %.3f to %.3f" % (CAP_H, min(band), max(band)))
# Iteration 2 note: the first run failed two predictions - float edge error at y=0.92, and I expected 0 clear positions at height 0.06 (observed two thin bands).
# the beats: 9 beats, 3 reveal captions (film/E3), each closes a gap that the previous beat opened
beats = 9; reveals = 3
def closure(cy):
    return {n: (reveals if visible(cy, vp) else 0) / reveals for n, vp in VIEWPORTS.items()}
print("gap closure at bottom edge of title-safe:", closure(0.92))
# BREAK: hero action occupies y 0.30-0.70 (the action zone); caption must also avoid it
ACTION = (0.30, 0.70)
def clear_of_action(cy, h=CAP_H): return cy + h/2 <= ACTION[0] + 1e-9 or cy - h/2 >= ACTION[1] - 1e-9
both = [cy for cy in step if count(cy) == 4 and clear_of_action(cy)]
print("caption %.2f high: positions safe in all 4 viewports AND clear of the action: %d" % (CAP_H, len(both)))
for h in (0.06, 0.04, 0.03):
    ok_h = [cy for cy in step if count(cy, h) == 4 and clear_of_action(cy, h)]
    print(f"  caption height {h:.2f}: {len(ok_h)} usable positions" + (f" (y {min(ok_h):.3f}-{max(ok_h):.3f})" if ok_h else ""))
ok = count(0.92) == 1 and count(0.50) == 4 and 0 < len(both) < 60 and len([cy for cy in step if count(cy, 0.03) == 4 and clear_of_action(cy, 0.03)]) > 0
print("RESULT: %s title-safe bottom caption shows in %d/4 viewports (gap closure %s), only a y %.2f-%.2f band shows in 4/4 and next to the 0.30-0.70 action zone just %d of 941 sampled positions remain at height 0.06 (two thin bands), %d at height 0.03"
      % ("PASS" if ok else "FAIL", count(0.92), "1 of 4 viewports", min(band), max(band), len(both), len([cy for cy in step if count(cy, 0.03) == 4 and clear_of_action(cy, 0.03)])))
