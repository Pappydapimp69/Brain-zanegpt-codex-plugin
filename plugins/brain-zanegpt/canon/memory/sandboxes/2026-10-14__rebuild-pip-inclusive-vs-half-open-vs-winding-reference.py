"""Rebuild of sandbox-geometry-pip/E1 from its claim only.
PREDICTION (before running): on integer-grid polygons with all test points on the integer grid, the inclusive-both-ends
crossing test disagrees with an independent exact reference (winding number with explicit on-boundary exclusion) only for
points whose row passes through a vertex where the boundary crosses (pass-through), is right for local-extremum vertices
(touch counts 2, parity unchanged), and the half-open test has 0 disagreements on every polygon, including one with a horizontal edge."""
from fractions import Fraction as F

def on_boundary(p, poly):
    x, y = p
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (x2 - x1) * (y - y1) == (y2 - y1) * (x - x1) and min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return True
    return False

def winding(p, poly):
    x, y = p; w = 0
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        cross = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)
        if y1 <= y < y2 and cross > 0: w += 1
        elif y2 <= y < y1 and cross < 0: w -= 1
    return w != 0

def inclusive(p, poly):
    x, y = p; inside = False
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[(i + 1) % len(poly)]
        if min(yi, yj) <= y <= max(yi, yj) and yi != yj:
            xc = xi + F(y - yi) * (xj - xi) / (yj - yi)
            if x < xc: inside = not inside
    return inside

def half_open(p, poly):
    x, y = p; inside = False
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[(i + 1) % len(poly)]
        if (yi > y) != (yj > y):
            xc = xi + F(y - yi) * (xj - xi) / (yj - yi)
            if x < xc: inside = not inside
    return inside

POLYS = {
  "diamond": [(5, 0), (10, 5), (5, 10), (0, 5)],
  "arrow-concave": [(0, 0), (8, 4), (0, 8), (3, 4)],
  "L-with-horizontal-edges": [(0, 0), (6, 0), (6, 3), (3, 3), (3, 6), (0, 6)],
  "zigzag-passthrough": [(0, 0), (4, 2), (2, 4), (6, 6), (0, 8)],
}
ok = True
for name, poly in POLYS.items():
    inc_bad = hop_bad = 0; vertex_row_bad = 0; n = 0
    vrows = {y for _, y in poly}
    for x in range(-2, 12):
        for y in range(-2, 12):
            p = (x, y)
            if on_boundary(p, poly): continue
            n += 1
            ref = winding(p, poly)
            if inclusive(p, poly) != ref:
                inc_bad += 1; vertex_row_bad += (y in vrows)
            if half_open(p, poly) != ref: hop_bad += 1
    print(f"{name}: points {n} inclusive wrong {inc_bad} (on vertex rows {vertex_row_bad}) half-open wrong {hop_bad}")
    ok &= hop_bad == 0 and vertex_row_bad == inc_bad
    if name in ("diamond", "zigzag-passthrough", "arrow-concave"): ok &= inc_bad > 0
    if name == "L-with-horizontal-edges": print("  L inclusive wrong:", inc_bad)
# off-grid control: rays at y+1/2 never hit a vertex row, so both implementations must agree everywhere
agree = all(inclusive((x, F(2 * y + 1, 2)), p) == half_open((x, F(2 * y + 1, 2)), p) for p in POLYS.values()
            for x in range(-2, 12) for y in range(-2, 12))
print("half-integer rows (no vertex alignment): inclusive == half-open everywhere:", agree)
ok &= agree
print("RESULT:", "PASS" if ok else "FAIL", "inclusive errs only on vertex-aligned rows; half-open exact on all four polygons; off-grid control agrees")
