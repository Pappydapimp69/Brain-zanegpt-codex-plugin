"""Cel loop 10 - screen-space outlines from the depth buffer. The zzamjak ToonShading URP
package (openupm) runs Roberts cross over depth and normal textures and 'normalizes depth
edges by center depth so line weight stays roughly constant with distance'.
Scene, ray-cast per pixel column (pinhole camera f = 1000 px, eye 1.5 m above a flat
floor, looking horizontally): a floor, and a box face 0.3 m in front of a back wall,
placed at distances z = 2..50 m. Depth image -> Roberts cross magnitude on depth.
  ABS: edge if |grad z| > 0.1 m        NORM: edge if |grad z| / z > 0.02
Measured: is the true box/wall edge detected (at its pixel row), and does the bare floor
produce false edges, at each distance. No RNG.
PREDICTION (written before running): ABS detects the 0.3 m step at every distance but
marks the bare floor as an edge beyond about 12 m (z^2/(f h) > 0.1); NORM keeps the floor
clean to about 30 m but loses the 0.3 m step beyond 15 m; neither covers 2-50 m."""
import math
f, h = 1000.0, 1.5
def floor_depth(row):             # row below the horizon (row > 0) -> distance along view axis
    return f * h / row if row > 0 else float("inf")
def roberts(img, r, c):
    return math.hypot(img[r][c] - img[r + 1][c + 1], img[r][c + 1] - img[r + 1][c])
def scene(zbox, gap=0.3):
    # a box front face at zbox in columns 0..9, the wall it stands before at zbox+gap in 10..19;
    # rows: a strip from the horizon down to 600 px, floor everywhere the objects don't cover
    rows = 600; img = []
    for r in range(rows):
        row = []
        for c in range(20):
            z_obj = zbox if c < 10 else zbox + gap
            zf = floor_depth(r + 1)
            # the object occupies rows whose floor point lies behind it
            row.append(z_obj if zf > z_obj else zf)
        img.append(row)
    return img
def test(z):
    img = scene(z)
    edge_row = max(1, int(f * h / z / 2))                         # a row halfway up the object (above its floor contact)
    g_edge = roberts(img, edge_row, 9)                            # across the box/wall column boundary
    # bare floor sample: the floor row whose depth is about z (no object column effect across rows)
    fr = max(1, int(f * h / z))
    g_floor = abs(floor_depth(fr) - floor_depth(fr + 1))         # vertical neighbour difference on the floor
    return {"ABS": (g_edge > 0.1, g_floor > 0.1), "NORM": (g_edge / z > 0.02, g_floor / z > 0.02)}
res = {z: test(z) for z in (2, 5, 10, 12, 15, 20, 30, 40, 50)}
for z, r in res.items():
    print(f"z {z:2d} m: ABS edge {'hit' if r['ABS'][0] else 'MISS'} floor {'FALSE EDGE' if r['ABS'][1] else 'clean'} | "
          f"NORM edge {'hit' if r['NORM'][0] else 'MISS'} floor {'FALSE EDGE' if r['NORM'][1] else 'clean'}")
abs_floor = min((z for z, r in res.items() if r["ABS"][1]), default=None)
norm_miss = min((z for z, r in res.items() if not r["NORM"][0]), default=None)
norm_floor = min((z for z, r in res.items() if r["NORM"][1]), default=None)
abs_all = all(r["ABS"][0] for r in res.values())
ok = abs_all and abs_floor is not None and 10 <= abs_floor <= 15 and norm_miss is not None and 15 <= norm_miss <= 20 and (norm_floor or 99) >= 30
print(f"RESULT: {'PASS' if ok else 'FAIL'} ABS finds the 0.3 m step at all distances: {abs_all}, floor false edges from {abs_floor} m; "
      f"NORM loses the step from {norm_miss} m, floor false edges from {norm_floor} m")
