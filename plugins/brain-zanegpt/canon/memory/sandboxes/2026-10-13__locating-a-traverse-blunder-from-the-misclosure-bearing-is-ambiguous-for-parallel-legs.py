"""Closed traverse: locate a single blunder leg from the misclosure bearing. Deterministic, plane geometry.
A distance blunder on leg k shifts the closing vector along leg k's bearing, so legs whose bearing is parallel (or
antiparallel) to the misclosure are suspects. An angle (bearing) blunder on leg k rotates all later legs and gives a
misclosure perpendicular to the chord from that station to the end, which a leg-bearing test does not see."""
import math
def poly(n, r=100.0, squash=1.0, twist=0.0):
    pts = [(r * math.cos(2 * math.pi * i / n + twist), r * squash * math.sin(2 * math.pi * i / n + twist)) for i in range(n)]
    return pts
def legs(pts):
    n = len(pts); out = []
    for i in range(n):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
        out.append((math.hypot(x1 - x0, y1 - y0), math.atan2(y1 - y0, x1 - x0)))
    return out
def misclosure(ls):
    x = sum(d * math.cos(b) for d, b in ls); y = sum(d * math.sin(b) for d, b in ls)
    return x, y
def suspects(mis, ls, tol_deg=5.0):
    mb = math.atan2(mis[1], mis[0]); out = []
    for i, (d, b) in enumerate(ls):
        diff = abs((mb - b + math.pi) % (2 * math.pi) - math.pi)
        diff = min(diff, math.pi - diff)
        if math.degrees(diff) <= tol_deg: out.append(i)
    return out
def run(name, pts, k, kind, amount, verbose=False):
    ls = legs(pts)
    if kind == "dist":
        d, b = ls[k]; ls[k] = (d + amount, b)
    else:  # bearing blunder: leg k and every later leg rotated (angle misread at station k)
        ls = [(d, b + (amount if i >= k else 0.0)) for i, (d, b) in enumerate(ls)]
    m = misclosure(ls); s = suspects(m, ls)
    if verbose: print(f"{name}: blunder {kind} on leg {k}, misclosure {math.hypot(*m):.2f}, suspects {s}, hit {k in s}")
    return (k in s), len(s)
def irregular(n):
    return [((100 + 17 * ((i * 5) % 3)) * math.cos(2 * math.pi * i / n + 0.11 * i), (100 - 13 * ((i * 7) % 4)) * math.sin(2 * math.pi * i / n + 0.11 * i)) for i in range(n)]
shapes = {"regular hexagon": poly(6), "regular pentagon": poly(5), "regular octagon": poly(8), "irregular hexagon": irregular(6), "irregular heptagon": irregular(7)}
tab = {}
for nm, pts in shapes.items():
    for kind, amt in (("dist", 2.0), ("ang", math.radians(3))):
        r = [run(nm, pts, k, kind, amt) for k in range(len(pts))]
        tab[(nm, kind)] = (sum(h for h, c in r) / len(r), sum(c for h, c in r) / len(r))
        print(f"{nm:20s} {kind}: hit rate {tab[(nm, kind)][0]:.2f}, mean suspects {tab[(nm, kind)][1]:.2f}")
ok = tab[("regular hexagon", "dist")] == (1.0, 2.0) and tab[("regular pentagon", "dist")][1] == 1.0 and tab[("irregular hexagon", "dist")][1] < 1.5 \
     and tab[("regular hexagon", "ang")][0] < 1.0 and tab[("irregular hexagon", "ang")][0] < 1.0
print(("RESULT: PASS" if ok else "RESULT: FAIL") + " " + "; ".join(f"{a} {b} hit {v[0]:.2f} susp {v[1]:.2f}" for (a, b), v in tab.items()))
