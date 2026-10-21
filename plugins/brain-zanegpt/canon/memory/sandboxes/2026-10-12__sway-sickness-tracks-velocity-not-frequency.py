"""Gap pass: seven E83 (replace breathing sway with a slow 6 s+ swell), E81/E85 (leave the 0.2-0.4 Hz band;
2 Hz jitter cuts dose 85-98%) both rank sway designs by FREQUENCY. Chen, Bao, Zhao & So 2016 (Ergonomics
59:4; fore-and-aft visual oscillation) found that with rms VELOCITY held constant VIMS was flat from
0.05 to 0.8 Hz, and with AMPLITUDE held constant nausea rose with frequency to a peak that moved up as
amplitude fell (0.2 Hz at 100 m, 0.8 at 25 m, 3.2 at 6.25 m); Diels & Howarth 2013 found 0.2-0.4 Hz.
Deterministic comparison of candidate designs (amplitude in degrees of whole-frame sway):
  breath   0.25 Hz, 3.0 deg       (E83's problem case)
  swell    0.15 Hz, 3.0 deg       (E83's fix: same amplitude, slower)
  swellbig 0.15 Hz, 6.0 deg       (a swell sized to read as strongly as the breath)
  jitter   2.0 Hz, 1.0 deg        (E85's fix)
  microjit 2.0 Hz, 0.2 deg
  edge     breath on a 30% edge ring (area 0.3)
Model A (frequency band, E81/E85-style): dose = area x band(f), band = 1 in 0.2-0.4 Hz, falling 12 dB/octave outside.
Model B (velocity, Chen Type A): dose = area x rms angular velocity = area x 2*pi*f*A/sqrt(2).
Predictions written before running:
 P1 model A ranks jitter (1 deg) as safer than breath; model B ranks it MORE provocative than breath.
 P2 under model B the E83 slow swell at equal amplitude halves-or-better the breath's dose (it is slower)
    but a swell sized to read as strongly (6 deg) is within 25% of the breath.
 P3 under model B a jitter must be <= 0.4 deg to dose no more than the breath.
 P4 the edge ring cuts dose by the same 70% in both models (area acts independently of the frequency question).
"""
import math

D = {"breath": (0.25, 3.0, 1.0), "swell": (0.15, 3.0, 1.0), "swellbig": (0.15, 6.0, 1.0),
     "jitter": (2.0, 1.0, 1.0), "microjit": (2.0, 0.2, 1.0), "edge": (0.25, 3.0, 0.3)}

def band(f):
    if 0.2 <= f <= 0.4: return 1.0
    octs = math.log2(0.2 / f) if f < 0.2 else math.log2(f / 0.4)
    return 10 ** (-12 * octs / 20)

def vel(f, a): return 2 * math.pi * f * a / math.sqrt(2)

A = {k: ar * band(f) for k, (f, a, ar) in D.items()}
B = {k: ar * vel(f, a) for k, (f, a, ar) in D.items()}
for k in D:
    print(f"{k:9s} f={D[k][0]:<5} amp={D[k][1]:<4} area={D[k][2]:<4}  model A dose {A[k]:.3f}   model B rms deg/s {B[k]:.2f}  (vs breath {B[k]/B['breath']:.2f}x)")
jit_max = B["breath"] * math.sqrt(2) / (2 * math.pi * 2.0)
print(f"largest 2 Hz jitter amplitude dosing no more than breath under B: {jit_max:.3f} deg")
p1 = A["jitter"] < A["breath"] and B["jitter"] > B["breath"]
p2 = B["swell"] <= 0.5 * B["breath"] and abs(B["swellbig"] / B["breath"] - 1) <= 0.25
p3 = jit_max <= 0.4
p4 = abs(A["edge"] / A["breath"] - 0.3) < 1e-9 and abs(B["edge"] / B["breath"] - 0.3) < 1e-9
checks = [("P1 models disagree on jitter vs breath", p1), ("P2 slow swell helps only at equal amplitude", p2),
          ("P3 jitter must be <= 0.4 deg", p3), ("P4 edge ring cuts 70% in both", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; model B vs breath: swell {B['swell']/B['breath']:.2f}x, swellbig {B['swellbig']/B['breath']:.2f}x, "
      f"jitter1deg {B['jitter']/B['breath']:.2f}x, microjitter {B['microjit']/B['breath']:.2f}x; model A jitter {A['jitter']:.3f} vs breath {A['breath']:.3f}; jitter cap {jit_max:.3f} deg")
