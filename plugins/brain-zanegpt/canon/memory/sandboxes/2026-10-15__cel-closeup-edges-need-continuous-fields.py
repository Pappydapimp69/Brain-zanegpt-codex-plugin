"""Cel loop 2 - GGXrd stored the shade-threshold offset in vertex colours instead of
textures because 'texture data are very resolution dependent ... vertex properties are
linearly interpolated, completely resolution independent' (Motomura, GDC 2015).
Test, at equal sample budget (17x17 samples over the patch), how far the shaded region's
edge strays from the intended smooth edge (a circle of radius 0.31 in UV) at close-up
zoom, for four ways to store it:
  A vertex grid, signed distance, linear on triangles      (GGXrd's way)
  B texture, signed distance, bilinear filtered
  C texture, painted binary mask, nearest
  D texture, painted binary mask, bilinear then threshold 0.5
Zoom Z = screen pixels per sample spacing. Deviation = max distance in screen px from a
classified boundary pixel to the true circle, over a supersampled scan. No RNG.
PREDICTION (written before running): A and B are within 25% of each other at every
zoom; C deviates about 0.7 Z px; D about 0.3 Z px; so the real axis is continuous field
vs painted mask, not vertex vs texture."""
import math
S = 17; R0 = 0.31; C0 = (0.5, 0.5)
sd = lambda u, v: math.hypot(u - C0[0], v - C0[1]) - R0            # signed distance, <0 inside
grid = [[sd(i / (S - 1), j / (S - 1)) for i in range(S)] for j in range(S)]
mask = [[1.0 if g < 0 else 0.0 for g in row] for row in grid]
def at(arr, i, j): return arr[max(0, min(S - 1, j))][max(0, min(S - 1, i))]
def tri_linear(u, v):           # A: split each cell along the diagonal, barycentric
    x, y = u * (S - 1), v * (S - 1); i, j = min(int(x), S - 2), min(int(y), S - 2); fx, fy = x - i, y - j
    if fx + fy <= 1: return at(grid, i, j) + fx * (at(grid, i + 1, j) - at(grid, i, j)) + fy * (at(grid, i, j + 1) - at(grid, i, j))
    return at(grid, i + 1, j + 1) + (1 - fx) * (at(grid, i, j + 1) - at(grid, i + 1, j + 1)) + (1 - fy) * (at(grid, i + 1, j) - at(grid, i + 1, j + 1))
def bilinear(arr, u, v):
    x, y = u * (S - 1), v * (S - 1); i, j = min(int(x), S - 2), min(int(y), S - 2); fx, fy = x - i, y - j
    return (at(arr, i, j) * (1 - fx) * (1 - fy) + at(arr, i + 1, j) * fx * (1 - fy)
            + at(arr, i, j + 1) * (1 - fx) * fy + at(arr, i + 1, j + 1) * fx * fy)
def nearest(arr, u, v): return at(arr, int(round(u * (S - 1))), int(round(v * (S - 1))))
inside = {"A vertex SDF": lambda u, v: tri_linear(u, v) < 0,
          "B texture SDF bilinear": lambda u, v: bilinear(grid, u, v) < 0,
          "C texture mask nearest": lambda u, v: nearest(mask, u, v) > 0.5,
          "D texture mask bilinear": lambda u, v: bilinear(mask, u, v) > 0.5}
def deviation(fn, Z):
    n = int(Z * (S - 1)); worst = 0.0
    step = max(1, n // 400)                       # scan up to ~400x400 screen samples
    for py in range(0, n, step):
        prev = None
        for px in range(0, n, step):
            u, v = px / n, py / n; inn = fn(u, v)
            if prev is not None and inn != prev:  # a boundary crossing on this row
                worst = max(worst, abs(sd(u, v)) * n)
            prev = inn
    for px in range(0, n, step):                  # columns too
        prev = None
        for py in range(0, n, step):
            u, v = px / n, py / n; inn = fn(u, v)
            if prev is not None and inn != prev: worst = max(worst, abs(sd(u, v)) * n)
            prev = inn
    return worst
res = {}
for Z in (2, 8, 32):
    res[Z] = {k: deviation(f, Z) for k, f in inside.items()}
    print(f"zoom {Z:2d}: " + "  ".join(f"{k}: {v:6.2f}px" for k, v in res[Z].items()))
ab = all(abs(res[Z]["A vertex SDF"] - res[Z]["B texture SDF bilinear"]) <= 0.25 * max(res[Z]["A vertex SDF"], res[Z]["B texture SDF bilinear"]) for Z in res)
cz = [res[Z]["C texture mask nearest"] / Z for Z in res]; dz = [res[Z]["D texture mask bilinear"] / Z for Z in res]
az = [res[Z]["A vertex SDF"] / Z for Z in res]
print("deviation per sample spacing: A", [f"{x:.3f}" for x in az], "C", [f"{x:.2f}" for x in cz], "D", [f"{x:.2f}" for x in dz])
ok = ab and all(0.5 <= x <= 0.9 for x in cz) and all(0.15 <= x <= 0.45 for x in dz)
print(f"RESULT: {'PASS' if ok else 'FAIL'} at zoom 32: vertex SDF {res[32]['A vertex SDF']:.2f}px, texture SDF {res[32]['B texture SDF bilinear']:.2f}px, "
      f"mask nearest {res[32]['C texture mask nearest']:.1f}px, mask bilinear {res[32]['D texture mask bilinear']:.1f}px; A~B {ab}")
