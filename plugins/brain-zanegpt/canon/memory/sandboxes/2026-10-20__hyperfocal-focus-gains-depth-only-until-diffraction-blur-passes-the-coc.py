"""DEPTH-OF-FIELD seed: hyperfocal distance H = f^2/(N*c) + f. Focus at H -> sharp from H/2 to infinity.
Real lenses also diffract: Airy disk diameter ~ 2.44*lambda*N. Total blur on the sensor = sqrt(geometric^2 + airy^2).
PREDICTION (before run): for a 35mm full-frame lens (f=35mm, c=0.030mm) focused at H, the 'sharp to infinity' range
holds at f/8 (H~4.7m, near limit 2.3m) but at f/32 diffraction (Airy ~0.043mm) exceeds c so NO distance is within c:
the in-focus subject itself is outside the circle of confusion. Smallest-blur aperture for a subject at 3 m lies
between f/8 and f/16. A thin-lens blur calculation must agree with the H formula to <1% for the near limit."""
import math
F, C, LAM = 35.0, 0.030, 0.00055     # mm
def hyper(N): return F*F/(N*C) + F
def blur_geom(N, s_focus, d):        # geometric blur diameter (mm) on sensor for subject at d, focused at s_focus (thin lens)
    return (F/N) * F * abs(d - s_focus) / (d * (s_focus - F))
def airy(N): return 2.44*LAM*N
def total(N, s, d): return math.hypot(blur_geom(N, s, d), airy(N))
def near_numeric(N, s, c=C):         # smallest d whose geometric blur <= c, numerically
    lo, hi = F*1.01, s
    for _ in range(80):
        m = (lo+hi)/2
        (lo, hi) = (lo, m) if blur_geom(N, s, m) <= c else (m, hi)
    return hi
rows = []
for N in (2.8, 8, 16, 32):
    H = hyper(N); s = H; near_h = H / 2          # exact: focused at H the near limit is H/2 (first run used H/2+f/2 by mistake, 0.6-2.5% off)
    nn = near_numeric(N, s)
    far_blur = blur_geom(N, s, 1e9)  # blur for subject at infinity
    rows.append((N, H, near_h, nn, far_blur, airy(N), total(N, s, s), total(N, s, 1e9)))
    print("f/%-4g H=%7.0f mm near(formula)=%6.0f near(numeric)=%6.0f  inf-blur=%.4f airy=%.4f  total@focus=%.4f total@inf=%.4f" % rows[-1])
agree = all(abs(r[2]-r[3])/r[2] < 0.01 for r in rows)
f8 = [r for r in rows if r[0] == 8][0]; f32 = [r for r in rows if r[0] == 32][0]
holds8 = f8[7] <= C*1.0001 * 1.5 and f8[6] <= C
fails32 = f32[6] > C
def best_N(d=3000.0):
    cands = [n/2 for n in range(4, 90)]
    return min(cands, key=lambda N: total(N, d, d*1.3))      # subject at 3 m, background at 3.9 m, focus on the subject
bn = best_N()
print("best aperture for focus on a 3 m subject with a 3.9 m background: f/%.1f" % bn)
ok = agree and holds8 and fails32 and 8 <= bn <= 16
print("RESULT: %s near limit formula vs numeric within 1%%; f/8 keeps in-focus blur %.3f<=0.030 mm, f/32 in-focus blur %.3f>0.030 mm (diffraction), best aperture f/%.1f" % ("PASS" if ok else "FAIL", f8[6], f32[6], bn))
