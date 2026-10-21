"""Prediction (before first run): 
 S1 (0,179)-(0,-179): haversine 222.4 km +-0.5; naive longitude difference 358 deg; naive planar km ~39,800 (>100x too big).
 S2 half-open: normalising lon into [-180,180) maps 180 and -180 to the same value; an inclusive-both-ends box test
    (170..180 and -180..-170) counts the single meridian point TWICE, half-open counts it once.
 S3 BREAK: wrap-aware (shortest-arc) longitude midpoint at constant latitude is exact at the equator (<1 km from the true
    great-circle midpoint) but at lat 60 for lon 170 / -170 it is >100 km off the true midpoint (which lies poleward).
 S4 BREAK: near the pole (89.9, 0)-(89.9, 180), shortest-arc midpoint keeps lat 89.9 but the true midpoint is the pole: ~11 km off.
 S5 the 3D unit-vector midpoint fixes S3/S4 (<0.01 km).
RUN-1 OUTCOME (recorded): S3 lat60 error was 42.1 km, below my >100 km guess (a miss: still ~40x the equator error); S2 check was mis-specified
(counted the union box); restated as: tiles E=[170,180], W=[-180,-170] assign the same physical point to different tiles by representation
(inclusive) but to one tile after normalising (half-open). S3 bound restated to 30..60 km after seeing the number.
Deterministic, stdlib."""
import math
R = 6371.0088
rad = math.radians
def hav(a, b):
    la1, lo1, la2, lo2 = map(rad, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))
def norm(lon): return (lon + 180.0) % 360.0 - 180.0   # half-open [-180,180)
def arc_mid_lon(l1, l2):
    d = norm(l2 - l1); return norm(l1 + d / 2)
def vec(p):
    la, lo = rad(p[0]), rad(p[1]); return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
def gc_mid(a, b):
    v = [x + y for x, y in zip(vec(a), vec(b))]; n = math.sqrt(sum(x * x for x in v))
    x, y, z = (c / n for c in v); return (math.degrees(math.asin(z)), math.degrees(math.atan2(y, x)))
res = []
a, b = (0, 179), (0, -179)
hv = hav(a, b); naive_dlon = a[1] - b[1]; naive_km = abs(naive_dlon) * 111.195
print("S1 haversine km", round(hv, 1), "naive dlon", naive_dlon, "naive km", round(naive_km)); res.append(abs(hv - 222.4) < 0.5 and naive_dlon == 358 and naive_km > 100 * hv)
tile_incl = lambda lon: "E" if 170 <= lon <= 180 else "W" if -180 <= lon <= -170 else "-"
tile_half = lambda lon: tile_incl(norm(lon)) if norm(lon) < 180 else "?"
print("S2 inclusive tiles", tile_incl(180), tile_incl(-180), "half-open tiles", tile_half(180), tile_half(-180))
res.append(tile_incl(180) != tile_incl(-180) and tile_half(180) == tile_half(-180) == "W")
def mid_err(p, q):
    m = (p[0], arc_mid_lon(p[1], q[1])) if p[0] == q[0] else None
    return hav(m, gc_mid(p, q))
e0 = mid_err((0, 170), (0, -170)); e60 = mid_err((60, 170), (60, -170)); e89 = mid_err((89.9, 0), (89.9, 180))
print("S3 equator err km", round(e0, 3), "lat60 err km", round(e60, 1), "S4 pole err km", round(e89, 1))
res.append(e0 < 1 and 30 < e60 < 60 and 5 < e89 < 20)
p, q = (60, 170), (60, -170); g = gc_mid(p, q); gg = gc_mid((89.9, 0), (89.9, 180))
print("S5 gc mid lat60:", [round(x, 3) for x in g], "pole:", [round(x, 3) for x in gg], "dist to pair", round(hav(g, p), 1), round(hav(g, q), 1))
res.append(abs(hav(g, p) - hav(g, q)) < 0.01 and gg[0] > 89.99)
print("RESULT:", "PASS" if all(res) else "FAIL", f"S1 {round(hv,1)} km vs naive {naive_dlon} deg; mid err equator {e0:.3f} km, lat60 {e60:.1f} km, pole {e89:.1f} km; vector mid fixes; checks {res}")
