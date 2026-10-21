# Virtual bass: does soft-clipping a sub add the 2nd-4th harmonics a phone speaker can play?
import math
FS, F0, N = 8000, 50.0, 8000          # 1 s, 1 Hz bins -> harmonics land on exact bins
def tone(drive, bias=0.0):
    out = []
    for i in range(N):
        x = drive * math.sin(2 * math.pi * F0 * i / FS) + bias
        y = x - x ** 3 / 3 if abs(x) <= 1 else math.copysign(2 / 3, x)
        out.append(y)
    m = sum(out) / N; return [v - m for v in out]          # remove DC
def amp(x, f):
    re = sum(v * math.cos(2 * math.pi * f * i / FS) for i, v in enumerate(x)); im = sum(v * math.sin(2 * math.pi * f * i / FS) for i, v in enumerate(x))
    return 2 * math.hypot(re, im) / N
def db(a, ref): return 20 * math.log10(max(a, 1e-12) / ref)
def report(name, x):
    a1 = amp(x, F0); h = [db(amp(x, F0 * k), a1) for k in (2, 3, 4)]
    print(f"{name}: H2 {h[0]:7.1f} dB  H3 {h[1]:7.1f} dB  H4 {h[2]:7.1f} dB (re fundamental)"); return h
res = []
s = report("1) symmetric soft clip, drive 1.5", tone(1.5))
res.append(s[0] < -80 and s[2] < -80 and s[1] > -40)          # odd only: no 2nd/4th
b = report("2) biased clip (+0.3 DC), drive 1.5", tone(1.5, .3))
res.append(b[0] > -30 and b[2] > -40)                         # bias creates even harmonics
r = [abs(math.sin(2 * math.pi * F0 * i / FS)) for i in range(N)]; m = sum(r) / N; r = [v - m for v in r]
# 3) full-wave rectifier: energy jumps to 2*F0 (fundamental cancels) -> an octave-up copy, not a richer sub
a2, a1 = amp(r, 2 * F0), amp(r, F0); print(f"3) full-wave rectify: F0 {a1:.4f}, 2F0 {a2:.4f}"); res.append(a1 < 1e-6 and a2 > .3)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" symmetric clip H2 {s[0]:.0f} dB H3 {s[1]:.0f} dB H4 {s[2]:.0f} dB (odd only); +0.3 bias H2 {b[0]:.0f} dB H4 {b[2]:.0f} dB; rectifier puts all energy at 2F0")
