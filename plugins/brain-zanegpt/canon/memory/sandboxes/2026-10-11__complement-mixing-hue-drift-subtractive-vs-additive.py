"""Sandbox (train gap, PAINTING colour-mixing kernel): complements neutralise but
shift hue while doing it. Toy spectral model, stdlib only, no RNG:
 wavelengths 400..700 step 10; three Gaussian observer sensitivities (toy, NOT CIE);
 pigment reflectances: a blue (Gaussian at 460) and oranges that are sigmoids with
 cutoff c (sweep 540..620). SUBTRACTIVE mix of weight t of the orange: reflectance =
 blue^(1-t) * orange^t per wavelength (multiplication, the 'mud' sibling kernel).
 ADDITIVE mix: linear-light average of the two stimuli's sensor responses.
 Colour = (R,G,B) sensor response under a flat illuminant. Chroma and hue angle are
 taken in an opponent plane (a=R-G, b=(R+G)/2-B) relative to the grey of the same lightness.
 Path hue drift = max |hue(t) - hue(0)| over the path from t=0 until chroma falls to 25%
 of the start. Reported per orange cutoff; minimum chroma reached on the path.
PREDICTION v1 (before first run; it FAILED, see Observed): (1) subtractive: hue drift depends strongly on the orange's cutoff;
there is a best cutoff (drift < 10 deg) and the worst sweep end drifts > 40 deg; (2) even the best
subtractive complement does NOT reach zero drift (> 1 deg), because the path is curved;
(3) additive mix of the blue with its best light complement (cutoff chosen to put the
line through grey) drifts < 1 deg since the path is a straight line; (4) BREAK: an
orange that is too far from complement never gets chroma below 25% of the start."""
import math
WL = list(range(400, 701, 10))
def gauss(x, mu, s): return math.exp(-0.5 * ((x - mu) / s) ** 2)
SENS = [[gauss(w, 600, 45) for w in WL], [gauss(w, 550, 45) for w in WL], [gauss(w, 450, 30) for w in WL]]
NORM = [sum(s) for s in SENS]
def sensors(refl): return [sum(r * s for r, s in zip(refl, S)) / n for S, n in zip(SENS, NORM)]
SIG = 35
def blue(): return [0.05 + 0.85 * gauss(w, 460, SIG) for w in WL]
def orange(c): return [0.05 + 0.85 / (1 + math.exp(-(w - c) / 12)) for w in WL]
def opp(rgb):
    R, G, B = rgb; return (R - G, (R + G) / 2 - B)
def chroma_hue(rgb):
    a, b = opp(rgb); return math.hypot(a, b), math.degrees(math.atan2(b, a))
def dh(h, h0): return abs((h - h0 + 180) % 360 - 180)

def sub_path(c, steps=600):
    B, O = blue(), orange(c)
    return [chroma_hue(sensors([bb ** (1 - t) * oo ** t for bb, oo in zip(B, O)])) for t in (i / steps for i in range(steps + 1))]

def drift(path, frac):
    c0, h0 = path[0]; d = 0.0; reach = False
    for c, h in path:
        if c < frac * c0: reach = True; break
        d = max(d, dh(h, h0))
    return d, reach

# v2 prediction (written after run 1, before run 2): with a NARROW saturated blue (sigma 20) and a deeper
# neutralisation target (10% of start chroma) the drift is larger than for sigma 35 at 25%, the best cutoff
# still leaves > 1 deg, and the spread between best and worst cutoff exceeds 5 deg.
cuts = list(range(540, 621, 5))
table = {}
for sig in (35, 20):
    SIG = sig
    for frac in (0.25, 0.10):
        r = {c: drift(sub_path(c), frac) for c in cuts}
        ok_c = [c for c in cuts if r[c][1]]
        best = min(ok_c, key=lambda c: r[c][0]); worst = max(ok_c, key=lambda c: r[c][0])
        table[(sig, frac)] = (best, r[best][0], worst, r[worst][0], len(cuts) - len(ok_c))
        print(f"blue sigma {sig}, neutralise to {frac:.0%}: best cutoff {best} drift {r[best][0]:.1f} deg, worst {worst} drift {r[worst][0]:.1f} deg, cutoffs that never get there {len(cuts) - len(ok_c)}/{len(cuts)}")

# additive contrast: if the second stimulus is built to be exactly opposite in sensor space the mixing path is a straight line through grey
SIG = 35
sb = sensors(blue()); g = sum(sb) / 3
opp_light = [2 * g - x for x in sb]
add = [chroma_hue([(1 - t) * x + t * y for x, y in zip(sb, opp_light)]) for t in (i / 200 for i in range(0, 101))]
add_drift = drift(add, 0.10)[0]
print(f"additive, light built exactly opposite in sensor space: drift {add_drift:.2f} deg (straight line through grey, true by construction)")

# v3 additions (predictions written before run 3), exercising the two sibling kernels:
#  (mud-is-multiplication) mixture chroma at t=0.5 falls as the second pigment's hue distance grows,
#    and narrow pigments (sigma 20) keep less chroma at distance than wide ones (sigma 35);
#  (rgb-are-not-subtractive-primaries) yellow + cyan-biased blue (peak 490) reaches higher peak
#    chroma than yellow + ultramarine-like blue (peak 440), along the mixing path.
def partner(peak, sig=35): return [0.05 + 0.85 * gauss(w, peak, sig) for w in WL]
def mix_chroma(P1, P2, t): return chroma_hue(sensors([x ** (1 - t) * y ** t for x, y in zip(P1, P2)]))[0]
SIG = 35
base = blue()
# run-3 fix: 'hue distance' is measured by the partner's spectral peak distance from the blue (460), not by complement-ness
ch = {pk: mix_chroma(base, partner(pk), 0.5) for pk in (480, 520, 560, 600)}
dist_fall = ch[480] > ch[520] > ch[560] > ch[600]
nw = {sg: mix_chroma(base, partner(560, sg), 0.5) for sg in (35, 20)}
narrow_worse = nw[20] < nw[35]
def peak_green(peak):
    Y = [0.05 + 0.85 / (1 + math.exp(-(w - 510) / 12)) for w in WL]
    Bp = partner(peak)
    return max(mix_chroma(Y, Bp, t / 100) for t in range(20, 81))
cyan_cleaner = peak_green(490) > peak_green(440)
print("mud kernel: mid-mix chroma vs partner peak distance " + ", ".join(f"{k}nm {v:.3f}" for k, v in ch.items()) + f"; falls monotonically {dist_fall}; narrow(20) {nw[20]:.3f} < wide(35) {nw[35]:.3f}: {narrow_worse}")
print(f"primaries kernel: interior peak chroma yellow+cyan-biased blue {peak_green(490):.3f} vs yellow+ultramarine-like blue {peak_green(440):.3f}: cyan cleaner {cyan_cleaner}")
a, b = table[(35, 0.25)], table[(20, 0.10)]
p_wide = b[3] > a[3]
p_best = all(v[1] > 1 for v in table.values())
p_spread = (b[3] - b[1]) > 5
print(f"v2 checks: narrower+deeper worst drift {b[3]:.1f} > {a[3]:.1f}: {p_wide}; best drift > 1 deg everywhere: {p_best}; spread {b[3]-b[1]:.1f} > 5 deg: {p_spread}; additive exact {add_drift < 0.5}")
ok = p_wide and p_best and p_spread and add_drift < 0.5 and dist_fall and narrow_worse and cyan_cleaner
print(f"RESULT: {'PASS' if ok else 'FAIL'} subtractive drift sigma35@25%: best {a[1]:.1f} worst {a[3]:.1f} deg; sigma20@10%: best {b[1]:.1f} worst {b[3]:.1f} deg; additive opposite {add_drift:.2f}; best>1deg {p_best}; dist_fall {dist_fall} narrow_worse {narrow_worse} cyan_cleaner {cyan_cleaner}")
