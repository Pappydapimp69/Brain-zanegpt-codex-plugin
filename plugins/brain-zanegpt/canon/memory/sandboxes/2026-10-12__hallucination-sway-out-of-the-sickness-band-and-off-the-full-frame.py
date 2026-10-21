"""Gap loop: visually induced motion sickness from hallucination distortion
(screen sway, warp, FOV pulsing). Which design choices cut the sickness dose?
Published inputs (research digest this session): visual-only oscillation is
most nauseating at 0.2-0.4 Hz and falls off above and below (Diels & Howarth
2013, Human Factors 55(3), abstract); the ISO 2631-1 / BS 6841 weighting for
body motion is flat 0.125-0.25 Hz, about -6 dB/octave below and -12 dB/octave
above; sickness and presence rise with the moving field of view (Lin et al.
2002); Xbox Accessibility Guideline 117 says avoid repetitive on-screen sway or
make it optional (page read).
ASSUMED model: dose ~ W(f) * amplitude * moving-field fraction * sqrt(duration),
with W flat over 0.2-0.4 Hz, -6 dB/octave below and -12 dB/octave above (the
ISO shape moved to the visual band). Exact arithmetic, no RNG.
PREDICTION (written before running): moving a 0.3 Hz full-frame sway to 2 Hz
cuts the dose by at least 90%; confining it to a 30% vignette cuts it by at
least 60%; a 0.05 Hz 'slow drift' cuts it by less than the 2 Hz version; an
opt-out (prefers-reduced-motion style) for the 30% of players who are
susceptible cuts their dose to 0.
"""
import math


def weight(f):
    if 0.2 <= f <= 0.4:
        return 1.0
    if f < 0.2:
        octaves = math.log2(0.2 / f)
        return 10 ** (-6 * octaves / 20)
    octaves = math.log2(f / 0.4)
    return 10 ** (-12 * octaves / 20)


def dose(f, amp=1.0, field=1.0, secs=60.0):
    return weight(f) * amp * field * math.sqrt(secs)


def main():
    ref = dose(0.3)
    cases = {
        "full-frame sway 0.3 Hz (reference)": dose(0.3),
        "full-frame slow drift 0.05 Hz": dose(0.05),
        "full-frame jitter 2 Hz": dose(2.0),
        "vignette-only (30% of field) 0.3 Hz": dose(0.3, field=0.3),
        "vignette-only jitter 2 Hz": dose(2.0, field=0.3),
    }
    for k, v in cases.items():
        print(f"{k:38s}: relative dose {v / ref:.3f}")
    cut2 = 1 - cases["full-frame jitter 2 Hz"] / ref
    cutv = 1 - cases["vignette-only (30% of field) 0.3 Hz"] / ref
    cutslow = 1 - cases["full-frame slow drift 0.05 Hz"] / ref
    checks = [
        (f"2 Hz instead of 0.3 Hz cuts the dose >= 90% (got {cut2:.0%})", cut2 >= 0.90),
        (f"a 30% vignette cuts the dose >= 60% (got {cutv:.0%})", cutv >= 0.60),
        (f"break case: a 0.05 Hz slow drift cuts less than 2 Hz jitter ({cutslow:.0%} vs {cut2:.0%})", cutslow < cut2),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; relative doses "
          + "; ".join(f"{k.split(' (')[0]} {v / ref:.3f}" for k, v in cases.items()))


if __name__ == "__main__":
    main()
