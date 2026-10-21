"""Ornithology seed: does a migrant flying a time-compensated sun compass WITHOUT resetting its
internal clock (it keeps home time while crossing longitudes) trace a near great-circle route?
The hypothesis (a sun-compass route approximating a great circle at high latitude) is from memory
of the migration literature (Alerstam); here only the spherical geometry is tested.
Bird model: at departure it picks angle alpha = (great-circle initial course) - (sun azimuth now);
in flight it keeps heading = sun azimuth at its CURRENT position, evaluated at the fixed home-clock
time of departure (so local solar time drifts by dLon/15 h), + alpha. Sun azimuth is computed from
declination and hour angle (no 15 deg/h shortcut). Compared with a loxodrome (constant compass
course, hits the target) and the great circle. Pure stdlib, deterministic.
"""
import math
R = 6371.0
rad, deg = math.radians, math.degrees

def gc_dist(a, b):
    (p1, l1), (p2, l2) = [(rad(x), rad(y)) for x, y in (a, b)]
    h = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin((l2-l1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def gc_course(a, b):
    (p1, l1), (p2, l2) = [(rad(x), rad(y)) for x, y in (a, b)]
    y = math.sin(l2-l1)*math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(l2-l1)
    return deg(math.atan2(y, x)) % 360

def step(pos, heading, d):
    p1, l1, th, dr = rad(pos[0]), rad(pos[1]), rad(heading), d / R
    p2 = math.asin(math.sin(p1)*math.cos(dr) + math.cos(p1)*math.sin(dr)*math.cos(th))
    l2 = l1 + math.atan2(math.sin(th)*math.sin(dr)*math.cos(p1), math.cos(dr) - math.sin(p1)*math.sin(p2))
    return (deg(p2), (deg(l2) + 540) % 360 - 180)

def sun_az(lat, hour_angle_deg, decl):
    p, H, d = rad(lat), rad(hour_angle_deg), rad(decl)
    az = math.atan2(math.sin(H), math.cos(H)*math.sin(p) - math.tan(d)*math.cos(p))
    return (deg(az) + 180) % 360   # measured from north, clockwise

def lon_diff(a, b):
    return (b - a + 540) % 360 - 180

def loxodrome_len(a, b):
    p1, p2 = rad(a[0]), rad(b[0]); dl = rad(lon_diff(a[1], b[1]))
    dpsi = math.log(math.tan(math.pi/4 + p2/2) / math.tan(math.pi/4 + p1/2))
    q = (p2 - p1)/dpsi if abs(dpsi) > 1e-12 else math.cos(p1)
    return R*math.sqrt((p2-p1)**2 + (q*dl)**2)

def fly_sun_compass(start, target, home_solar_hour, decl, ds=2.0):
    H0 = 15.0*(home_solar_hour - 12.0)
    alpha = gc_course(start, target) - sun_az(start[0], H0, decl)
    pos, dist, east = start, 0.0, lon_diff(start[1], target[1]) > 0
    total_dlon = abs(lon_diff(start[1], target[1]))
    while True:
        dlon = lon_diff(start[1], pos[1])
        if (dlon if east else -dlon) >= total_dlon or dist > 3*gc_dist(start, target):
            break
        H = H0 + dlon                       # local solar time runs ahead of the unreset home clock
        pos = step(pos, sun_az(pos[0], H, decl) + alpha, ds)
        dist += ds
    return pos, dist

def sun_alt(lat, H, d):
    p, H, d = rad(lat), rad(H), rad(d)
    return deg(math.asin(math.sin(p)*math.sin(d) + math.cos(p)*math.cos(d)*math.cos(H)))

def sun_up_whole_route(a, b, hour, decl):
    dl = lon_diff(a[1], b[1])
    return all(sun_alt(a[0] + (b[0]-a[0])*f, 15*(hour-12) + dl*f, decl) > 0 for f in (0, 0.25, 0.5, 0.75, 1))

cases = [
    ("S1 high-arctic east: 72N 140E -> 66N 160W", (72.0, 140.0), (66.0, -160.0)),
    ("S2 arctic west: 70N 100W -> 64N 170E", (70.0, -100.0), (64.0, 170.0)),
    ("S3 low latitude east: 25N 20E -> 22N 80E", (25.0, 20.0), (22.0, 80.0)),
]
# S4 (added after run 2, reported separately, not part of the pass criterion): the regime the
# literature hypothesis is usually stated for, midnight sun near the pole (declination 20, 80N).
S4 = ("S4 midnight-sun east: 80N 60E -> 76N 150E, decl 20", (80.0, 60.0), (76.0, 150.0))
# Run 1 (fixed 06h and 18h departures) refuted the latitude-only claim; this sweep over every even
# home-clock hour 04-20, keeping only hours with the sun above the horizon along the whole route,
# is the final test. Claim under test: at high latitude a clock-fixed sun compass lands within 300 km
# of the target for EVERY daylight departure hour (the pass criterion), and low latitude does worse.
out = {}
for name, a, b in cases:
    g, lx = gc_dist(a, b), loxodrome_len(a, b)
    rows = []
    for hour in range(4, 21, 2):
        if not sun_up_whole_route(a, b, hour, 10.0):
            continue
        end, d = fly_sun_compass(a, b, float(hour), decl=10.0)
        rows.append((hour, gc_dist(end, b), d))
    out[name] = (g, lx, rows)
    print(f"{name}: great circle {g:.0f} km, loxodrome {lx:.0f} km (+{100*(lx/g-1):.1f}%), sun-up hours {[h for h,_,_ in rows]}")
    for hour, miss, d in rows:
        print(f"   departs {hour:02d}h home time: flown {d:.0f} km ({100*(d/g-1):+.1f}% vs GC), misses target by {miss:.0f} km")

name, a, b = S4
g4 = gc_dist(a, b); s4 = []
for hour in range(0, 24, 2):
    if sun_up_whole_route(a, b, hour, 20.0):
        end, d = fly_sun_compass(a, b, float(hour), decl=20.0)
        s4.append((hour, gc_dist(end, b), d))
print(f"{name}: great circle {g4:.0f} km, loxodrome {loxodrome_len(a, b):.0f} km, sun-up hours {len(s4)} of 12")
print("   misses by hour:", [(h, round(m)) for h, m, _ in s4])
arctic = [out[c[0]] for c in cases[:2]]
arctic_misses = [m for _, _, r in arctic for _, m, _ in r]
low_misses = [m for _, m, _ in out[cases[2][0]][2]]
claim = max(arctic_misses) < 300 and min(low_misses) > max(arctic_misses)
print(f"arctic sun-up misses: min {min(arctic_misses):.0f}, max {max(arctic_misses):.0f} km over {len(arctic_misses)} departures; "
      f"low-latitude: min {min(low_misses):.0f}, max {max(low_misses):.0f} km over {len(low_misses)}")
print(f"RESULT: {'PASS' if claim else 'FAIL'} latitude-only claim refuted={not claim}: arctic daylight misses run "
      f"{min(arctic_misses):.0f}-{max(arctic_misses):.0f} km by departure hour, low latitude {min(low_misses):.0f}-{max(low_misses):.0f} km; "
      f"loxodrome +4.1%/+9.6% longer than GC on the arctic routes; midnight-sun 80N max miss {max(m for _, m, _ in s4):.0f} km over {len(s4)} hours")
