"""Train kernel (apply): SUNDIALS/horizontal-dial - a vertical stick's shadow
is not a polar-aligned style, so its geometry changes with season - applied to
WAYFINDING (seven E91: the visible sky is the navigation dial; a fixed cue
pulls heading toward the intended bearing).
Two uses of the sun a lost walker actually has:
 (1) the shadow-tip method: mark a vertical stick's shadow tip twice, the line
     from first to second mark is taken as west->east;
 (2) holding the sun at a fixed angle and correcting 15 degrees per hour.
Exact spherical geometry, no rng. Sun vector in east-north-up from latitude,
declination and hour angle; vertical stick height 1.
PREDICTION (written before running): at the equinox the shadow-tip line is
exactly east-west at any hour (error < 0.1 deg); at the June solstice, lat 40,
marks 30 min apart give errors of several degrees in mid-morning (>= 5 deg at
09:00) and less near noon; (2) the 15 deg/h correction is close at the
equinox but near noon in June at lat 40 the sun's azimuth moves > 40 deg/h, so
a walker correcting 15 deg/h turns > 25 deg between 11:00 and 13:00 - a biased
cue that, in E91's walker model, makes the path curve instead of loop.
"""
import math, sys
print("python", sys.version.split()[0])
r = math.radians
def sun(lat, dec, hours_from_noon):
    H = r(15 * hours_from_noon); p, d = r(lat), r(dec)
    E = -math.cos(d) * math.sin(H)
    N = math.sin(d) * math.cos(p) - math.cos(d) * math.cos(H) * math.sin(p)
    U = math.sin(d) * math.sin(p) + math.cos(d) * math.cos(H) * math.cos(p)
    return E, N, U
def tip(lat, dec, h):
    E, N, U = sun(lat, dec, h); return (-E / U, -N / U)
def az(lat, dec, h):
    E, N, U = sun(lat, dec, h); return math.degrees(math.atan2(E, N)) % 360
def tip_error(lat, dec, h, gap=0.5):
    (x1, y1), (x2, y2) = tip(lat, dec, h), tip(lat, dec, h + gap)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))   # 0 = due east
    return abs((ang + 180) % 360 - 180)
rows = {}
for lat in (20, 40, 55):
    for dec, nm in ((0, "equinox"), (23.44, "June"), (-23.44, "Dec")):
        errs = {clock: tip_error(lat, dec, clock - 12) for clock in (9, 10.5, 11.75, 13.5)}
        rows[(lat, nm)] = errs
        print(f"lat {lat} {nm:7s} shadow-tip error deg: " + ", ".join(f"{c:>5}h {e:5.2f}" for c, e in errs.items()))
def az_rate(lat, dec, h, dh=1 / 60):
    a, b = az(lat, dec, h), az(lat, dec, h + dh)
    return ((b - a + 180) % 360 - 180) / dh
for lat, dec, nm in ((40, 0, "equinox"), (40, 23.44, "June"), (20, 23.44, "June")):
    print(f"lat {lat} {nm}: azimuth rate deg/h at 09 {az_rate(lat,dec,-3):5.1f}, 11 {az_rate(lat,dec,-1):5.1f}, 12 {az_rate(lat,dec,0):5.1f}")
def walker_turn(lat, dec, h0, h1):
    """walker keeps the sun at a fixed relative angle, corrected 15 deg/h: net heading change."""
    sweep = (az(lat, dec, h1) - az(lat, dec, h0) + 180) % 360 - 180
    return sweep - 15 * (h1 - h0)
wt_eq = walker_turn(40, 0, -1, 1); wt_june = walker_turn(40, 23.44, -1, 1); wt_june20 = walker_turn(20, 23.44, -1, 1)
print(f"walker 11:00-13:00 with 15 deg/h correction: lat 40 equinox turns {wt_eq:.1f} deg, June {wt_june:.1f}, lat 20 June {wt_june20:.1f}")
# E91-style walker: cue pulls heading toward a bearing that drifts as the residual accumulates
def walk(bias_deg_per_h, hours=2, k=0.05, steps_per_h=4800):
    h = 0.0; x = y = 0.0
    for i in range(int(hours * steps_per_h)):
        target = math.radians(bias_deg_per_h * i / steps_per_h)
        h -= k * math.atan2(math.sin(h - target), math.cos(h - target))
        x += 0.75 * math.cos(h); y += 0.75 * math.sin(h)
    return math.degrees(h), math.hypot(x, y) / (0.75 * hours * steps_per_h)
fin, st = walk(wt_june / 2)
print(f"E91-style walker with that residual: final heading off by {fin:.1f} deg, straightness {st:.3f}")
eq_ok = all(e < 0.1 for (lat, nm), errs in rows.items() if nm == "equinox" for e in errs.values())
c = [eq_ok, rows[(40, "June")][9] >= 5, rows[(40, "June")][11.75] < rows[(40, "June")][9],
     abs(wt_eq) < 10, abs(wt_june) > 25]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; shadow-tip equinox exact={eq_ok}; lat40 June error 09h {rows[(40,'June')][9]:.2f} 11:45 {rows[(40,'June')][11.75]:.2f} deg; 15 deg/h walker 11-13h turns eq {wt_eq:.1f}, June lat40 {wt_june:.1f}, lat20 {wt_june20:.1f} deg; E91 walker final heading {fin:.1f} deg straightness {st:.3f}")
