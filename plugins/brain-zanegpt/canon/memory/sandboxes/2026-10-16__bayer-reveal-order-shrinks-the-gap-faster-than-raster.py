# Reveal a 16x16 image in 16 steps. Bayer order reveals cell when M[y&3][x&3] < k; raster reveals 16 cells per step row-major.
M = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
N = 16
def image(kind):
    if kind == "uniform": return [[0.5] * N for _ in range(N)]
    return [[min(1.0, x / N * 0.5 + (0.5 if (x - 8) ** 2 + (y - 8) ** 2 < 30 else 0.0)) for x in range(N)] for y in range(N)]
def revealed(order, k):
    if order == "bayer": return {(x, y) for y in range(N) for x in range(N) if M[y & 3][x & 3] < k}
    return {(i % N, i // N) for i in range(k * 16)}
def error(img, order, k):
    rev = revealed(order, k); tot = 0
    for y in range(N):
        for x in range(N):
            if (x, y) in rev: continue
            if not rev: tot += abs(img[y][x] - 0.5); continue
            best = min(rev, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[1], p[0]))
            tot += abs(img[y][x] - img[best[1]][best[0]])
    return tot / (N * N)
img = image("disc"); uni = image("uniform")
nested = all(revealed(o, k) <= revealed(o, k + 1) for o in ("bayer", "raster") for k in range(16))
eb = [error(img, "bayer", k) for k in range(1, 17)]; er = [error(img, "raster", k) for k in range(1, 17)]
ub = max(error(uni, "bayer", k) for k in range(1, 17)); ur = max(error(uni, "raster", k) for k in range(2, 17))
print([round(v, 3) for v in eb]); print([round(v, 3) for v in er])
ok = nested and eb[7] < 0.5 * er[7] and eb[15] == 0 == er[15] and ub == 0 and ur == 0
print("RESULT: %s nested=%s error at step 8 bayer=%.3f raster=%.3f, step 16 both 0; uniform image gives 0 for both (order is moot)" % (
    "PASS" if ok else "FAIL", nested, eb[7], er[7]))
