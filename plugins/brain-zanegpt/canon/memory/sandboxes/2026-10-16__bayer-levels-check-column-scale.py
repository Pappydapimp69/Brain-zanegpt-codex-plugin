"""Toy: encode a check-column's graded verdict (0..16) as a 4x4 Bayer 1-bit swatch, then view it
at different scales. Count how many of the 17 levels stay distinguishable by mean brightness of a
single swatch-sized window. Deterministic: nearest-neighbour scaling, no RNG."""
B = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def swatch(level):  # level 0..16 -> 4x4 of 0/1; pixel on if B < level
    return [[1 if B[y][x] < level else 0 for x in range(4)] for y in range(4)]
def scale(img, f, size=4):
    n = round(size*f)
    return [[img[min(size-1,int(y/f))][min(size-1,int(x/f))] for x in range(n)] for y in range(n)]
def window_mean(img, ox, oy, w):
    h = len(img)
    pts = [img[y][x] for y in range(oy, min(h, oy+w)) for x in range(ox, min(len(img[0]), ox+w))]
    return sum(pts)/len(pts)
def distinct_levels(f, w=4, step=1):
    # worst case over viewer-tile phases of the number of distinct window means among the 17 levels
    n = round(4*f); worst = 17
    for oy in range(0, n-w+1, step):
        for ox in range(0, n-w+1, step):
            means = {round(window_mean(scale(swatch(lv), f), ox, oy, w), 6) for lv in range(17)}
            worst = min(worst, len(means))
    return worst
res = {}
for name, f in (("native 1x",1),("integer 2x",2),("integer 3x",3),("BREAK non-integer 1.5x",1.5),("non-integer 2.5x",2.5)):
    w = round(4*f) if float(f).is_integer() else 4   # integer scales read whole swatch; others read a fixed 4px window
    res[name] = distinct_levels(f, w=w if float(f).is_integer() else 4, step=1) if not float(f).is_integer() else distinct_levels(f, w=round(4*f), step=round(4*f))
    print(f"{name}: worst-phase distinct levels = {res[name]}/17")
ok = res["native 1x"] == 17 and res["integer 2x"] == 17 and res["integer 3x"] == 17 and res["BREAK non-integer 1.5x"] < 17 and res["non-integer 2.5x"] < 17 and res["BREAK non-integer 1.5x"] > 1
print("RESULT: PASS" if ok else "RESULT: FAIL", f"integer scales worst-phase 17/17, 1.5x worst-phase {res['BREAK non-integer 1.5x']}/17, 2.5x keeps {res['non-integer 2.5x']}/17")
