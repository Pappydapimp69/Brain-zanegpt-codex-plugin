"""Prediction (before run): with only M2 (12.4206 h, amp 1.00) and S2 (12.0000 h, amp 0.46) the daily tidal range
peaks every 1/(1/12 - 1/12.4206) h = 14.765 d (measured peak spacing within +-0.1 d); spring range ~ 2*(1+0.46)=2.92
and neap ~ 2*(1-0.46)=1.08 (within 3%); with amp S2 > amp M2 the beat period is unchanged but the phase flips
(range min is then 2*(0.46... swapped)); adding a diurnal K1 term (23.9345 h) does NOT move the 14.77 d period of
the semidiurnal range. Stdlib, hourly step, deterministic, no RNG."""
import math
M2, S2, K1 = 12.4206012, 12.0, 23.9344697
def h(t, aM, aS, aK):
    return aM*math.cos(2*math.pi*t/M2) + aS*math.cos(2*math.pi*t/S2) + aK*math.cos(2*math.pi*t/K1)
def daily_range(aM, aS, aK, days=120):
    out = []
    for d in range(days):
        vals = [h(d*24 + k*0.25, aM, aS, aK) for k in range(96)]
        out.append(max(vals) - min(vals))
    return out
def peaks(r):
    return [i for i in range(1, len(r)-1) if r[i] >= r[i-1] and r[i] > r[i+1]]
def spacing(r):
    p = peaks(r); return sum(b-a for a, b in zip(p, p[1:])) / (len(p)-1)
pred = 1/(1/12.0 - 1/M2)/24
r1 = daily_range(1.0, 0.46, 0.0)
sp1 = spacing(r1); hi, lo = max(r1), min(r1)
print("s1 M2+S2: predicted beat %.3f d, measured peak spacing %.2f d, range max %.2f min %.2f (formula 2.92/1.08)" % (pred, sp1, hi, lo))
r2 = daily_range(0.46, 1.0, 0.0)
sp2 = spacing(r2); print("s2 swapped amps: spacing %.2f d, max %.2f min %.2f" % (sp2, max(r2), min(r2)))
r3 = daily_range(1.0, 0.46, 0.8)
sp3 = spacing(r3); print("s3 +K1 diurnal: spacing %.2f d, max %.2f min %.2f" % (sp3, max(r3), min(r3)))
# BREAK: shrink the observation to one beat vs a sample every 2 days (aliasing)
def dom_period(r):
    n = len(r); m = sum(r)/n; x = [v-m for v in r]; best = (0, 0)
    for k10 in range(40, 1000):          # periods 2.0 .. 50 d on a 0.01 cycles/day grid-free search
        T = k10/20.0
        w = 2*math.pi/T
        c = sum(v*math.cos(w*i) for i, v in enumerate(x)); sn = sum(v*math.sin(w*i) for i, v in enumerate(x))
        p = c*c + sn*sn
        if p > best[0]: best = (p, T)
    return best[1]
big1 = daily_range(1.0, 0.46, 0.0, 360); big3 = daily_range(1.0, 0.46, 0.8, 360)
d1, d3 = dom_period(big1), dom_period(big3)
print("iteration2 DFT dominant period of daily range, 360 d: M2+S2 %.2f d ; +K1 %.2f d" % (d1, d3))
r4 = r1[::2]; sp4 = spacing(r4) * 2; print("s4 sampled every 2 d: apparent spacing %.2f d" % sp4)
ok = abs(sp1 - pred) < 0.6 and abs(hi-2.92)/2.92 < .05 and abs(lo-1.08)/1.08 < .08 and abs(sp2 - pred) < 0.6 and abs(d1 - pred) < 0.6
print("RESULT: %s beat_pred=%.3f d measured=%.2f d range=%.2f/%.2f swapped=%.2f d with_K1_peak_spacing=%.2f d dft_M2S2=%.2f d dft_with_K1=%.2f d (K1 range %.2f/%.2f) sampled2d=%.2f d" % ("PASS" if ok else "FAIL", pred, sp1, hi, lo, sp2, sp3, d1, d3, max(r3), min(r3), sp4))
