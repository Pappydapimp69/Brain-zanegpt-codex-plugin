"""Prediction (before run): on the sphere, Web Mercator's local linear scale is sec(lat) and area scale sec^2(lat), so
area is inflated 1.00x at the equator, 2.00x at 45 deg, 4.00x at 60 deg, 33.4x at 83 deg (computed numerically from the
projection by finite differences, not from the formula); a square world map (y range equals x range, i.e. y=+-pi)
is cut at lat = atan(sinh(pi)) = 85.0511 deg; Greenland (~2.17e6 km2 at ~72N centroid) draws ~10.5x its true share
relative to an equatorial region (Africa ~30.4e6 km2 at ~2N centroid) and looks larger than Africa's 1/14 share
by about 10x. Built to break: the single-latitude factor is wrong for a large region -> integrate a 20-60N band.
Stdlib, deterministic."""
import math
def proj(lat, lon):
    la = math.radians(lat); lo = math.radians(lon)
    return lo, math.log(math.tan(math.pi / 4 + la / 2))
def area_scale(lat, eps=1e-5):
    # numerical Jacobian of (lon,lat)->(x,y) relative to the sphere metric (cos(lat) per lon radian, 1 per lat radian)
    d = math.degrees(eps)  # eps is radians; proj takes degrees (first run had this unit slip and returned ~0)
    x1, y1 = proj(lat, 0); x2, y2 = proj(lat, d); x3, y3 = proj(lat + d, 0)
    jac = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / (eps * eps)
    return jac / math.cos(math.radians(lat)) * 1.0
vals = {lat: area_scale(lat) for lat in (0, 45, 60, 83)}
print("s1 numeric area scale:", {k: round(v, 2) for k, v in vals.items()})
cut = math.degrees(math.atan(math.sinh(math.pi))); print("s2 square-map cutoff latitude", round(cut, 4))
gl, af = 72, 2
ratio = area_scale(gl) / area_scale(af); print("s3 Greenland drawn-area inflation vs Africa", round(ratio, 2))
# s4 BREAK: a 20-60 N band, true area = integral cos(lat), drawn area = integral sec(lat) * (1/cos^... ) -> compute by slabs
true = drawn = 0.0
for i in range(2000):
    lat = 20 + 40 * (i + .5) / 2000; dlat = math.radians(40 / 2000)
    true += math.cos(math.radians(lat)) * dlat
    drawn += (1.0) * dlat * (1 / math.cos(math.radians(lat))) * (1.0)  # dx per lon rad = 1, dy = sec(lat) dlat
band = drawn / true; mid = area_scale(40)
print("s4 band 20-60N inflation", round(band, 3), "vs midpoint-latitude factor", round(mid, 3))
ok = abs(vals[0] - 1) < 0.01 and abs(vals[45] - 2) < 0.02 and abs(vals[60] - 4) < 0.05 and abs(vals[83] - 1 / math.cos(math.radians(83)) ** 2) < 0.5 and abs(cut - 85.0511) < 0.001 and 9 < ratio < 12 and abs(band - mid) / mid > 0.05
print("RESULT: %s area_scale_0_45_60_83=%s cutoff=%.4f greenland_vs_africa=%.2f band20_60=%.3f midpoint_factor=%.3f" % ("PASS" if ok else "FAIL", [round(v, 2) for v in vals.values()], cut, ratio, band, mid))
