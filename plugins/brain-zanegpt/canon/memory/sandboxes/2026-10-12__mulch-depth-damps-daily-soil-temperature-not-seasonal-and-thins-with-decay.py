"""Prediction (before first run): a 1-D heat-conduction model (implicit finite volume, no RNG) with a mulch layer of depth d over soil,
air temperature a sinusoid, gives for the DAILY cycle (10 C amplitude) an amplitude 5 cm below the soil surface that falls monotonically with d:
bare ~2.6 C, 2 in mulch below 1 C, 4 in below 0.3 C, and the saving from 4 to 8 in is under 0.3 C (flat returns, consistent with the recorded water-saving
flatness past 4 in). For the ANNUAL cycle (15 C amplitude) the same 4 in layer cuts the 5 cm amplitude by under 15 percent, so the kernel's
'moderates temperature' claim is a daily-swing claim. Decay from 4 to 2 in (recorded wood chips under 2 in at month 24) roughly doubles the daily amplitude at 5 cm. 
BREAK: the annual run, where depth should barely matter. Assumed properties: mulch k=0.12 W/mK, C=0.6e6 J/m3K; soil k=1.0, C=2.0e6."""
import math
IN = 0.0254
K = {"mulch": 0.12, "soil": 1.0}
C = {"mulch": 0.6e6, "soil": 2.0e6}

def amplitude(d_in, period, amp_air, dx, dt, cycles, probe=0.05, depth=1.2 if False else None):
    dm = d_in * IN
    zmax = 3.0 if period > 1e6 else 0.6
    nm = round(dm / dx); ns = round(zmax / dx)
    n = nm + ns
    kk = [K["mulch"]] * nm + [K["soil"]] * ns
    cc = [C["mulch"]] * nm + [C["soil"]] * ns
    # conductance between nodes i,i+1 (harmonic mean); node 0 is driven by air through half cell
    g = [2 * kk[i] * kk[i + 1] / (kk[i] + kk[i + 1]) / dx for i in range(n - 1)]
    g0 = kk[0] / (dx / 2)
    T = [15.0] * n
    steps_per = int(period / dt); probe_i = nm + round(probe / dx)
    rec = []
    for s in range(steps_per * cycles):
        tair = 15.0 + amp_air * math.sin(2 * math.pi * (s + 1) * dt / period)
        a = [0.0] * n; b = [0.0] * n; c = [0.0] * n; r = [0.0] * n
        for i in range(n):
            cap = cc[i] * dx / dt
            lo = g[i - 1] if i > 0 else 0.0
            hi = g[i] if i < n - 1 else 0.0
            top = g0 if i == 0 else 0.0
            a[i] = -lo; c[i] = -hi; b[i] = cap + lo + hi + top
            r[i] = cap * T[i] + top * tair
        for i in range(1, n):          # Thomas algorithm
            w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; r[i] -= w * r[i - 1]
        T[n - 1] = r[n - 1] / b[n - 1]
        for i in range(n - 2, -1, -1):
            T[i] = (r[i] - c[i] * T[i + 1]) / b[i]
        if s >= steps_per * (cycles - 1): rec.append(T[probe_i])
    return (max(rec) - min(rec)) / 2

DAY = 86400.0
daily = {d: amplitude(d, DAY, 10.0, 0.005, 300.0, 5) for d in (0, 1, 2, 3, 4, 6, 8)}
print("daily amplitude at 5 cm (C):", {d: round(v, 3) for d, v in daily.items()})
YEAR = 365 * DAY
ann = {d: amplitude(d, YEAR, 15.0, 0.02, 21600.0, 3) for d in (0, 4, 8)}
print("annual amplitude at 5 cm (C):", {d: round(v, 3) for d, v in ann.items()})
mono = all(daily[a] > daily[b] for a, b in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 8)))
flat = daily[4] - daily[8]
ann_cut = 1 - ann[4] / ann[0]
decay = daily[2] / daily[4]
print(f"monotone={mono}; 4->8 in saving {flat:.3f} C; annual cut at 4 in {ann_cut:.1%}; 2 in vs 4 in daily ratio {decay:.1f}x")
ok = mono and daily[4] < 0.3 * 1.0 + 0.0 and flat < 0.3 and ann_cut < 0.15 and 1.5 < decay < 3.5
print("RESULT:", "PASS" if ok else "FAIL", f"daily bare {daily[0]:.2f} 2in {daily[2]:.2f} 4in {daily[4]:.2f} 8in {daily[8]:.2f} C; annual cut at 4 in {ann_cut:.1%}; decayed 2 in = {decay:.1f}x the 4 in swing")
