# Sandbox: a Bayer-4x4 dithered tone reveal (17 levels from two colours) is cut into
# BEATS equal steps (a check-column row per beat) and shown in four vertical-video
# crops with y offsets 0, 285, 420, 656. Two questions:
#  (1) do equal-looking beats stay equal in level steps for 4, 6, 8 beats?
#  (2) does the pattern stay identical across crops when anchored to the screen vs world?
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

def render(level, x0, y0, w, h, anchor_world):
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            px, py = (x0 + x, y0 + y) if anchor_world else (x, y)
            row.append(1 if level > BAYER[py % 4][px % 4] else 0)
        out.append(row)
    return out

# (0) 17 levels: count distinct on-pixel fractions over one 4x4 tile
fr = sorted({sum(sum(r) for r in render(l, 0, 0, 4, 4, True)) for l in range(0, 17)})
print("distinct tile densities:", len(fr))

# (1) beat step sizes
def steps(beats):
    lv = [round(16 * i / beats) for i in range(beats + 1)]
    d = [lv[i + 1] - lv[i] for i in range(beats)]
    return d
S = {b: steps(b) for b in (4, 6, 8)}
for b, d in S.items():
    print("beats=%d steps=%s unequal=%s" % (b, d, len(set(d)) > 1))

# (2) crop consistency: world render of the full frame cropped at offset vs a render made
# for the crop with the pattern anchored to the crop (screen) -- count differing pixels
W, FH, CH = 16, 64, 24
level = 8
mism = {}
for off in (0, 285, 420, 656):
    # the "master" frame is rendered once in world space; the viewer sees rows off..off+CH
    master = render(level, 0, off, W, CH, True)             # world anchored, crop of master
    world_crop = render(level, 0, off, W, CH, True)          # same by construction (control)
    screen = render(level, 0, 0, W, CH, False)               # pattern restarts at the crop top
    diff = sum(master[y][x] != screen[y][x] for y in range(CH) for x in range(W))
    mism[off] = (off % 4, diff)
    print("offset=%3d off%%4=%d screen-anchored differs from world in %d of %d px"
          % (off, off % 4, diff, W * CH))

# Prediction (before run): 17 densities; 4 and 8 beats are equal-stepped (4,... / 2,...) but 6 beats
# give steps {2,3} (unequal); screen-anchored crops differ from world in 0 px when offset%%4==0
# (offsets 0,420,656) and in a positive count when offset 285 (offset%%4=1).
ok = (len(fr) == 17 and len(set(S[4])) == 1 and len(set(S[8])) == 1 and len(set(S[6])) == 2
      and all(mism[o][1] == 0 for o in (0, 420, 656)) and mism[285][1] > 0)
print("RESULT: %s densities=%d six-beat steps=%s offset285 diff=%d px"
      % ("PASS" if ok else "FAIL", len(fr), S[6], mism[285][1]))
