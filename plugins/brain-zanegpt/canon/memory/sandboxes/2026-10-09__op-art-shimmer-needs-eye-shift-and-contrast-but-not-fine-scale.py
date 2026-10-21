"""Sandbox: is Op-art motion 'in the eye'? Toy retinal-shift motion model.

A STATIC pattern is sampled on a pixel grid at several fixed sub-pixel retinal
offsets (a deterministic stand-in for fixational drift). A gradient (Lucas-
Kanade, 8x8 patch) motion estimator reports local motion per patch.
Metrics per scenario:
  energy    RMS of frame-to-frame luminance change (raw, contrast-dependent)
  flow      mean |patch flow| over patches whose gradient energy is above a
            fixed noise floor (contrast-normalised velocity estimate)
  coherence |mean flow vector| / mean |flow| over active patches
            (1 = whole image moves rigidly; low = patches move in different
            directions = 'shimmer' rather than a shifted object)
  active    fraction of patches above the noise floor
Stdlib only, no RNG, no timing.
"""
import math

N = 128         # image side (px)
P = 16          # patch side (v2: 16 so a patch holds >=1 cycle at lam=8..16)
NOISE = 1e-3    # fixed detector noise floor on mean squared gradient
# fixed drift steps (dx, dy) in units of amp, 8 directions, deterministic
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def straight(lam, c):
    # horizontal-line grating (gradient along y)
    return lambda x, y: c * math.sin(2 * math.pi * y / lam)


def riloid(lam, c, A=24.0, mu=96.0, s=1.0):
    # phase-modulated grating, a parametric stand-in for Riley-style 'Fall'; s scales the whole design
    A, mu, lam = A * s, mu * s, lam * s
    return lambda x, y: c * math.sin(2 * math.pi * (y + A * math.sin(2 * math.pi * x / mu)) / lam)


def checker(lam, c):
    return lambda x, y: c * math.sin(2 * math.pi * x / lam) * math.sin(2 * math.pi * y / lam)


def frame(f, dx, dy):
    return [[f(x + dx, y + dy) for x in range(N)] for y in range(N)]


def flows(f0, f1):
    """Per-patch (vx, vy, grad_energy) between two frames by regularised LK."""
    out = []
    for py in range(1, N // P - 1):
        for px in range(1, N // P - 1):
            sxx = sxy = syy = sxt = syt = g2 = 0.0
            n = 0
            for y in range(py * P, py * P + P):
                for x in range(px * P, px * P + P):
                    ix = (f0[y][x + 1] - f0[y][x - 1]) / 2.0
                    iy = (f0[y + 1][x] - f0[y - 1][x]) / 2.0
                    it = f1[y][x] - f0[y][x]
                    sxx += ix * ix; sxy += ix * iy; syy += iy * iy
                    sxt += ix * it; syt += iy * it
                    n += 1
            sxx /= n; sxy /= n; syy /= n; sxt /= n; syt /= n
            g2 = sxx + syy
            eps = 1e-9 + 1e-3 * g2
            a, b, d = sxx + eps, sxy, syy + eps
            det = a * d - b * b
            vx = -(d * sxt - b * syt) / det
            vy = -(-b * sxt + a * syt) / det
            out.append((vx, vy, g2))
    return out


def measure(f, amp, steps=8):
    en = 0.0; fl = 0.0; coh = 0.0; act = 0.0; m = 0; mc = 0; spr = 0.0
    base = frame(f, 0.0, 0.0)
    for k in range(steps):
        dx, dy = DIRS[k % 8]
        sh = frame(f, dx * amp, dy * amp)
        en += math.sqrt(sum((sh[y][x] - base[y][x]) ** 2 for y in range(N) for x in range(N)) / (N * N))
        fs = flows(base, sh)
        on = [(vx, vy) for vx, vy, g2 in fs if g2 > NOISE]
        act += len(on) / len(fs)
        if on:
            mags = [math.hypot(vx, vy) for vx, vy in on]
            mm = sum(mags) / len(on)
            sx = sum(v[0] for v in on) / len(on); sy = sum(v[1] for v in on) / len(on)
            fl += mm
            if mm > 0.05:   # v2: skip steps whose drift runs along the lines (no signal -> direction undefined)
                coh += math.hypot(sx, sy) / mm
                cs = sum(v[0] / math.hypot(*v) for v in on if math.hypot(*v) > 1e-9) / len(on)
                sn = sum(v[1] / math.hypot(*v) for v in on if math.hypot(*v) > 1e-9) / len(on)
                R = min(1.0, math.hypot(cs, sn))
                spr += math.degrees(math.sqrt(-2 * math.log(max(R, 1e-9))))
                mc += 1
        m += 1
    SPREAD[0] = spr / mc if mc else 0.0
    return en / m, fl / m, (coh / mc if mc else 0.0), act / m


def line(tag, r):
    e, fl, co, ac = r
    print(f"{tag:42s} energy={e:.4f} flow={fl:.3f} coherence={co:.3f} active={ac:.2f}")


SPREAD = [0.0]
checks = []
print("S1 incoherence: rigid shift of straight grating vs phase-modulated grating (lam=8, c=0.9, amp=0.5)")
rs = measure(straight(8, 0.9), 0.5); line("straight grating", rs)
rr = measure(riloid(8, 0.9), 0.5); line("riloid", rr)
rc = measure(checker(8, 0.9), 0.5); line("checker", rc)
checks.append(("H1 coherence straight>0.98", rs[2] > 0.98))
checks.append(("H1 coherence riloid<0.90", rr[2] < 0.90))

print("S2 no eye movement (amp=0): canvas is unchanged, no signal at all")
r0 = measure(riloid(8, 0.9), 0.0); line("riloid amp=0", r0)
checks.append(("H0 zero shift -> zero energy", r0[0] == 0.0))

print("S3 contrast sweep (riloid lam=8, amp=0.5)")
e = {}
for c in (0.1, 0.5, 0.9):
    r = measure(riloid(8, c), 0.5); line(f"contrast {c}", r); e[c] = r
ratio_c = e[0.9][0] / e[0.1][0]
print(f"energy ratio c=0.9/c=0.1 = {ratio_c:.2f}")
checks.append(("H3 contrast ratio in 8.5..9.5", 8.5 <= ratio_c <= 9.5))

print("S4 grating scale sweep, same design, same eye shift (riloid c=0.5, amp=0.5)")
sc = {}
for lam in (8, 16, 32, 64):
    r = measure(riloid(lam, 0.5), 0.5); line(f"lambda {lam}", r); sc[lam] = r
ratio_e = sc[8][0] / sc[32][0]
print(f"raw energy ratio lam8/lam32 = {ratio_e:.2f}")
checks.append(("H2 raw energy ratio 3..5", 3.0 <= ratio_e <= 5.0))
checks.append(("H4 flow lam32 within 20% of lam8", abs(sc[32][1] - sc[8][1]) / sc[8][1] < 0.20))

print("S5 low-contrast + coarse: detector floor kills it (riloid c=0.1)")
lo = {}
for lam in (8, 32, 64):
    r = measure(riloid(lam, 0.1), 0.5); line(f"c=0.1 lambda {lam}", r); lo[lam] = r
checks.append(("H5 active fraction falls to <0.2 at c=0.1 lam64", lo[64][3] < 0.2 and lo[8][3] > 0.8))

print("S6 BREAK: shift comparable to period (aliasing), straight grating c=0.9")
for lam, amp in ((8, 0.5), (4, 1.5), (2, 1.0)):
    r = measure(straight(lam, 0.9), amp); line(f"lam={lam} amp={amp}", r)
al = measure(straight(2, 0.9), 1.0)
ok = measure(straight(8, 0.9), 0.5)
checks.append(("H6 aliased flow no longer matches shift (>25% off)", abs(al[1] - 1.0) / 1.0 > 0.25 and abs(ok[1] - 0.5) / 0.5 < 0.35))

print("S7 paint the SAME design larger (all of lam, A, mu scaled by s), same eye shift, amp=0.5")
ws = {}
for sc_ in (1, 2, 4):
    r = measure(riloid(8, 0.5, s=sc_), 0.5); line(f"design x{sc_} c=0.5", r); ws[sc_] = r
wl = {}
for sc_ in (1, 2, 4):
    r = measure(riloid(8, 0.1, s=sc_), 0.5); line(f"design x{sc_} c=0.1", r); wl[sc_] = r
ratio_w = ws[1][0] / ws[4][0]
print(f"raw energy ratio x1/x4 = {ratio_w:.2f}; normalised flow x1={ws[1][1]:.2f} x4={ws[4][1]:.2f}")
checks.append(("H7a design energy ratio x1/x4 in 3..5", 3.0 <= ratio_w <= 5.0))
checks.append(("H7b normalised flow x4 within 25% of x1", abs(ws[4][1] - ws[1][1]) / ws[1][1] < 0.25))
checks.append(("H7c c=0.1 active >=0.8 at x1, <0.2 at x4", wl[1][3] >= 0.8 and wl[4][3] < 0.2))

print("S8 modulation steepness (slope = 2*pi*A/mu), riloid lam=16 c=0.9 amp=0.5 -- incoherence needs strongly bent lines")
sl = {}
for A_, mu_ in ((8, 192), (24, 96), (24, 48), (24, 32)):
    r = measure(riloid(16, 0.9, A=A_, mu=mu_), 0.5); sl[(A_, mu_)] = r
    line(f"A={A_} mu={mu_} slope={2*math.pi*A_/mu_:.2f}", r)
checks.append(("H8 steepest-bend coherence <0.90 and < gentlest", sl[(24, 32)][2] < 0.90 and sl[(24, 32)][2] < sl[(8, 192)][2]))

print("S9 direction spread (circular std of patch-flow angle, deg): the shimmer signature in Zanker & Walker's incoherent-motion account")
sp = {}
for tag, fn in (("straight", straight(16, 0.9)), ("riloid slope0.26", riloid(16, 0.9, A=8, mu=192)),
                ("riloid slope1.57", riloid(16, 0.9, A=24, mu=96)), ("riloid slope4.71", riloid(16, 0.9, A=24, mu=32))):
    measure(fn, 0.5); sp[tag] = SPREAD[0]; print(f"{tag:24s} spread={SPREAD[0]:.1f} deg")
checks.append(("H9 straight<5deg, steepest>20deg, monotone", sp["straight"] < 5 and sp["riloid slope4.71"] > 20 and sp["straight"] < sp["riloid slope0.26"] < sp["riloid slope1.57"] < sp["riloid slope4.71"]))

print()
for name, ok_ in checks:
    print(("ok   " if ok_ else "MISS ") + name)
nbad = sum(1 for _, o in checks if not o)
print(f"RESULT: {'PASS' if nbad == 0 else 'FAIL'} {len(checks)-nbad}/{len(checks)} predictions held; coherence straight={rs[2]:.2f} riloid={rr[2]:.2f}; energy ratio c9/c1={ratio_c:.2f}, lam8/lam32={ratio_e:.2f}; flow lam8={sc[8][1]:.2f} lam32={sc[32][1]:.2f}; direction spread straight={sp[chr(115)+chr(116)+chr(114)+chr(97)+chr(105)+chr(103)+chr(104)+chr(116)]:.0f}deg steepest-riloid={sp[chr(114)+chr(105)+chr(108)+chr(111)+chr(105)+chr(100)+chr(32)+chr(115)+chr(108)+chr(111)+chr(112)+chr(101)+chr(52)+chr(46)+chr(55)+chr(49)]:.0f}deg")
