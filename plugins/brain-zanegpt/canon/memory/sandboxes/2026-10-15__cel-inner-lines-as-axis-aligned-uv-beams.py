"""Cel loop 6 - GGXrd inner lines: 'All the lines are drawn as Axis Aligned beams on the
texture, and the UV is lined up alongside them. How much the UV overlaps these beams,
defines how thick that line becomes. As long as the pixels are Aligned to an Axis they
don't get any jaggie' (Motomura, GDC 2015).
Model: a 32x32 texture; a 30-degree line on the surface, rendered at 24x magnification
(screen px per texel) with bilinear sampling then threshold 0.5 (a crisp cel line).
  A: the line painted diagonally into the texture (anti-aliased by coverage, 2 texels wide),
     UV = surface coordinates
  B: a horizontal beam 2 texels tall painted on texel rows, UV rotated by 30 degrees so the
     beam runs along the same surface line
Edge error = max distance (screen px) from classified edge pixels to the ideal edge lines.
Also: B's width vs UV offset across the beam edge (the thickness control).
PREDICTION (written before running): A's edge error is >= 0.25 texel (6 px at 24x), B's is
< 0.5 px; B's line width grows linearly with how far the UV strip overlaps the beam."""
import math
T, M = 32, 24
ang = math.radians(30); ca, sa = math.cos(ang), math.sin(ang)
HALF = 1.0                                    # half width of the line in texels
def cov_diag(i, j):                           # A: coverage of texel (i,j) by the diagonal band, 4x4 supersampled
    c = 0
    for a in range(4):
        for b in range(4):
            x, y = i + (a + 0.5) / 4 - T / 2, j + (b + 0.5) / 4 - T / 2
            c += abs(-sa * x + ca * y) <= HALF
    return c / 16
texA = [[cov_diag(i, j) for i in range(T)] for j in range(T)]
texA2 = [[1.0 if abs(-sa * (i + 0.5 - T / 2) + ca * (j + 0.5 - T / 2)) <= HALF else 0.0 for i in range(T)] for j in range(T)]   # hard-painted diagonal
texB = [[1.0 if T / 2 - HALF <= j + 0.5 <= T / 2 + HALF else 0.0 for i in range(T)] for j in range(T)]
def bil(tex, u, v):                           # u,v in texel units, texel centres at +0.5
    x, y = u - 0.5, v - 0.5; i, j = math.floor(x), math.floor(y); fx, fy = x - i, y - j
    g = lambda a, b: tex[min(T - 1, max(0, b))][min(T - 1, max(0, a))]
    return g(i, j) * (1 - fx) * (1 - fy) + g(i + 1, j) * fx * (1 - fy) + g(i, j + 1) * (1 - fx) * fy + g(i + 1, j + 1) * fx * fy
def render_err(sampler, offset=0.0):
    n = T * M; worst = 0.0; widths = []
    for py in range(n // 4, 3 * n // 4, 3):
        row = []
        for px in range(n // 4, 3 * n // 4):
            x, y = px / M - T / 2, py / M - T / 2           # surface coords in texels, centred
            row.append(sampler(x, y, offset) > 0.5)
        for k in range(1, len(row)):
            if row[k] != row[k - 1]:
                x, y = (n // 4 + k) / M - T / 2, py / M - T / 2
                d = abs(abs(-sa * x + ca * y) - HALF * (1 if offset == 0 else 1))
                worst = max(worst, d * M)
    return worst
sampA = lambda x, y, o: bil(texA, x + T / 2, y + T / 2)
def sampB(x, y, o):
    u = ca * x + sa * y; v = -sa * x + ca * y + o         # rotate surface coords into beam space
    return bil(texB, u + T / 2, v + T / 2)
eA, eB = render_err(sampA), render_err(sampB)
eA2 = render_err(lambda x, y, o: bil(texA2, x + T / 2, y + T / 2))
print(f"(iteration 2) A2 hard-painted diagonal: {eA2:.2f}px ({eA2/M:.2f} texel); B's 0.50px equals the half-pixel scan quantisation")
# thickness control: shrink the UV strip so it only partly overlaps the beam -> measured width along the normal
def width_for_overlap(scale):
    hits = 0; steps = 4000
    for k in range(steps):
        v = (k / steps - 0.5) * 6                              # sample across the line, texels
        hits += bil(texB, T / 2, v * scale + T / 2) > 0.5
    return hits / steps * 6
wid = {s: width_for_overlap(s) for s in (0.5, 1.0, 2.0)}
print(f"edge error: A diagonal-in-texture {eA:.2f}px ({eA/M:.2f} texel); B axis-aligned beam {eB:.2f}px")
print("B line width (texels on surface) vs UV scale across the beam:", {s: round(w_, 2) for s, w_ in wid.items()})
lin = abs(wid[0.5] / wid[1.0] - 2) < 0.1 and abs(wid[1.0] / wid[2.0] - 2) < 0.1
ok = eA / M >= 0.25 and eB < 0.5 and lin
print(f"RESULT: {'PASS' if ok else 'FAIL'} diagonal line edge error {eA:.1f}px ({eA/M:.2f} texel) vs axis-aligned beam {eB:.2f}px at {M}x; "
      f"beam width scales with UV scale (1/scale): {lin}")
