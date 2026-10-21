"""Sandbox: where a horizontal-bodied biped's 'lean' lives (pitch balance about the hip).

Claims under test, for a theropod-like body (trunk, neck and tail roughly level,
balanced over the hip):
 A) pitching the whole trunk+neck+head+tail rigidly about the hip barely moves the
    fore-aft centre of mass (CoM), because the CoM sits near hip height and the
    fore-aft shift of a near-horizontal segment is second order in its angle;
 B) lowering/extending a raised S-curved neck is a first-order forward CoM shift,
    and straightening a nearly straight tail cannot cancel it (fails if the tail
    starts strongly drooped);
 C) during acceleration a the support must sit behind the CoM by h*a/g
    (di Prampero et al. 2005 lean angle, alpha = arctan(g/a)); for a horizontal
    biped that offset has to come from where the feet are planted, and the leg's
    reach (dlist/E3) caps the sustainable acceleration.

Iteration history: run 1 predicted < 1 cm per 10 deg of pitch and ~2 cm for the
neck; observed 1.09 cm and 1.03 cm, so A and B are the SAME size, not first vs
second order. Run 2 (this file) tests the surviving claim: every posture change
is under a tenth of the support offset an acceleration needs; and it uses the
demo's mean pelvis height per speed (run 1 used a fixed 1.12 m hip).

Geometry from demos/skin-test/index.html. Segment mass fractions are ASSUMED and
swept. Deterministic, stdlib only.
"""
import math

G = 9.81
HIP = (1.18, 0.0)  # (y, z) pelvis joint in body frame, z forward

J = {
    "pelvis": (1.18, 0.0), "spine1": (1.2, 0.38), "spine2": (1.19, 0.74), "chest": (1.15, 1.05),
    "neck1": (1.2, 1.3), "neck2": (1.36, 1.5), "neck3": (1.52, 1.66), "head": (1.62, 1.8), "snout": (1.53, 2.36),
}
TAIL = [(1.18, 0.0), (1.17, -0.3), (1.14, -0.7), (1.1, -1.1), (1.05, -1.5), (1.0, -1.88), (0.95, -2.24), (0.9, -2.56), (0.86, -2.86)]


def poly_points(pts, mass, taper=False, n=200):
    """Spread `mass` along a polyline as n point masses (linear taper to zero if asked)."""
    segs = list(zip(pts, pts[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    total = sum(lens)
    out = []
    for i in range(n):
        s = (i + 0.5) / n * total
        acc = 0
        for (a, b), L in zip(segs, lens):
            if acc + L >= s:
                t = (s - acc) / L
                p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                break
            acc += L
        w = (1 - s / total) if taper else 1.0
        out.append([p, w])
    wsum = sum(w for _, w in out)
    return [(p, mass * w / wsum) for p, w in out]


def com(points):
    m = sum(w for _, w in points)
    return (sum(p[0] * w for p, w in points) / m, sum(p[1] * w for p, w in points) / m)


def rot_about(p, c, th):
    """Rotate (y, z) point p about c by th (positive = nose down)."""
    dy, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dy * math.cos(th) - dz * math.sin(th), c[1] + dy * math.sin(th) + dz * math.cos(th))


def neck_chain(extended):
    if not extended:
        return [J["neck1"], J["neck2"], J["neck3"], J["head"]], [J["head"], J["snout"]]
    lens = [math.dist(J["neck1"], J["neck2"]), math.dist(J["neck2"], J["neck3"]), math.dist(J["neck3"], J["head"])]
    ang = math.radians(-5)  # neck straightened, aimed 5 deg below level
    pts = [J["neck1"]]
    for L in lens:
        y, z = pts[-1]
        pts.append((y + L * math.sin(ang), z + L * math.cos(ang)))
    hd = (J["snout"][0] - J["head"][0], J["snout"][1] - J["head"][1])
    return pts, [pts[-1], (pts[-1][0] + hd[0], pts[-1][1] + hd[1])]


def tail_chain(droop_deg, straight):
    base = TAIL[0]
    if straight:
        L = sum(math.dist(a, b) for a, b in zip(TAIL, TAIL[1:]))
        pts = [base, (base[0], base[1] - L)]
    else:
        pts = TAIL
    extra = math.radians(droop_deg)
    return [rot_about(p, base, extra) for p in pts]  # extra droop: tail tip down


def body(fr, neck_ext=False, tail_droop=0.0, tail_straight=False, pitch=0.0):
    """Upper body (pitches about hip) + legs (do not pitch). fr = mass fractions."""
    upper = []
    upper += poly_points([J["pelvis"], J["spine1"], J["spine2"], J["chest"]], fr["trunk"])
    nk, hd = neck_chain(neck_ext)
    upper += poly_points(nk, fr["neck"])
    upper += poly_points(hd, fr["head"])
    upper += poly_points([(0.95, 0.9), (0.75, 1.05)], fr["arms"])
    upper += poly_points(tail_chain(tail_droop, tail_straight), fr["tail"], taper=True)
    upper = [(rot_about(p, HIP, pitch), w) for p, w in upper]
    legs = poly_points([(1.14, 0.02), (0.66, 0.22), (0.2, -0.06), (0.035, 0.1)], fr["legs"])
    return upper + legs


def fracs(tail, headneck):
    rest = 1 - tail - headneck - 0.02 - 0.15
    return {"trunk": rest, "neck": headneck / 2, "head": headneck / 2, "arms": 0.02, "legs": 0.15, "tail": tail}


fails = []
cases = [(t, hn) for t in (0.12, 0.18, 0.25) for hn in (0.06, 0.09, 0.12)]

# S1: rigid pitch about the hip.
print("S1 rigid pitch of trunk+neck+head+tail about hip")
worst_pitch = 0
for t, hn in cases:
    fr = fracs(t, hn)
    z0 = com(body(fr))[1]
    for deg in (5, 10, -10):
        dz = com(body(fr, pitch=math.radians(deg)))[1] - z0
        worst_pitch = max(worst_pitch, abs(dz) / abs(deg) * 10)
print(f"  worst fore-aft CoM shift per 10 deg of pitch over 9 mass splits: {worst_pitch * 100:.2f} cm")

# S2: neck extension vs tail straightening (demo tail).
print("S2 neck extension vs straightening the demo tail")
ratios = []
for t, hn in cases:
    fr = fracs(t, hn)
    z0 = com(body(fr))[1]
    dn = com(body(fr, neck_ext=True))[1] - z0
    dt = com(body(fr, tail_straight=True))[1] - z0
    ratios.append(abs(dt) / dn)
    if (t, hn) == (0.18, 0.09):
        print(f"  tail 18%, head+neck 9%: neck extension {dn * 100:+.2f} cm, tail straightening {dt * 100:+.2f} cm")
demo_droop = math.degrees(math.atan2(TAIL[0][0] - TAIL[-1][0], -TAIL[-1][1]))
print(f"  demo tail chord droop {demo_droop:.1f} deg; tail/neck cancel ratio range {min(ratios):.2f}-{max(ratios):.2f}")
if max(ratios) >= 0.2:
    fails.append("tail cancels >= 20% of neck shift")

# S3 (BUILT TO BREAK claim B): a strongly drooped tail, straightened.
print("S3 BREAK: tail starting 30 deg drooped, then straightened")
fr = fracs(0.18, 0.09)
z0 = com(body(fr, tail_droop=30))[1]
dt30 = com(body(fr, tail_straight=True))[1] - z0
dn = com(body(fr, neck_ext=True))[1] - com(body(fr))[1]
print(f"  straightening from 30 deg: {dt30 * 100:+.2f} cm vs neck extension {dn * 100:+.2f} cm -> ratio {abs(dt30) / dn:.2f}")
break_ok = abs(dt30) / dn > 0.6  # the claim should FAIL here

# S4: acceleration lean.
fr = fracs(0.18, 0.09)
hc = com(body(fr))[0]
print(f"S4 CoM height {hc:.2f} m")
for a in (1.0, 3.0, -6.5):
    off = hc * a / G
    print(f"  a={a:+.1f} m/s^2: support {abs(off):.2f} m {'behind' if a > 0 else 'ahead of'} CoM, line angle from vertical {math.degrees(math.atan2(abs(a), G)):.1f} deg")
off3 = hc * 3.0 / G


# S5: compose with dlist/E3 reach (heel lift): max acceleration whose support offset fits.
def alexander_stride(v, h=1.18):
    return 2.3 * (v * v / (G * h)) ** 0.3 * h


def froude_duty(v, L=1.15):
    fr_ = v * v / (G * L)
    return 0.5 + 0.14 * math.tanh((0.5 - fr_) / 0.25)


REACH_LIFT = 0.522 + 0.539 + 0.230
BALL_Z = 0.10


def hipj(v):  # demo: pelvis drops 0.04*sf at speed plus a mean bob of half its amplitude
    sf = min(v / 7.4, 1.0)
    return (1.14 - 0.04 * sf - 0.5 * (0.012 + 0.016 * v), 0.02)


def fits(v, shift):
    half = 0.5 * froude_duty(v) * alexander_stride(v)
    for i in range(201):
        dz = half - 2 * half * i / 200 - shift
        if math.dist((0.035, BALL_Z + dz), hipj(v)) > REACH_LIFT:
            return False
    return True


print("S5 reach-limited acceleration (stance window shifted back by h*a/g, heel-lift reach)")
amax = {}
for v in (1.0, 2.0, 3.0, 5.0, 7.0):
    lo, hi = 0.0, 10.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if fits(v, hc * mid / G):
            lo = mid
        else:
            hi = mid
    amax[v] = lo
    print(f"  v={v:.1f} m/s: stance {froude_duty(v) * alexander_stride(v):.2f} m, max sustainable a={lo:.2f} m/s^2")

posture_max = max(worst_pitch, dn, abs(dt30))
print(f"  largest posture-driven CoM shift {posture_max * 100:.2f} cm = {posture_max / off3:.3f} of the a=3 support offset")
if posture_max > 0.1 * off3:
    fails.append("posture shift >= 10% of accel offset")
ok = not fails and break_ok
if ok:
    print(f"RESULT: PASS posture moves CoM <= {posture_max * 100:.2f} cm ({posture_max / off3:.3f} of the {off3:.2f} m support offset a=3 m/s^2 needs): pitch {worst_pitch * 100:.2f} cm per 10 deg, neck extension {dn * 100:+.2f} cm vs demo-tail straightening cancels {min(ratios):.2f}-{max(ratios):.2f} of it, a 30-deg-drooped tail cancels {abs(dt30) / dn:.2f} (break holds); reach caps a at {amax[2.0]:.2f}/{amax[5.0]:.2f}/{amax[7.0]:.2f} m/s^2 at 2/5/7 m/s")
else:
    print(f"RESULT: FAIL fails={fails} break_ok={break_ok} ratio30={abs(dt30) / dn:.2f}")
