"""Two-light Lambertian face model: does the key:fill ratio alone set contrast?
Stdlib only, deterministic, no RNG, no timing.
Pipeline: light levels -> Lambert -> exposure (stops) -> clip -> tone curve ->
8-bit quantise -> display lightness L*. Contrast metric = delta L* between a lit
site and a shadow site.
"""
import math

LIT_TARGET = 0.4   # scene-linear value the lit patch is normalised to
checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(("ok   " if ok else "FAIL ") + name + " :: " + detail)


# ---------- tone curves: scene-linear (post exposure, clipped) -> display linear
def srgb_enc(x):
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def srgb_dec(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def curve_srgb(x):
    return min(1.0, max(0.0, x))


def curve_gamma22(x):  # simple power system; quantised in its own gamma domain
    return min(1.0, max(0.0, x))


def curve_filmic(x):  # S curve with toe and shoulder (logistic in log2 domain)
    x = max(x, 1e-9)
    s = math.log2(x / 0.18)
    y = 1.0 / (1.0 + math.exp(-0.9 * s))
    lo = 1.0 / (1.0 + math.exp(0.9 * 7))
    hi = 1.0 / (1.0 + math.exp(-0.9 * 3))
    return min(1.0, max(0.0, (y - lo) / (hi - lo)))


def display(x, curve="srgb"):
    """scene-linear after exposure -> (8-bit code, display linear light)."""
    if curve == "srgb":
        v = curve_srgb(x)
        code = round(255 * srgb_enc(v))
        return code, srgb_dec(code / 255)
    if curve == "gamma22":
        v = curve_gamma22(x)
        code = round(255 * v ** (1 / 2.2))
        return code, (code / 255) ** 2.2
    v = curve_filmic(x)
    code = round(255 * srgb_enc(v))
    return code, srgb_dec(code / 255)


def lstar(y):
    return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16


def dlstar(lit, shadow, exposure_gain, curve="srgb"):
    cl, yl = display(lit * exposure_gain, curve)
    cs, ys = display(shadow * exposure_gain, curve)
    return lstar(yl) - lstar(ys), cl, cs


# ---------- light vectors, Lambert sites
def unit(v):
    n = math.sqrt(sum(a * a for a in v))
    return tuple(a / n for a in v)


def ldir(az_deg, el_deg):  # +x = subject's right as seen from camera, +z toward camera
    az, el = math.radians(az_deg), math.radians(el_deg)
    return (math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el))


def lam(n, l):
    return max(0.0, sum(a * b for a, b in zip(n, l)))


def total_ratio_from_label(kind, label):
    """Return (K, F) lux for a nominal label read four different ways, F=1."""
    if kind == "KF_lux":      # 8:1 = key lux : fill lux
        return float(label), 1.0
    if kind == "total_lux":   # 8:1 = (key+fill) : fill
        return float(label) - 1.0, 1.0
    if kind == "stops_total":  # 8 stops = 2**8 : 1 total
        return 2.0 ** label - 1.0, 1.0
    if kind == "stops_as_ratio":  # '3' stops misread as 3:1 key:fill
        return float(label), 1.0
    raise ValueError(kind)


def cast_shadow_pair(K, F, A):
    """Standard textbook sites: lit side gets K+F+A, key-occluded side F+A."""
    return K + F + A, F + A


def cheek_pair(K, F, A, key_az=45.0, key_el=0.0, fill_az=-45.0, fill_el=0.0, cheek=35.0):
    """Cheeks of a sphere-ish head, normals +-cheek deg from camera axis.
    Key from subject-left (negative x): lit cheek is the left one."""
    lk, lf = ldir(-key_az, key_el), ldir(-fill_az, fill_el)
    nl, ns = ldir(-cheek, 0), ldir(cheek, 0)
    lit = K * lam(nl, lk) + F * lam(nl, lf) + A
    sh = K * lam(ns, lk) + F * lam(ns, lf) + A
    return lit, sh


def sphere_percentiles(K, F, A, key_az=45.0, key_el=20.0, fill_az=-45.0, fill_el=0.0, n=48):
    lk, lf = ldir(-key_az, key_el), ldir(-fill_az, fill_el)
    vals = []
    for i in range(n):
        for j in range(n):
            x = -0.9 + 1.8 * (i + 0.5) / n
            y = -0.9 + 1.8 * (j + 0.5) / n
            r2 = x * x + y * y
            if r2 > 0.81:
                continue
            nrm = (x, y, math.sqrt(1 - r2))
            vals.append(K * lam(nrm, lk) + F * lam(nrm, lf) + A)
    vals.sort()
    p = lambda q: vals[int(q * (len(vals) - 1))]
    return p(0.05), p(0.95)


def stops(r):
    return math.log2(r)


# =========================================================== P8 arithmetic
check("P8a 2 stops=4:1, 3 stops=8:1", 2 ** 2 == 4 and 2 ** 3 == 8, "exact powers of two")

# =========================================================== P1 normalised exposure
print("\n[P1] normalised exposure: lit patch pinned to %.2f scene-linear" % LIT_TARGET)
spreads = []
for ratio in (2.0, 9.0):
    ds = []
    for b in range(-3, 4):  # brightness sweep in stops
        K, F = 8 * 2.0 ** b, 1 * 2.0 ** b
        K, F = (ratio - 1) * 2.0 ** b, 1 * 2.0 ** b
        lit, sh = cast_shadow_pair(K, F, 0.0)
        gain = LIT_TARGET / lit
        d, _, _ = dlstar(lit, sh, gain)
        ds.append(d)
    spreads.append(max(ds) - min(ds))
    print("  total %.1f:1  DeltaL* over -3..+3 stops brightness: min %.2f max %.2f" % (ratio, min(ds), max(ds)))
check("P1 brightness irrelevant when exposure normalised", max(spreads) < 1.5, "worst spread %.3f L*" % max(spreads))

ladder = [1.5, 2, 4, 8, 16, 64, 256]
lad = []
for r in ladder:
    lit, sh = r, 1.0
    d, _, cs = dlstar(lit, sh, LIT_TARGET / lit)
    lad.append(d)
print("  ladder total-ratio %s -> DeltaL* %s" % (ladder, [round(x, 1) for x in lad]))
check("P1 ladder monotonic in ratio", all(b > a for a, b in zip(lad, lad[1:])), "strictly increasing")
d15, d2, d8, d16 = lad[0], lad[1], lad[3], lad[4]
check("P8b 1.5:1 vs 2:1 barely separated, 2:1 vs 8:1 clearly", (d2 - d15) < 10 and (d8 - d2) > 15,
      "1.5->2 gives +%.1f L*, 2->8 gives +%.1f L*, 8->16 gives +%.1f L*" % (d2 - d15, d8 - d2, d16 - d8))

# =========================================================== P2 fixed exposure (BREAK)
print("\n[P2] BREAK: exposure frozen, key brightness varied at constant 8:1 K/F")
base_K, base_F = 8.0, 1.0
lit0, sh0 = cast_shadow_pair(base_K, base_F, 0.0)
gain0 = LIT_TARGET / lit0
row = {}
for b in range(-4, 5):
    K, F = base_K * 2.0 ** b, base_F * 2.0 ** b
    lit, sh = cast_shadow_pair(K, F, 0.0)
    d, cl, cs = dlstar(lit, sh, gain0)
    row[b] = d
    print("  brightness %+d st: lit code %3d shadow code %3d DeltaL* %.1f" % (b, cl, cs, d))
dev1 = max(abs(row[1] - row[0]), abs(row[-1] - row[0]))
dev3 = max(abs(row[3] - row[0]), abs(row[-3] - row[0]))
check("P2a +-1 stop of brightness tolerable", dev1 < 12, "max shift %.1f L*" % dev1)
check("P2b +-3 stops of brightness breaks ratio-only claim", dev3 > 20, "max shift %.1f L*" % dev3)
fx = [dlstar(r, 1.0, gain0 * 1.0)[0] for r in (2, 8)]  # ratio ladder at fixed exposure, shadow=1
print("  ratio effect at fixed exposure (lit fixed): 2:1 %.1f L*, 8:1 %.1f L*" % (fx[0], fx[1]))

# =========================================================== P3 stops vs lux readings of '8:1'
print("\n[P3] one label, four readings (cast-shadow site, normalised, sRGB 8-bit)")
reads = {}
for kind, label in (("KF_lux", 8), ("total_lux", 8), ("stops_total", 8), ("stops_as_ratio", 3)):
    K, F = total_ratio_from_label(kind, label)
    lit, sh = cast_shadow_pair(K, F, 0.0)
    d, cl, cs = dlstar(lit, sh, LIT_TARGET / lit)
    reads[kind] = (d, cs, lit / sh)
    print("  %-15s label %d -> total %.1f:1 (%.2f st) DeltaL* %.1f shadow code %d" % (kind, label, lit / sh, stops(lit / sh), d, cs))
check("P3a K:F vs total-lux reading are interchangeable at 8:1", abs(reads["KF_lux"][0] - reads["total_lux"][0]) < 3,
      "differ %.2f L*" % abs(reads["KF_lux"][0] - reads["total_lux"][0]))
check("P3b 8 stops (256:1) is a different look: crushed shadow", abs(reads["KF_lux"][0] - reads["stops_total"][0]) >= 20 and reads["stops_total"][1] < 8,
      "differ %.1f L*, shadow code %d" % (abs(reads["KF_lux"][0] - reads["stops_total"][0]), reads["stops_total"][1]))
check("P3c stops-count misread as ratio is also a different look", abs(reads["KF_lux"][0] - reads["stops_as_ratio"][0]) >= 10,
      "differ %.1f L*" % abs(reads["KF_lux"][0] - reads["stops_as_ratio"][0]))
# low ratio confusion: '1:1' K/F gives total 2:1 (1 stop), true total 1:1 means no key at all
lit, sh = cast_shadow_pair(1.0, 1.0, 0.0)
check("P3d 'near 1:1' as K:F still leaves 1 stop of shadow", abs(stops(lit / sh) - 1.0) < 1e-9, "K=F gives total %.1f:1" % (lit / sh))

# =========================================================== P4 geometry
print("\n[P4] nominal 8:1 K/F on a real face: cheek sites, Lambert cosines")
lit, sh = cheek_pair(8.0, 1.0, 0.0, 45, 0, -45, 0)
print("  45/45 rig: cheek lit/shadow = %.2f:1 (%.2f stops) vs nominal 8:1 (3 stops)" % (lit / sh, stops(lit / sh)))
check("P4a face contrast is far below nominal 8:1", 3.0 <= lit / sh <= 3.8, "%.2f:1" % (lit / sh))
rs = []
for az in range(20, 75, 10):
    l, s = cheek_pair(8.0, 1.0, 0.0, az, 0, -45, 0)
    rs.append(l / s)
    print("  key az %2d deg: cheek ratio %.2f:1 (%.2f st)" % (az, l / s, stops(l / s)))
check("P4b same nominal 8:1, key angle alone spreads face ratio >3x", max(rs) / min(rs) > 3.0, "%.2fx (%.2f..%.2f)" % (max(rs) / min(rs), min(rs), max(rs)))
p5, p95 = sphere_percentiles(8.0, 1.0, 0.0)
print("  whole-head P95/P05 at 8:1, key 45/20: %.1f:1 (%.1f st)" % (p95 / p5, stops(p95 / p5)))

# =========================================================== P5 ambient / bounce floor
print("\n[P5] ambient / bounce floor under a nominal 8:1 K/F (cast-shadow site)")
tot = {}
for A in (0.0, 1.0, 2.0):
    lit, sh = cast_shadow_pair(8.0, 1.0, A)
    tot[A] = lit / sh
    print("  A=%.1f (A/K=%.3f): total %.2f:1 = %.2f st" % (A, A / 8, lit / sh, stops(lit / sh)))
check("P5a A=K/8 loses ~0.85 st, A=K/4 ~1.3 st", abs(stops(tot[0.0]) - stops(tot[1.0]) - 0.85) < 0.03 and abs(stops(tot[0.0]) - stops(tot[2.0]) - 1.30) < 0.03,
      "lost %.2f and %.2f st" % (stops(tot[0.0]) - stops(tot[1.0]), stops(tot[0.0]) - stops(tot[2.0])))
cap = [(8 + a) / a for a in (0.5, 1.0, 2.0)]
l0, s0 = cast_shadow_pair(8.0, 0.0, 1.0)
check("P5b zero fill still capped by (K+A)/A", abs(l0 / s0 - 9.0) < 1e-9, "F=0, A=K/8 -> %.1f:1 not infinite; caps %s" % (l0 / s0, [round(c, 1) for c in cap]))
dd = []
for A in (0.0, 1.0, 2.0):
    lit, sh = cast_shadow_pair(8.0, 1.0, A)
    dd.append(dlstar(lit, sh, LIT_TARGET / lit)[0])
print("  DeltaL* by A: %s" % [round(x, 1) for x in dd])

# =========================================================== P6 fixed vs proportional ambient
print("\n[P6] BREAK: ambient independent of key (window/practical) vs proportional (bounce)")
fixed, prop = [], []
for b in range(-3, 4):
    K, F = 8 * 2.0 ** b, 1 * 2.0 ** b
    lit, sh = cast_shadow_pair(K, F, 1.0)
    fixed.append(lit / sh)
    lit, sh = cast_shadow_pair(K, F, 1.0 * 2.0 ** b)
    prop.append(lit / sh)
print("  fixed A   total ratio over -3..+3 st: %s" % [round(x, 2) for x in fixed])
print("  bounce A  total ratio over -3..+3 st: %s" % [round(x, 2) for x in prop])
check("P6a fixed ambient: brightness changes the ratio", max(fixed) / min(fixed) > 3.0, "%.2fx" % (max(fixed) / min(fixed)))
check("P6b proportional bounce: ratio brightness-independent", max(prop) / min(prop) < 1.0001, "%.4fx" % (max(prop) / min(prop)))
# same break seen in the image: normalised exposure, fixed ambient
dn = []
for b in (-3, 0, 3):
    K, F = 8 * 2.0 ** b, 2.0 ** b
    lit, sh = cast_shadow_pair(K, F, 1.0)
    dn.append(dlstar(lit, sh, LIT_TARGET / lit)[0])
print("  even with exposure normalised, fixed ambient DeltaL* at -3/0/+3 st: %s" % [round(x, 1) for x in dn])

# =========================================================== P7 tone curves
print("\n[P7] tone curve changes magnitude, not ordering")
tab = {}
for c in ("srgb", "gamma22", "filmic"):
    tab[c] = [dlstar(r, 1.0, LIT_TARGET / r, c)[0] for r in (2, 4, 8, 16)]
    print("  %-8s DeltaL* at 2/4/8/16:1 = %s" % (c, [round(x, 1) for x in tab[c]]))
order_ok = all(all(b > a for a, b in zip(v, v[1:])) for v in tab.values())
at8 = [v[2] for v in tab.values()]
check("P7a ratio ordering preserved by every curve", order_ok, "monotonic in all 3")
# PREDICTION MISS recorded on purpose: the guess was a >5 L* spread at 8:1, but all
# three curves happen to agree there (the S curve crosses the straight curves near 8:1).
miss = not (max(at8) - min(at8) > 5)
print("  PREDICTION MISS P7b: spread at 8:1 is %.1f L* (guessed >5); curves agree at 8:1 by coincidence" % (max(at8) - min(at8)))
ends = [max(v[i] for v in tab.values()) - min(v[i] for v in tab.values()) for i in (0, 3)]
check("P7c curve changes magnitude at the ends of the ladder (2:1 and 16:1)", min(ends) > 5, "spread %.1f L* at 2:1, %.1f L* at 16:1" % (ends[0], ends[1]))

# exposure normalisation mode: lit patch vs face mean
print("\n[P2c] exposure metered on face mean instead of lit patch")
dm = []
for r in (2, 8, 64):
    lit, sh = r, 1.0
    mean = 0.5 * (lit + sh)
    gain = 0.18 / mean
    d, cl, cs = dlstar(lit, sh, gain)
    dm.append((r, cl, round(d, 1)))
print("  (ratio, lit code, DeltaL*) with mean metering: %s" % dm)
print("  lit-patch metering gives DeltaL* %s" % [round(dlstar(r, 1.0, LIT_TARGET / r)[0], 1) for r in (2, 8, 64)])

# =========================================================== P9 encoded-space light mixing
print("\n[P9] fading the key to 50 percent: linear light vs averaging encoded codes")
lit_full, sh_n = LIT_TARGET, LIT_TARGET / 9.0   # 8:1 K/F, total 9:1, cast-shadow site
lin_half = lit_full * (0.5 * 8 + 1) / 9.0          # key at 50 percent, fill unchanged
enc_half = srgb_dec(0.5 * (srgb_enc(lit_full) + srgb_enc(sh_n)))
r_lin, r_enc = lin_half / sh_n, enc_half / sh_n
print("  linear half-key total ratio %.2f:1 ; encoded-space average %.2f:1 ; gap %.2f st" % (r_lin, r_enc, stops(r_lin) - stops(r_enc)))
check("P9 encoded-space mixing understates the ratio ~0.36 st", abs(r_lin - 5.0) < 1e-9 and 0.3 < stops(r_lin) - stops(r_enc) < 0.45,
      "gap %.2f st" % (stops(r_lin) - stops(r_enc)))

# =========================================================== verdict
passed = sum(checks)
print()
print("RESULT: %s %d/%d checks held, %d prediction miss (P7b); ratio sets contrast only with exposure normalised, a stated-in-lux ratio, a fixed key angle, no fixed ambient"
      % ("PASS" if all(checks) else "FAIL", passed, len(checks), 1 if miss else 0))
