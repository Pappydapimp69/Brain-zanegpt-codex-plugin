"""Sandbox: is the mean synodic phase a proxy for the true new moon, and does the corrected function agree with an
INDEPENDENT ground truth? Ground truth here is NOT a recalled almanac table: it is the root of (moon longitude - sun
longitude) = 0 found by bisection, from a truncated Meeus ch.47 lunar series and a solar equation-of-center series.
Compared: (a) mean phase JDE0 = 2451550.09766 + 29.530588861 k; (b) dominant term only (-0.4072 sin M');
(c) the full ch.49 periodic-term correction. All in dynamical time (no delta-T needed for comparison).
PREDICTION (before first run), k = -1200..1200 (about 1903 to 2097):
  P1 mean phase max |error| between 9 and 14 hours;
  P2 dominant-term-only max |error| between 3 and 6 hours (kernel recalled 4.4 h);
  P3 full ch.49 max |error| < 5 minutes against the elongation root (kernel recalled 1.2 min vs almanac; my truncated
     longitude series limits this check to ~1-2 minutes, so 5 min is the bound that could fail);
  P4 break: dropping the E eccentricity factor and the 2nd-order terms (keeping only 4 terms) leaves > 3x the full error.
RUN 1 RESULT (recorded honestly): FAIL on P1 only -- mean-phase max error was 14.16 h, not 9-14 h; P2 (5.02 h), P3 (3.40 min) and
P4 (21.9 min) held. The kernel's "up to about 12 hours" is the max over 17 sampled moons, not a bound.
PREDICTION 2 (written after run 1, BEFORE run 2): the true bound is the sum of the periodic-term amplitudes (~0.63 d =
~15 h); so P1b: mean max error over 2401 lunations lies in [13, 15.2] h and is > 12 h, while a 17-moon sample drawn from
the kernel's years (k = 0, 8, 9.. spread) shows < 12.5 h; P1c: the error exceeds 12 h in at least 1% of lunations.
RUN 2 RESULT (recorded honestly): FAIL again -- the 17-moon spread sample reached 13.90 h (> my 12.5 h), and 10.1% of lunations
exceed 12 h; so the kernel's 11.9 h is a property of ITS 17 moons, not of the method.
PREDICTION 3 (written after run 2, BEFORE run 3): P1d: mean max in [13, 15.2] h; a spread 17-moon sample max in [11, 15] h;
the share of lunations above 12 h lies in [5%, 15%].
Stdlib only, deterministic, no RNG."""
import math
d2r = math.pi / 180
def sin(x): return math.sin(x * d2r)

def ch49(k, terms="full"):
    T = k / 1236.85
    jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * T * T - 0.00000015 * T**3 + 0.00000000073 * T**4
    if terms == "mean": return jde
    E = 1 - 0.002516 * T - 0.0000074 * T * T
    M = 2.5534 + 29.1053567 * k - 0.0000014 * T * T
    Mp = 201.5643 + 385.81693528 * k + 0.0107582 * T * T
    F = 160.7108 + 390.67050284 * k - 0.0016118 * T * T
    Om = 124.7746 - 1.56375588 * k + 0.0020672 * T * T
    if terms == "dominant": return jde - 0.4072 * sin(Mp)
    c = (-0.40720 * sin(Mp) + 0.17241 * E * sin(M) + 0.01608 * sin(2 * Mp) + 0.01039 * sin(2 * F)
         + 0.00739 * E * sin(Mp - M) - 0.00514 * E * sin(Mp + M) + 0.00208 * E * E * sin(2 * M)
         - 0.00111 * sin(Mp - 2 * F) - 0.00057 * sin(Mp + 2 * F) + 0.00056 * E * sin(2 * Mp + M)
         - 0.00042 * sin(3 * Mp) + 0.00042 * E * sin(M + 2 * F) + 0.00038 * E * sin(M - 2 * F)
         - 0.00024 * E * sin(2 * Mp - M) - 0.00017 * sin(Om))
    if terms == "four": c = -0.40720 * sin(Mp) + 0.17241 * sin(M) + 0.01608 * sin(2 * Mp) + 0.01039 * sin(2 * F)
    return jde + c

def moon_minus_sun(jde):
    T = (jde - 2451545.0) / 36525
    Lp = 218.3164477 + 481267.88123421 * T
    D = 297.8501921 + 445267.1114034 * T
    M = 357.5291092 + 35999.0502909 * T
    Mp = 134.9633964 + 477198.8675055 * T
    F = 93.2720950 + 483202.0175233 * T
    E = 1 - 0.002516 * T - 0.0000074 * T * T
    s = (6288774 * sin(Mp) + 1274027 * sin(2 * D - Mp) + 658314 * sin(2 * D) + 213618 * sin(2 * Mp)
         - 185116 * E * sin(M) - 114332 * sin(2 * F) + 58793 * sin(2 * D - 2 * Mp) + 57066 * E * sin(2 * D - M - Mp)
         + 53322 * sin(2 * D + Mp) + 45758 * E * sin(2 * D - M) - 40923 * E * sin(M - Mp) - 34720 * sin(D)
         - 30383 * E * sin(M + Mp) + 15327 * sin(2 * D - 2 * F) - 12528 * sin(Mp + 2 * F) + 10980 * sin(Mp - 2 * F)) / 1e6
    moon = Lp + s
    L0 = 280.46646 + 36000.76983 * T
    sun = L0 + (1.914602 - 0.004817 * T) * sin(M) + 0.019993 * sin(2 * M) + 0.000289 * sin(3 * M) - 0.00569
    x = (moon - sun) % 360
    return x - 360 if x > 180 else x

def root(guess):
    lo, hi = guess - 0.6, guess + 0.6
    flo = moon_minus_sun(lo)
    for _ in range(60):
        mid = (lo + hi) / 2
        fm = moon_minus_sun(mid)
        if (fm > 0) == (flo > 0): lo, flo = mid, fm
        else: hi = mid
    return (lo + hi) / 2

ks = range(-1200, 1201)
err = {m: 0.0 for m in ("mean", "dominant", "full", "four")}
rms_full = 0.0
for k in ks:
    r = root(ch49(k, "full"))
    for m in err:
        e = abs(ch49(k, m) - r) * 24
        err[m] = max(err[m], e)
        if m == "full": rms_full += e * e
rms_full = (rms_full / len(ks)) ** .5
print(f"max |error| hours vs elongation root over {len(ks)} lunations: " + ", ".join(f"{m}={v:.3f}" for m, v in err.items()) + f"; full rms={rms_full*60:.2f} min")
amp = (0.4072+0.17241+0.01608+0.01039+0.00739+0.00514+0.00208+0.00111+0.00057+0.00056+0.00042*2+0.00038+0.00024+0.00017)*24
sample = [-1200 + 141 * i for i in range(17)]
sm = max(abs(ch49(k, "mean") - root(ch49(k, "full"))) * 24 for k in sample)
frac12 = sum(abs(ch49(k, "mean") - root(ch49(k, "full"))) * 24 > 12 for k in ks) / len(ks)
print(f"amplitude sum bound={amp:.2f} h; 17-moon spread sample max={sm:.2f} h; share of lunations with mean error > 12 h = {frac12:.3f}")
p1 = 13 <= err["mean"] <= 15.2 and 11 <= sm <= 15 and 0.05 <= frac12 <= 0.15
p2 = 3 <= err["dominant"] <= 6
p3 = err["full"] * 60 < 5
p4 = err["four"] > 3 * err["full"]
print(f"P1={p1} P2={p2} P3={p3} P4={p4}")
print(f"RESULT: {'PASS' if all((p1,p2,p3,p4)) else 'FAIL'} mean max={err['mean']:.2f} h, dominant max={err['dominant']:.2f} h, "
      f"full ch49 max={err['full']*60:.2f} min (rms {rms_full*60:.2f}), four-term max={err['four']*60:.1f} min over k=-1200..1200")
