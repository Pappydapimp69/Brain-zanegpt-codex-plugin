"""Sandbox: where is a buried avalanche transceiver relative to the lowest distance reading?

Model: the buried transmitter is a magnetic dipole at depth d (metres) below a flat
snow surface. The searcher's receiver reads the field magnitude
|B| ~ sqrt(1 + 3 cos^2(theta)) / r^3 (theta = angle between the dipole axis and the
line to the receiver) and displays an equivalent distance (|B|/|B|_ref)^(-1/3),
calibrated so a receiver directly on the dipole's broadside reads the true range,
rounded to 0.1 m as many displays do. The searcher pinpoints along a surface line
lying in the plane of the dipole axis. Measures: half-width of the surface stretch
showing the minimum reading (plateau), offset of the true field maximum from the
point directly above the transmitter, and the error of the bracket midpoint
(midpoint of the two surface points showing min + 0.3 m).
Deterministic, stdlib only.
"""
from math import sin, cos, radians, sqrt

STEP = 0.001  # 1 mm surface sampling
XS = [i * STEP for i in range(-6000, 6001)]


def field(x, d, tilt_deg):
    # transmitter at (0, -d); axis tilted tilt_deg from horizontal, in the x-z plane
    t = radians(tilt_deg)
    mx, mz = cos(t), sin(t)
    rx, rz = x, d
    r = sqrt(rx * rx + rz * rz)
    c = (mx * rx + mz * rz) / r
    return sqrt(1 + 3 * c * c) / r ** 3


def display(b):
    # broadside calibration: |B| = 1/r^3 reads r
    return round(b ** (-1.0 / 3.0) + 1e-12, 1)


def analyse(d, tilt):
    bs = [field(x, d, tilt) for x in XS]
    imax = max(range(len(XS)), key=lambda i: bs[i])
    x_peak = XS[imax]
    disp = [display(b) for b in bs]
    dmin = min(disp)
    plateau = [XS[i] for i in range(len(XS)) if disp[i] == dmin]
    half_width = (max(plateau) - min(plateau)) / 2
    plateau_mid = (max(plateau) + min(plateau)) / 2
    # bracket: outermost surface points still at or under dmin + 0.3 m
    target = round(dmin + 0.3, 1)
    inside = [XS[i] for i in range(len(XS)) if disp[i] <= target]
    bracket_mid = (max(inside) + min(inside)) / 2
    return dmin, half_width, x_peak, plateau_mid, bracket_mid


rows = {}
print("depth  tilt  min_read  plateau_halfwidth  field_peak_x  plateau_mid_x  bracket_mid_x")
for d in (1.0, 2.0, 3.0):
    for tilt in (0, 30, 45, 60, 90):
        res = analyse(d, tilt)
        rows[(d, tilt)] = res
        dmin, hw, xp, pm, bm = res
        print(f"{d:4.1f}  {tilt:4d}  {dmin:7.1f}  {hw:16.3f}  {xp:12.3f}  {pm:13.3f}  {bm:13.3f}")

# probe spiral cost to cover the uncertainty (25 cm grid, an assumed spacing)
def probes_to_cover(radius, spacing=0.25):
    n = 0
    k = int(radius / spacing) + 1
    for i in range(-k, k + 1):
        for j in range(-k, k + 1):
            if (i * spacing) ** 2 + (j * spacing) ** 2 <= radius ** 2 + 1e-9:
                n += 1
    return n

for d in (1.0, 2.0, 3.0):
    worst = max(abs(rows[(d, t)][4]) for t in (0, 30, 45, 60, 90))
    hw0 = rows[(d, 0)][1]
    print(f"depth {d}: worst bracket-mid error {worst:.3f} m; flat-burial plateau half-width {hw0:.3f} m; "
          f"probes to cover r=plateau {probes_to_cover(hw0)}, r=error+0.25 {probes_to_cover(worst + 0.25)}")

rule_ok = True
for d in (1.0, 2.0, 3.0):
    worst = max(abs(rows[(d, t)][4]) for t in (0, 30, 45, 60, 90))
    radius = d / 4 + 0.25
    rule_ok = rule_ok and radius >= worst
    print(f"rule radius depth/4+0.25 at {d} m = {radius:.2f} m covers worst {worst:.3f} m: {radius >= worst}; probes {probes_to_cover(radius)}")

flat2 = rows[(2.0, 0)]
vert2 = rows[(2.0, 90)]
tilt2 = rows[(2.0, 45)]
tilt1 = rows[(1.0, 45)]
tilt3 = rows[(3.0, 45)]
checks = [
    ("symmetric burials: bracket midpoint exact (<1 cm)", all(abs(rows[(d, t)][4]) < 0.01 for d in (1.0, 2.0, 3.0) for t in (0, 90))),
    ("flat burial plateau wider than vertical at 2 m", flat2[1] > vert2[1]),
    ("min reading equals depth for flat burial", all(abs(rows[(d, 0)][0] - d) < 0.051 for d in (1.0, 2.0, 3.0))),
    ("45-degree tilt moves the field peak off the burial", abs(tilt2[2]) > 0.05),
    ("depth/4 + one spacing covers the worst bracket error", rule_ok),
    ("tilt offset grows with depth", abs(tilt1[2]) < abs(tilt2[2]) < abs(tilt3[2])),
]
for name, ok in checks:
    print(f"  check {name}: {ok}")
allok = all(ok for _, ok in checks)
print(f"RESULT: {'PASS' if allok else 'FAIL'} at 2 m a flat beacon shows its minimum over +/-{flat2[1]:.2f} m "
      f"(vertical +/-{vert2[1]:.2f} m); bracket midpoint exact when symmetric, but a 45-degree tilt puts the field peak "
      f"{abs(tilt1[2]):.2f}/{abs(tilt2[2]):.2f}/{abs(tilt3[2]):.2f} m off at 1/2/3 m and the bracket midpoint "
      f"{abs(tilt1[4]):.2f}/{abs(tilt2[4]):.2f}/{abs(tilt3[4]):.2f} m off")
