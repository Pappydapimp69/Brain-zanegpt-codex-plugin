"""Blind rebuild of seven E81 (keep hallucination sway out of the 0.2-0.4 Hz
sickness band and off the full frame: 2 Hz jitter cut dose ~96%, 30% vignette
~70%). TOY MODEL of real people.
Own fixture: the ISO 2631-1 Wf motion-sickness frequency weighting, entered as
a table from memory (ASSUMED values, peak ~0.16-0.2 Hz), interpolated in
log-frequency. Dose for a sinusoidal sway = Wf(f) x the sway's ACCELERATION
amplitude (MSDV is built on weighted acceleration), scaled by the fraction of
the visual field that moves. The fork no claim states: what is held constant
when the designer switches frequency - (D) displacement amplitude (same pixels
of sway), (V) peak velocity, or (A) peak acceleration.
PREDICTION (before running): under V and A, 2 Hz cuts >= 90% vs 0.3 Hz;
under D (same pixel amplitude, the natural designer move) 2 Hz does NOT cut
>= 90% because acceleration grows with f^2; a 0.05 Hz drift cuts less than 2 Hz
jitter under A but MORE under D - i.e. the comparison flips with the convention.
Vignette leaving 30% of the frame moving cuts 70% under a linear-area dose; a
periphery-weighted dose (periphery counts 2x per area, ASSUMED) cuts more.
"""
import math, sys
print("python", sys.version.split()[0])
WF = [(0.05, 0.157), (0.063, 0.267), (0.08, 0.461), (0.1, 0.695), (0.125, 0.895),
      (0.16, 1.006), (0.2, 0.992), (0.25, 0.854), (0.315, 0.619), (0.4, 0.384),
      (0.5, 0.224), (0.63, 0.116), (0.8, 0.053), (1.0, 0.0235), (1.25, 0.00998),
      (1.6, 0.00377), (2.0, 0.00155), (2.5, 0.00064), (3.15, 0.00025), (4.0, 0.000097)]
def wf(f):
    for (f0, w0), (f1, w1) in zip(WF, WF[1:]):
        if f0 <= f <= f1:
            t = math.log(f/f0)/math.log(f1/f0); return math.exp(math.log(w0)+t*(math.log(w1)-math.log(w0)))
    raise ValueError(f)
def dose(f, conv):
    w = 2*math.pi*f
    acc = {"D": w*w, "V": w, "A": 1.0}[conv]
    return wf(f)*acc
cuts = {}
for conv in "DVA":
    b = dose(0.3, conv)
    cuts[conv] = {f: 1 - dose(f, conv)/b for f in (0.05, 0.1, 1.0, 2.0)}
    print(conv, {f: round(c, 3) for f, c in cuts[conv].items()})
c1 = cuts['V'][2.0] >= 0.9 and cuts['A'][2.0] >= 0.9
c2 = cuts['D'][2.0] < 0.9
flipA = cuts['A'][0.05] < cuts['A'][2.0]; flipD = cuts['D'][0.05] > cuts['D'][2.0]
lin = 1 - 0.30
# periphery-weighted: frame split 50% centre (weight 1), 50% periphery (weight 2);
# vignette masks the outer 70% of area = all periphery + 20% of the centre
tot = 0.5*1 + 0.5*2; left = 0.30*1
per = 1 - left/tot
print(f"vignette: linear-area cut {lin:.2f}, periphery-weighted cut {per:.2f}")
ok = c1 and c2 and flipA and flipD
print(f"RESULT: {'PASS' if ok else 'FAIL'} 2Hz cut D {cuts['D'][2.0]:.3f} V {cuts['V'][2.0]:.3f} A {cuts['A'][2.0]:.3f}; 0.05Hz cut D {cuts['D'][0.05]:.3f} A {cuts['A'][0.05]:.3f}; the claim's numbers hold only if velocity or acceleration is held, not pixel amplitude")
