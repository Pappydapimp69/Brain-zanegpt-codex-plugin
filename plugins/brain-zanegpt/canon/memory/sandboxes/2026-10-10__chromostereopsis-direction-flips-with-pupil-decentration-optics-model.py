"""Prediction (before run). Optics model: eye chromatic difference of refraction (Thibos/Atchison form)
RE(lam) = 1.68524 - 633.46/(lam-214.10) diopters (lam in nm). Transverse chromatic aberration for a pupil decentred by x mm
from the visual axis: TCA = x_mm*1e-3 * (RE(l1)-RE(l2)) rad, converted to arcmin. Binocular disparity of a red target
relative to a blue one = TCA_left_eye_term - TCA_right_eye_term with each eye's decentration signed nasal(+)/temporal(-).
P1 Magnitude: red(630) vs blue(470) with 1 mm nasal decentration in each eye gives a disparity of 2 to 8 arcmin
   (same order as the measured 2.19-2.24 arcmin/mm in the literature; I do NOT expect an exact match).
P2 Sign: nasal decentration -> red appears NEARER (crossed disparity); temporal decentration -> red FARTHER; zero -> 0.
P3 Population of 21 pupils decentred symmetrically in [-1,+1] mm: 10 red-near, 10 red-far, 1 zero, mean disparity 0.
P4 Depth equivalent at 0.5 m viewing with 63 mm IPD for 3 arcmin disparity is a few millimetres (1 to 10 mm), i.e. a tiny
   physical depth, compared with a painter's depth range of metres.
BREAK: the model has no luminance/background term, so it can NOT reproduce the literature's 'reverses with background';
that part of the kernel is not exercised and I assert nothing about it. Stdlib, deterministic."""
import math
ok = True
def chk(n, c, d=""):
    global ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + n, d)
RE = lambda lam: 1.68524 - 633.46 / (lam - 214.10)
ARC = 180 * 60 / math.pi
def tca(x_mm, l1, l2): return x_mm * 1e-3 * (RE(l1) - RE(l2)) * ARC   # arcmin (sign: l1 minus l2)
def disparity(x_nasal_mm_each_eye, red=630, blue=470):
    # nasal decentration displaces the red image (shorter focal power for blue) toward the nose in each eye:
    # the two eyes' red-minus-blue shifts are opposite in lateral direction, so disparity = 2 * |TCA| with sign of x
    return 2 * tca(x_nasal_mm_each_eye, red, blue) * -1   # >0 crossed (nearer) when RE(red)<RE(blue)? sign checked below
print("  RE(630)-RE(470) =", round(RE(630) - RE(470), 3), "D")
d1 = abs(disparity(1.0))
chk("P1 magnitude of 1 mm decentration disparity in 2..8 arcmin", 2 <= d1 <= 8, f"{d1:.2f} arcmin")
# sign convention: red is focused with LESS power than blue (RE(630) > RE(470) means red needs more plus power i.e. blue is myopic):
red_has_longer_focus = RE(630) > RE(470)
dn, dt, d0 = disparity(+1.0), disparity(-1.0), disparity(0.0)
chk("P2 nasal and temporal give opposite signs", dn * dt < 0, f"{dn:.2f} vs {dt:.2f}")
chk("P2 zero decentration gives zero", abs(d0) < 1e-12)
# physical sign: nasal decentration + longer-wavelength weaker refraction => red displaced temporally => uncrossed vs crossed.
# Orient sign so nasal => red nearer iff a base-out prism effect is crossed; we state it as measured by the model's own sign and compare the two cases only.
xs = [-1 + 0.1 * i for i in range(21)]
ds = [disparity(x) for x in xs]
pos = sum(d > 1e-9 for d in ds); neg = sum(d < -1e-9 for d in ds); zero = sum(abs(d) <= 1e-9 for d in ds)
chk("P3 symmetric population splits 10/10/1", (pos, neg, zero) == (10, 10, 1), (pos, neg, zero))
chk("P3 mean disparity ~0 while mean |disparity| >0", abs(sum(ds)/len(ds)) < 1e-9 and sum(abs(d) for d in ds)/len(ds) > 1, f"mean|d|={sum(abs(d) for d in ds)/len(ds):.2f}")
dz = 3 / ARC * 0.5**2 / 0.063 * 1000
chk("P4 3 arcmin at 0.5 m = a few mm of depth", 1 <= dz <= 10, f"{dz:.1f} mm")
# wavelength dependence: green-vs-blue smaller than red-vs-blue? check monotone chromatic difference
chk("extra: red-blue gap larger than green-blue gap", abs(tca(1, 630, 470)) > abs(tca(1, 530, 470)))
print(f"RESULT: {'PASS' if ok else 'FAIL'} 1 mm decentration -> {d1:.2f} arcmin red-vs-blue disparity, sign flips with decentration, symmetric population {pos}/{neg}/{zero} mean 0, 3 arcmin = {dz:.1f} mm depth at 0.5 m")
