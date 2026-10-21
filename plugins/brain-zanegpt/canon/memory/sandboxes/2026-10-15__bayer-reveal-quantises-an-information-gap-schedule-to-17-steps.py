# Sandbox: a film "reveal" (withhold -> show) done as a Bayer 4x4 threshold dissolve on a 1-bit image.
# Kernels exercised: tension-as-information-gap (the reveal SCHEDULE is the discourse structure),
# bayer-4x4-gives-17-levels (matrix, 17 tones, world-space anchoring), film (24 fps frame clock, 2.0 s shot, camera pan).
# Prediction (written before running): over 48 frames (2 s at 24 fps) a linear schedule shows exactly 17 distinct
# revealed counts and 48-17=31 repeat frames... precisely: distinct levels = 17, revealed sets are nested in 48/48 frames
# with a world-anchored matrix, but with a screen-anchored matrix and a 1 px/frame pan the sets stop being nested
# in at least 40 of 47 transitions; a cubic (suspense) schedule holds level 0 for at least 12 frames.
M = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
W = H = 32; F = 48
def thr(x, y): return (M[y & 3][x & 3] + 0.5) / 16
def frame(p, camx=0, anchored=True):
    # world pixel (wx,wy) is revealed when progress p > threshold; screen pixel x shows world x+camx
    return {(x, y) for y in range(H) for x in range(W)
            if p > thr((x + camx) if anchored else x, y)}
def world_set(p, camx, anchored):
    # express revealed set in WORLD coordinates for nesting comparison
    return {(x + camx, y) for (x, y) in frame(p, camx, anchored)}
lin = [i / (F - 1) for i in range(F)]
cub = [(i / (F - 1)) ** 3 for i in range(F)]
levels = lambda sched: [sum(1 for k in range(16) if p > (k + 0.5) / 16) for p in sched]
ll, cl = levels(lin), levels(cub)
print("linear distinct levels", len(set(ll)), "cubic distinct", len(set(cl)), "cubic frames at level 0:", cl.count(0))
def nested(anch):
    bad = 0
    for i in range(1, F):
        a = world_set(lin[i-1], i-1, anch); b = world_set(lin[i], i, anch)
        # keep only world columns visible in both frames, then require a subset
        cols = set(range(i, W + i - 1))
        a = {q for q in a if q[0] in cols}; b = {q for q in b if q[0] in cols}
        if not a <= b: bad += 1
    return bad
bad_a, bad_s = nested(True), nested(False)
print("non-nested transitions (of 47): anchored", bad_a, "screen-anchored", bad_s)
ok = len(set(ll)) == 17 and bad_a == 0 and bad_s >= 40 and cl.count(0) >= 12
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"linear levels {len(set(ll))}, anchored breaks {bad_a}/47, screen-anchored breaks {bad_s}/47, cubic dead frames at 0: {cl.count(0)}")
