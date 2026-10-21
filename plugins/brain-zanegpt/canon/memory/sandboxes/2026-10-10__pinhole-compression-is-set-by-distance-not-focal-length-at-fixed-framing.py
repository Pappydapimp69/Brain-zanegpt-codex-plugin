"""Pinhole model of 'wide+close expands depth, tele+far compresses it' with framing held constant.

Model: image coordinate x = f * X / Z (pinhole), sensor frame height 24 mm. A subject of height 1.75 m stands at
distance d; a same-size twin object (the 'background') stands DELTA metres behind it. The compression metric is
the image-size ratio  R = size(background twin) / size(subject)  (1.0 = fully flat/stacked, small = deep).

PREDICTIONS (written before the first run, each could come out wrong):
 P1  Framing held constant (subject fills 50% of frame height) with DELTA=20 m: 24 mm needs d=3.6 m and gives
     R=0.1525 (=3.6/23.6); 200 mm needs d=30 m and gives R=0.600 (=30/50). Tolerance 0.001.
 P2  Same distance (d=10 m), focal length swept 24..200 mm: R changes by exactly 0 (< 1e-12); only subject size moves.
 P3  Crop-vs-optics: a 24 mm shot from the 200 mm camera position, rescaled (centre-cropped by 200/24), reproduces
     the 200 mm image to < 1e-9 (normalised to subject height); a 24 mm shot from the close position differs by more
     than 0.3 (BREAK case: matching the framing with a lens swap at the wrong spot does not reproduce the look).
 P4  Shot-size vocabulary (ECU..ELS) names f/d only: for each named size the 24 mm and 200 mm cameras sit at
     distances in the ratio exactly 200/24 and give different R for the same shot-size name.
 P5  BREAK: the pinhole is silent about blur. A thin lens at fixed N=2.8, fixed framing, DELTA=20 m makes the
     background blur diameter (fraction of frame height) between 3x and 5x larger at 200 mm than at 24 mm, so
     'distance only' holds for perspective but not for the whole look.
 P6  Zoom vs dolly: a 3x zoom at fixed position leaves R unchanged (change 0); a dolly-in that also grows the subject 3x
     (d1=15 m, DELTA=20 m) shrinks R by more than 2x.
 P7  BREAK (small separation): when DELTA << d (DELTA=0.5 m, a person against a wall) the 24 mm and 200 mm framings
     differ in R by < 0.05, so lens/distance choice barely changes depth there.
 P8  Viewer-side inference: a viewer who infers depth from known size recovers the depth ratio (d+DELTA)/d
     regardless of viewing distance and screen width.
 P9  Face-scale 3D: nose tip 0.10 m in front of ear plane; nose/ear magnification ratio at d=0.5 m is >= 1.15 and at
     d=3 m is <= 1.04.
"""

SENSOR_H = 0.024   # m, frame height
H = 1.75           # subject height, m
FAIL = []


def check(name, ok, detail):
    print(("ok   " if ok else "MISS ") + name + " " + detail)
    if not ok:
        FAIL.append(name)


def img_h(f, z, h=H):
    return f * h / z


def dist_for_frac(f, frac, h=H):
    return f * h / (frac * SENSOR_H)


def R(f, d, delta):
    return img_h(f, d + delta) / img_h(f, d)


# ---- P1: framing held, focal length and distance change together
delta = 20.0
d24, d200 = dist_for_frac(0.024, 0.5), dist_for_frac(0.200, 0.5)
r24, r200 = R(0.024, d24, delta), R(0.200, d200, delta)
check("P1", abs(r24 - 0.1525) < 1e-3 and abs(r200 - 0.6) < 1e-3,
      "d24=%.2f R24=%.4f d200=%.2f R200=%.4f" % (d24, r24, d200, r200))
for f in (0.014, 0.024, 0.035, 0.05, 0.085, 0.135, 0.2, 0.4):   # closed form: R is a function of d alone
    d = dist_for_frac(f, 0.5)
    assert abs(R(f, d, delta) - d / (d + delta)) < 1e-12

# ---- P2: same distance, focal swept
rs = [R(f, 10.0, delta) for f in (0.024, 0.035, 0.05, 0.085, 0.135, 0.2)]
check("P2", max(rs) - min(rs) < 1e-12, "spread=%.2e subject frac 24mm=%.3f 200mm=%.3f" % (
    max(rs) - min(rs), img_h(0.024, 10) / SENSOR_H, img_h(0.2, 10) / SENSOR_H))

# ---- P3: crop vs optics
scene = [(0.0, 0.0, 0.0), (0.3, 0.2, 0.0), (-0.4, 0.5, 0.0), (0.5, 0.9, 5.0), (-0.6, 0.3, 12.0),
         (0.2, 1.2, 20.0), (-0.2, 1.7, 8.0)]  # (X lateral, Y height, Z behind subject plane)


def project(f, d, pts):
    s = img_h(f, d)                    # normalise to the subject's own image height
    return [(f * X / (d + Z) / s, f * Y / (d + Z) / s) for X, Y, Z in pts]


tele = project(0.2, d200, scene)
crop = project(0.024, d200, scene)     # wide lens at the tele position, then rescaled/cropped
close = project(0.024, d24, scene)     # wide lens at the close position (same framing of subject, new perspective)
cropfac = 0.2 / 0.024
e_crop = max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a, b in zip(tele, crop))
e_close = max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a, b in zip(tele, close))
check("P3", e_crop < 1e-9 and e_close > 0.3,
      "crop-vs-tele err=%.2e wide-close-vs-tele err=%.3f (crop costs %.2fx linear resolution)" % (e_crop, e_close, cropfac))

# ---- P4: shot-size vocabulary names f/d only
sizes = {"ECU": 0.10, "CU": 0.30, "MCU": 0.60, "MS": 1.00, "LS": 1.80, "ELS": 8.0}  # metres of subject filling frame height
rows, okp4 = [], True
for name, vis in sizes.items():
    da, db = 0.024 * vis / SENSOR_H, 0.200 * vis / SENSOR_H
    ra, rb = da / (da + delta), db / (db + delta)
    okp4 = okp4 and abs(db / da - 0.2 / 0.024) < 1e-9 and abs(ra - rb) > 1e-3
    rows.append("%s d24=%.2f d200=%.2f R24=%.3f R200=%.3f" % (name, da, db, ra, rb))
check("P4", okp4, "; ".join(rows))

# ---- P5: thin-lens blur (the pinhole cannot see this)
def blur_frac(f, s1, dl, N=2.8):
    s2 = s1 + dl
    return f * f * abs(s2 - s1) / (N * s2 * (s1 - f)) / SENSOR_H


b24, b200 = blur_frac(0.024, d24, delta), blur_frac(0.2, d200, delta)
check("P5", 3.0 <= b200 / b24 <= 5.0, "blur24=%.4f blur200=%.4f of frame height, ratio=%.2f" % (b24, b200, b200 / b24))

# ---- P6: dolly vs zoom
d1 = 15.0
rz = (R(0.05, d1, delta), R(0.15, d1, delta))
rd = (R(0.05, d1, delta), R(0.05, d1 / 3.0, delta))
sub_zoom = img_h(0.15, d1) / img_h(0.05, d1)
sub_dolly = img_h(0.05, d1 / 3.0) / img_h(0.05, d1)
check("P6", abs(rz[1] - rz[0]) < 1e-12 and rd[0] / rd[1] > 2.0 and abs(sub_zoom - sub_dolly) < 1e-12,
      "zoom R %.4f->%.4f; dolly R %.4f->%.4f (x%.2f shrink); subject growth zoom %.1fx dolly %.1fx" % (
          rz[0], rz[1], rd[0], rd[1], rd[0] / rd[1], sub_zoom, sub_dolly))


def lat(f, d, off=3.0):
    return img_h(f, d + delta, off) / img_h(f, d)   # background lateral offset (3 m) in subject-heights


print("info  bg lateral offset in subject-heights: zoom %.3f->%.3f, dolly %.3f->%.3f" % (
    lat(0.05, d1), lat(0.15, d1), lat(0.05, d1), lat(0.05, d1 / 3.0)))

# ---- P7: DELTA << d
dl = 0.5
a, b = R(0.024, d24, dl), R(0.2, d200, dl)
check("P7", abs(a - b) < 0.05, "R24=%.4f R200=%.4f gap=%.4f DELTA/d24=%.3f" % (a, b, abs(a - b), dl / d24))
th = next(x / 100.0 for x in range(1, 5000) if abs(R(0.024, d24, x / 100.0) - R(0.2, d200, x / 100.0)) > 0.05)
print("info  framing choice moves R by >0.05 once DELTA >= %.2f m for this subject size" % th)

# ---- P8: viewer inference from known size
ok8, vals = True, []
for V in (0.5, 1.5, 4.0):
    for screen_w in (0.3, 1.2):
        scale = screen_w / 0.036
        for f, d in ((0.024, d24), (0.2, d200)):
            ss, sb = img_h(f, d) * scale, img_h(f, d + delta) * scale
            zs, zb = V * H / ss, V * H / sb
            ok8 = ok8 and abs(zb / zs - (d + delta) / d) < 1e-9
            vals.append(zb / zs)
check("P8", ok8, "inferred depth ratios %.3f..%.3f (true %.3f for 24mm, %.3f for 200mm)" % (
    min(vals), max(vals), (d24 + delta) / d24, (d200 + delta) / d200))

# ---- P9: face scale
n1, n2 = (0.5 + 0.10) / 0.5, (3.0 + 0.10) / 3.0
check("P9", n1 >= 1.15 and n2 <= 1.04, "nose/ear magnification: 0.5 m %.3f, 3 m %.3f" % (n1, n2))

if FAIL:
    print("RESULT: FAIL missed predictions: " + ",".join(FAIL))
else:
    print("RESULT: PASS at fixed framing background/subject size ratio = d/(d+delta) (0.153 at 24mm/3.6m, 0.600 at 200mm/30m); "
          "focal length alone moves it by 0; crop reproduces tele exactly; only blur (%.1fx) and small delta/d bound the claim" % (b200 / b24))
