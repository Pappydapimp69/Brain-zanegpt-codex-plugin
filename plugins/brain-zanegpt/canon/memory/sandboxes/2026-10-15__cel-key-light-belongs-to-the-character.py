"""Cel loop 3 - per-character light vector vs scene lights. GGXrd: 'does not have a global
lighting system affecting the characters. Each character has his or her own dedicated
light vector that lights their idle pose in the best way' (Motomura, GDC 2015).
Model: a character = 600 surface normals on a head-sized sphere (Fibonacci points, front
hemisphere only), authored look = cel shading under its own light Lc (upper front left
in the character's local frame). Scenarios over a fight: walk 0..1200 px across the
stage, then a side switch (mirror on x, as fighters face the opponent).
  P: scene point light at (600, 900, 400) px     D: scene directional light
  C: per-character light, defined in the character's local (mirrored) frame
Metric: share of the surface whose lit/shaded state differs from the authored look.
PREDICTION (written before running): P differs from the authored look on >= 15% of the
surface somewhere on the walk; D differs on 0% during the walk but >= 15% after the side
switch; C differs on 0% throughout."""
import math
def norm(v): k = math.sqrt(sum(c * c for c in v)); return tuple(c / k for c in v)
pts = []
n = 1200; ga = math.pi * (3 - math.sqrt(5))
for i in range(n):
    y = 1 - 2 * (i + 0.5) / n; r = math.sqrt(1 - y * y); th = ga * i
    p = (r * math.cos(th), y, r * math.sin(th))
    if p[2] > 0: pts.append(p)                    # front hemisphere, facing the camera (+z)
Lc_local = norm((-0.6, 0.5, 0.62))                # authored: upper-left-front in the character's frame
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
def lit_set(light_for_point):
    return [dot(p, light_for_point(p)) > 0 for p in pts]
authored = lit_set(lambda p: Lc_local)
def diff(a, b): return sum(x != y for x, y in zip(a, b)) / len(a)
RADIUS = 60.0                                      # head radius in px
POINT = (600.0, 900.0, 400.0)                      # scene point light (stage coords, y up)
SUN = norm((-0.6, 0.5, 0.62))                      # scene sun chosen to match the authored light at the start
def world_points(x, mirrored):
    # character centre at (x, 300, 0); mirroring flips local x
    return [((-p[0] if mirrored else p[0]), p[1], p[2]) for p in pts], (x, 300.0, 0.0)
def shade_world(x, mirrored, kind):
    wp, c = world_points(x, mirrored)
    out = []
    for p_local, p in zip(pts, wp):
        if kind == "P":
            pos = (c[0] + RADIUS * p[0], c[1] + RADIUS * p[1], c[2] + RADIUS * p[2])
            L = norm(tuple(POINT[i] - pos[i] for i in range(3)))
            out.append(dot(p, L) > 0)
        elif kind == "D":
            out.append(dot(p, SUN) > 0)
        else:                                       # C: light lives in the character frame, so mirror it with the body
            Lw = ((-Lc_local[0] if mirrored else Lc_local[0]), Lc_local[1], Lc_local[2])
            out.append(dot(p, Lw) > 0)
    return out
res = {}
for kind in "PDC":
    walk = max(diff(shade_world(x, False, kind), authored) for x in range(0, 1201, 50))
    switched = diff(shade_world(600, True, kind), authored)
    res[kind] = (walk, switched)
    print(f"{kind}: worst difference from the authored look on the walk {walk:6.1%}; after side switch {switched:6.1%}")
ok = res["P"][0] >= 0.15 and res["D"][0] == 0 and res["D"][1] >= 0.15 and res["C"] == (0, 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} point light walk {res['P'][0]:.1%}, sun walk {res['D'][0]:.1%} / side switch {res['D'][1]:.1%}, "
      f"per-character light {res['C'][0]:.1%} / {res['C'][1]:.1%}")
