"""Sandbox: does a teal-orange grade separate skin from background?  stdlib only, no RNG, no timing.

PREDICTIONS (written BEFORE the first run):
 P1 dark backdrop (L=0.30,C=0.08, 12 hues x 10 skins = 120 pairs): luminance-split grade G1 raises
    chromatic separation dEab in >= 70% of pairs.
 P2 matched-luminance backdrop (bg L = skin L): G1 is an additive shift with the same weight on both
    sides, so median |gain| in dEab is < 0.5 (OKLab x100) -> it cannot rescue an orange backdrop lit like the skin.
 P3 hue-curve grade G2 (pull each hue toward nearer of orange/teal anchor): mean gain > 0 for backdrop hues
    150..270 deg and mean gain < 0 for backdrop hues 0..120 deg (orange-side backgrounds get LESS separated).
 P4 skin fidelity under G1: the darkest skin tone (L<0.35) shifts hue >= 30 deg while the lightest shifts < 15 deg.
 P5 deutan CVD: median retention (dEab_sim/dEab_normal) after G1 >= 0.5 for teal-ish backdrops (hue 170..230)
    and < 0.35 for green/red-ish backdrops (hue 0..30 and 120..160) on the dark backdrop.
 P6 grade gain is chromatic only (L untouched): median deutan gain / median normal gain < 0.7 on the dark backdrop.

RUN 1 OBSERVED (before the post-hoc block existed; backdrops were NOT yet gamut-clipped, a method flaw fixed in run 2 -
 the matched/saturated backdrops at high L fell outside sRGB, so run-1 numbers for S2/S3/S9 are contaminated): P1 FAIL (0.19 improved), P2 held, P3 FAIL, P4 FAIL (28 vs 30 deg),
 P5 FAIL (0.39 vs 0.35 bound), P6 FAIL (median normal gain is <= 0 so the ratio is meaningless). Held 1/6.
POST-HOC predictions (written AFTER run 1, from what it showed; labelled so they are not mistaken for blind ones):
 H1 before any grade, at matched luminance and C=0.08, median-skin separation peaks at a backdrop hue in 225..270 and
    the teal anchor (195) reaches < 95% of that peak (the OKLab complement of skin is blue, not teal).
 H2 raising grade strength s from 0.03 to 0.10 lifts the improved share on the dark backdrop above 40% but pushes
    >= 3 of 10 skin tones off the original skin hue range (+-5 deg).
 H3 moving the hue-curve teal anchor from 195 to 250 turns the G2 mean matched-L gain positive over backdrop hues 150..300.
 H4 at s=0.03 on the dark backdrop, light skins (L>0.8) improve (>1 unit) in >= 50% of pairs, dark skins (L<0.45) in < 20%.
"""
import math

# ---------- colour maths ----------
def s2l(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def l2s(c):
    c = max(0.0, min(1.0, c))
    return 255.0 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)
def lin2ok(r, g, b):
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l, m, s = (math.copysign(abs(x) ** (1/3), x) for x in (l, m, s))
    return (0.2104542553*l + 0.7936177850*m - 0.0040720468*s,
            1.9779984951*l - 2.4285922050*m + 0.4505937099*s,
            0.0259040371*l + 0.7827717662*m - 0.8086757660*s)
def ok2lin(L, a, b):
    l = (L + 0.3963377774*a + 0.2158037573*b) ** 3
    m = (L - 0.1055613458*a - 0.0638541728*b) ** 3
    s = (L - 0.0894841775*a - 1.2914855480*b) ** 3
    return (4.0767416621*l - 3.3077115913*m + 0.2309699292*s,
            -1.2684380046*l + 2.6097574011*m - 0.3413193965*s,
            -0.0041960863*l - 0.7034186147*m + 1.7076147010*s)
def hex2ok(h):
    return lin2ok(*(s2l(int(h[i:i+2], 16)) for i in (1, 3, 5)))
def lch(L, C, h):
    return (L, C*math.cos(math.radians(h)), C*math.sin(math.radians(h)))
def hue(a, b):
    return math.degrees(math.atan2(b, a)) % 360
def wrap(d):
    return (d + 180) % 360 - 180
def dE(p, q):
    return 100*math.sqrt(sum((x-y)**2 for x, y in zip(p, q)))
def dEab(p, q):
    return 100*math.hypot(p[1]-q[1], p[2]-q[2])
clipcount = [0]
bg_clips = [0]
def clip_gamut(ok):
    lin = ok2lin(*ok)
    if any(x < -1e-6 or x > 1+1e-6 for x in lin):
        clipcount[0] += 1
    lin = tuple(max(0.0, min(1.0, x)) for x in lin)
    return lin2ok(*lin)
# Vienot 1999 style dichromat matrices in LINEAR sRGB (rows sum to 1, white preserved: checked below)
DEUT = ((0.29275, 0.70725, 0.0), (0.29275, 0.70725, 0.0), (-0.02234, 0.02234, 1.0))
PROT = ((0.10889, 0.89111, 0.0), (0.10889, 0.89111, 0.0), (0.00447, -0.00447, 1.0))
def cvd(ok, M):
    lin = ok2lin(*ok)
    lin = tuple(max(0.0, min(1.0, x)) for x in lin)
    out = tuple(sum(M[i][j]*lin[j] for j in range(3)) for i in range(3))
    return lin2ok(*out)
def wcag_lum(ok):
    r, g, b = (max(0.0, min(1.0, x)) for x in ok2lin(*ok))
    return 0.2126*r + 0.7152*g + 0.0722*b

# ---------- data (illustrative swatches typed for this test; NOT a measured skin dataset) ----------
SKIN = ["#f6ede4", "#f3e7db", "#f7ead0", "#eadaba", "#d7bd96", "#a07e56", "#825c43", "#604134", "#3a312a", "#292420"]
skin_ok = [hex2ok(h) for h in SKIN]
HUES = list(range(0, 360, 30))
SKIN_H = [hue(p[1], p[2]) for p in skin_ok]
SKIN_HLO, SKIN_HHI = min(SKIN_H), max(SKIN_H)

# ---------- grades ----------
TEAL, ORANGE = 195.0, 55.0     # OKLab hue anchors
def smooth(x):
    x = max(0.0, min(1.0, x)); return x*x*(3-2*x)
def G0(ok): return ok
def G1(ok, s=0.03):
    """luminance-split tint: shadows -> teal, highlights -> orange (additive in OKLab a,b)"""
    L, a, b = ok
    ws, wh = smooth((0.5-L)/0.5), smooth((L-0.5)/0.5)
    ta, tb = math.cos(math.radians(TEAL)), math.sin(math.radians(TEAL))
    oa, ob = math.cos(math.radians(ORANGE)), math.sin(math.radians(ORANGE))
    return clip_gamut((L, a + s*(ws*ta + wh*oa), b + s*(ws*tb + wh*ob)))
def G2(ok, k=0.4, TEAL=TEAL):
    """hue-curve grade: rotate each hue a fraction k toward the nearer of the two anchors"""
    L, a, b = ok
    C, h = math.hypot(a, b), hue(a, b)
    if C < 1e-4: return ok
    d_o, d_t = wrap(ORANGE-h), wrap(TEAL-h)
    d = d_o if abs(d_o) <= abs(d_t) else d_t
    return clip_gamut(lch(L, C, h + k*d))

def sweep(bg_fn, grade, sim=None):
    """returns list of (skin_idx, bg_hue, before, after) using dEab"""
    out = []
    for i, sk in enumerate(skin_ok):
        for bh in HUES:
            c_ = clipcount[0]; bg = clip_gamut(bg_fn(sk, bh)); bg_clips[0] += clipcount[0]-c_; clipcount[0] = c_
            b0, a0 = (sk, bg), (grade(sk), grade(bg))
            if sim:
                b0 = (cvd(sk, sim), cvd(bg, sim)); a0 = (cvd(a0[0], sim), cvd(a0[1], sim))
            out.append((i, bh, dEab(*b0), dEab(*a0), dE(*b0), dE(*a0)))
    return out
def med(x):
    x = sorted(x); n = len(x); return x[n//2] if n % 2 else 0.5*(x[n//2-1]+x[n//2])
def frac_improved(rows, thr=1.0): return sum(1 for r in rows if r[3]-r[2] > thr)/len(rows)

dark = lambda sk, bh: lch(0.30, 0.08, bh)
mid = lambda sk, bh: lch(0.55, 0.08, bh)
matched = lambda sk, bh: lch(sk[0], 0.08, bh)
satlit = lambda sk, bh: lch(0.75, 0.15, bh)
checks = {}

# sanity: roundtrip + white preserved
rt = max(abs(x-y) for x, y in zip(ok2lin(*lin2ok(0.2, 0.5, 0.7)), (0.2, 0.5, 0.7)))
wp = [sum(r) for r in DEUT]+[sum(r) for r in PROT]
print("sanity roundtrip err %.2e, matrix row sums %s" % (rt, [round(x, 3) for x in wp]))
print("skin OKLab L:", [round(p[0], 2) for p in skin_ok])
print("skin OKLab hue:", [round(h) for h in SKIN_H], " chroma:", [round(math.hypot(p[1], p[2]), 3) for p in skin_ok])

# S1 dark backdrop
R1 = sweep(dark, G1)
checks["P1"] = frac_improved(R1) >= 0.70
print("S1 dark bg G1: improved(>1 unit) %.2f  median before %.1f after %.1f" % (frac_improved(R1), med([r[2] for r in R1]), med([r[3] for r in R1])))
print("   full dE (incl. luminance) median before %.1f after %.1f ; grade moves it by %+.2f median" % (med([r[4] for r in R1]), med([r[5] for r in R1]), med([r[5]-r[4] for r in R1])))
byh = {bh: sum(r[3]-r[2] for r in R1 if r[1] == bh)/10 for bh in HUES}
print("   mean gain by bg hue:", {h: round(v, 1) for h, v in byh.items()})
# S1b mid backdrop
R1b = sweep(mid, G1)
print("S1b mid bg (L .55) G1: improved %.2f median gain %.2f" % (frac_improved(R1b), med([r[3]-r[2] for r in R1b])))
# S2 matched luminance
R2 = sweep(matched, G1)
mg = med([abs(r[3]-r[2]) for r in R2])
checks["P2"] = mg < 0.5
print("S2 matched-L bg G1: median |gain| %.3f max |gain| %.2f (gamut clips so far %d)" % (mg, max(abs(r[3]-r[2]) for r in R2), clipcount[0]))
# S3 G2 hue curve, per-hue gain, dark and matched
R3 = sweep(matched, G2)
g3 = {bh: sum(r[3]-r[2] for r in R3 if r[1] == bh)/10 for bh in HUES}
print("S3 G2 hue-curve matched-L, mean gain by bg hue:", {h: round(v, 1) for h, v in g3.items()})
lo = [g3[h] for h in HUES if 0 <= h <= 120]; hi = [g3[h] for h in HUES if 150 <= h <= 270]
checks["P3"] = (sum(lo)/len(lo) < 0 and sum(hi)/len(hi) > 0)
print("   mean gain hues 0-120: %.2f ; hues 150-270: %.2f" % (sum(lo)/len(lo), sum(hi)/len(hi)))
# S4 BREAK: saturated lit orange/teal backdrops
R4 = sweep(satlit, G1); R4b = sweep(satlit, G2)
for nm, rr in (("G1", R4), ("G2", R4b)):
    for bh in (30, 60, 90, 180, 210):
        g = [r[3]-r[2] for r in rr if r[1] == bh]; b = [r[2] for r in rr if r[1] == bh]; a = [r[3] for r in rr if r[1] == bh]
        print("S4 satlit %s bg hue %3d: median dEab before %.1f after %.1f gain %+.1f" % (nm, bh, med(b), med(a), med(g)))
# S5 skin fidelity
print("S5 skin fidelity G1 / G2 (hue shift deg, dE shift, in-locus?)")
shifts = []
for i, sk in enumerate(skin_ok):
    for nm, g in (("G1", G1), ("G2", G2)):
        s2 = g(sk); dh = wrap(hue(s2[1], s2[2])-SKIN_H[i]); h2 = hue(s2[1], s2[2])
        inloc = SKIN_HLO-5 <= h2 <= SKIN_HHI+5
        if nm == "G1": shifts.append((sk[0], abs(dh)))
        print("   skin%d L%.2f %s dh %+6.1f dE %.2f hue_after %3.0f in-locus %s" % (i, sk[0], nm, dh, dE(sk, s2), h2, inloc))
dark_sk = [abs(h) for L, h in shifts if L < 0.35]; light_sk = [abs(h) for L, h in shifts if L > 0.9]
checks["P4"] = min(dark_sk) >= 30 and max(light_sk) < 15
print("   G1 dark-skin(L<.35) |dh| %s ; lightest(L>.9) |dh| %s" % ([round(x) for x in dark_sk], [round(x) for x in light_sk]))
# S6 CVD
for nm, M in (("deutan", DEUT), ("protan", PROT)):
    RC = sweep(dark, G1, sim=M)
    ret = {bh: med([r[3]/r[2] if r[2] > 1e-6 else 0 for r in R1 if r[1] == bh]) for bh in HUES}
    retc = {bh: med([r[3]/ r0[3] if r0[3] > 1e-6 else 0 for r, r0 in zip(RC, R1) if r[1] == bh]) for bh in HUES}
    gainN = med([r[3]-r[2] for r in R1]); gainC = med([r[3]-r[2] for r in RC])
    print("S6 %s dark bg: median gain normal %.2f sim %.2f ; retention (after_sim/after_normal) by bg hue:" % (nm, gainN, gainC), {h: round(v, 2) for h, v in retc.items()})
    if nm == "deutan":
        tl = [retc[h] for h in (180, 210)]; gr = [retc[h] for h in (0, 30, 120, 150)]
        checks["P5"] = (med(tl) >= 0.5 and med(gr) < 0.35)
        print("   teal-ish(180,210) median retention %.2f ; red/green-ish(0,30,120,150) %.2f" % (med(tl), med(gr)))
        checks["P6"] = (gainC/gainN < 0.7) if gainN > 0 else False
        print("   gain ratio sim/normal %.2f" % (gainC/gainN))
        # luminance survival: WCAG luminance gap skin vs dark bg unchanged by grade?
        lg0 = med([abs(wcag_lum(sk)-wcag_lum(dark(sk, 0))) for sk in skin_ok])
        lg1 = med([abs(wcag_lum(G1(sk))-wcag_lum(G1(dark(sk, 0)))) for sk in skin_ok])
        print("   WCAG luminance gap skin-vs-dark-bg before %.3f after G1 %.3f (grade adds no luminance axis)" % (lg0, lg1))

post = {}
# S7 static hue-separation curve (no grade), matched L, C=0.08
curve = {bh: med([dEab(sk, lch(sk[0], 0.08, bh)) for sk in skin_ok]) for bh in range(0, 360, 15)}
pk = max(curve, key=curve.get)
print("S7 pre-grade separation vs bg hue (median skin, matched L, C .08):", {h: round(v, 1) for h, v in curve.items()})
print("   peak hue %d value %.1f ; teal(195) %.1f = %.0f%% of peak ; orange(60) %.1f" % (pk, curve[pk], curve[195], 100*curve[195]/curve[pk], curve[60]))
post["H1"] = 225 <= pk <= 270 and curve[195]/curve[pk] < 0.95
# S8 strength sweep, dark bg
off = {}
for s in (0.03, 0.06, 0.10):
    c0 = clipcount[0]
    Rs = sweep(dark, lambda o, s=s: G1(o, s))
    nOff = 0
    for i, sk in enumerate(skin_ok):
        h2 = hue(*G1(sk, s)[1:])
        if not (SKIN_HLO-5 <= h2 <= SKIN_HHI+5): nOff += 1
    off[s] = nOff
    print("S8 strength %.2f dark bg: improved %.2f median gain %+.2f ; skins off hue-range %d/10 ; clips +%d" % (s, frac_improved(Rs), med([r[3]-r[2] for r in Rs]), nOff, clipcount[0]-c0))
    if s == 0.10: f10 = frac_improved(Rs)
post["H2"] = f10 > 0.40 and off[0.10] >= 3
# S9 anchor move
for ta in (195.0, 250.0):
    Rg = sweep(matched, lambda o, ta=ta: G2(o, 0.4, ta))
    gg = {bh: sum(r[3]-r[2] for r in Rg if r[1] == bh)/10 for bh in HUES}
    rng = [gg[h] for h in HUES if 150 <= h <= 300]
    print("S9 G2 teal anchor %d matched-L mean gain bg hues 150-300: %+.2f ; all-hue mean %+.2f" % (ta, sum(rng)/len(rng), sum(gg.values())/12))
    if ta == 250.0: post["H3"] = sum(rng)/len(rng) > 0
# S10 by skin lightness
def share(sel):
    rr = [r for r in R1 if sel(skin_ok[r[0]][0])]
    return frac_improved(rr), len(rr)
sl, nl = share(lambda L: L > 0.8); sd, nd = share(lambda L: L < 0.45)
print("S10 G1 s=.03 dark bg improved share: light skins (L>.8) %.2f (n=%d), dark skins (L<.45) %.2f (n=%d)" % (sl, nl, sd, nd))
post["H4"] = sl >= 0.5 and sd < 0.2
print("post-hoc:", post)
print("grade-induced clipped colours:", clipcount[0], " backdrop colours that needed gamut clipping before grading:", bg_clips[0])
fails = sorted(k for k, v in checks.items() if not v)
print("checks:", {k: checks[k] for k in sorted(checks)})
pf = sorted(k for k, v in post.items() if not v)
allf = fails + pf
print("RESULT: %s blind predictions held=%d/6 (failed %s); post-hoc held=%d/4 (failed %s)" % ("PASS" if not allf else "FAIL", 6-len(fails), ",".join(fails) or "none", 4-len(pf), ",".join(pf) or "none"))
