"""Chiptune kernel: with too few voices, drop the chord's FIFTH before its THIRD. Two claimed reasons:
(1) the third carries major vs minor, the fifth doesn't; (2) the fifth is largely redundant. Test both with a
harmonic model: each note = partials 1..10 at 1/n amplitude (a square-ish chip voice keeps odd ones, also tested).
Deterministic, stdlib only."""
import math
def partials(midi, odd_only=False):
    f = 440 * 2 ** ((midi - 69) / 12)
    return [(f * n, 1 / n) for n in range(1, 11) if not odd_only or n % 2]
def spectrum(notes, odd_only=False, cents=25):
    bins = {}
    for m in notes:
        for fr, a in partials(m, odd_only):
            b = round(1200 * math.log2(fr / 55) / cents); bins[b] = bins.get(b, 0) + a
    return bins
def cos(a, b):
    ks = set(a) | set(b); dot = sum(a.get(k, 0) * b.get(k, 0) for k in ks)
    return dot / math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
def implied(root, interval, odd_only=False, tol=20):
    """energy the ROOT's own partials put on the pitch class INTERVAL semitones above it (any octave)"""
    e = 0
    for fr, a in partials(root, odd_only):
        c = (1200 * math.log2(fr / (440 * 2 ** ((root - 69) / 12)))) % 1200
        if min(abs(c - interval * 100), 1200 - abs(c - interval * 100)) < tol: e += a * a
    return e
R = 60
res = {}
for odd in (False, True):
    tag = 'square-ish (odd partials)' if odd else 'all partials'
    fi, mj, mn = implied(R, 7, odd), implied(R, 4, odd), implied(R, 3, odd)
    dist_third = 1 - cos(spectrum([R, R + 4], odd), spectrum([R, R + 3], odd))
    res[odd] = (fi, mj, mn, dist_third)
    print(f"{tag}: the root alone sounds the fifth at {fi:.3f}, the major third at {mj:.3f}, the minor third at {mn:.3f} (energy); "
          f"major vs minor apart with root+third {dist_third:.2f}, with root+fifth 0.00")
ok = all(res[o][0] > 2 * res[o][1] and res[o][2] == 0 and res[o][3] > .2 for o in res)
print(f"RESULT: {'PASS' if ok else 'FAIL'} in both timbres the root's own overtones sound the fifth {res[False][0]/res[False][1]:.1f}x (square {res[True][0]/res[True][1]:.1f}x) as strongly as the major third and never the minor third; root+fifth loses major/minor entirely, so drop the fifth, and a minor third is the one tone nothing else supplies")
