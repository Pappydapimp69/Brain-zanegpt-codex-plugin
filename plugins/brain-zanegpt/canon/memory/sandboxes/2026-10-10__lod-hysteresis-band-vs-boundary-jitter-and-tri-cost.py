# RUN 1 result: FAIL on my own prediction. A sine crosses the boundary twice per cycle, so 4 cycles give 8 switches, not >=100,
# and I also had the delay direction backwards (the code comment below says "recede"; the run showed the delay is on APPROACH and
# recede is unprotected). RUN 2 prediction, written before re-running: S1=8 exactly; S2<=1; S3 (amp6 > band 2.5)=8 (no help);
# S3b (h=.20, band 10)<=1; ramp approach h=.05 delays entering LOD0 by ~25 frames (2.5 units / 0.1 per frame) and saves tris;
# recede first-LOD1 frame identical for h=0 and h=.05 (one-sided band).
# Prediction (before run): camera jitter of amplitude 2 around the 50-unit LOD boundary (30 samples/cycle, 4 cycles) flips
# every sample pair without hysteresis (>=100 switches), and a three.js-style hysteresis of 0.05 (visible level threshold
# shifted by 2.5 units) cuts it to <=1 switch. Built to break: amplitude 6 exceeds the band, so flicker must come back (>=20 switches).
# A monotonic approach must show the price: the switch is delayed by h*dist, costing extra triangles over the delay.
import math
LEVELS = [(0.0, 10000), (50.0, 2500), (100.0, 600)]       # (min distance, triangles)
def pick(d, cur, h):
    # three.js LOD.update: first level (from far) whose threshold <= d, threshold of the CURRENT level reduced by h*distance
    new = 0
    for i in range(1, len(LEVELS)):
        thr = LEVELS[i][0]
        if i == cur: thr -= thr * h
        if d >= thr: new = i
        else: break
    return new
def run(path, h):
    cur = pick(path[0], -1, 0.0); sw = 0; tris = 0; levels = []
    for d in path:
        n = pick(d, cur, h)
        if n != cur: sw += 1; cur = n
        levels.append(cur); tris += LEVELS[cur][1]
    return sw, tris, levels
def jitter(center, amp, cycles=4, per=30):
    return [center + amp * math.sin(2 * math.pi * k / per + 0.3) for k in range(cycles * per)]
S1 = run(jitter(50, 2), 0.0)[0]
S2 = run(jitter(50, 2), 0.05)[0]
S3 = run(jitter(50, 6), 0.05)[0]
S3b = run(jitter(50, 6), 0.20)[0]
ramp = [70 - 0.1 * k for k in range(400)]                 # monotonic approach 70 -> 30
_, t0, l0 = run(ramp, 0.0); _, t5, l5 = run(ramp, 0.05); _, t20, l20 = run(ramp, 0.20)
# a crossfade of F frames at each real switch costs both LODs for F frames
def xfade_cost(levels, F=6):
    extra = 0
    for k in range(1, len(levels)):
        if levels[k] != levels[k-1]:
            extra += F * LEVELS[levels[k-1]][1]
    return extra
x0 = xfade_cost(l0)
late0 = l0.index(0); late5 = l5.index(0)                   # first frame at LOD0 on approach
print(f"S1 amp2 h=0: switches={S1}; S2 amp2 h=.05: {S2}; S3 amp6 h=.05: {S3}; S3b amp6 h=.20: {S3b}")
print(f"S4 ramp first LOD0 frame h0={late0} h.05={late5} (delay {late5-late0} frames); tris h0={t0} h.05={t5} h.20={t20}")
print(f"S5 crossfade extra tris for the {2} real switches on ramp: {x0}")
# one-sided band: the shifted threshold belongs to the CURRENT level, so only the near-side exit of LOD1 is delayed.
rec = [30 + 0.1 * k for k in range(400)]
_, tr0, lr0 = run(rec, 0.0); _, tr5, lr5 = run(rec, 0.05)
print(f"S6 recede 30->70: first LOD1 frame h0={lr0.index(1)} h.05={lr5.index(1)}; tris h0={tr0} h.05={tr5}")
ok = S1 == 8 and S2 <= 1 and S3 == 8 and S3b <= 1 and 20 <= late5-late0 <= 30 and t5 < t0 and lr0.index(1) == lr5.index(1)
print(f"RESULT: {'PASS' if ok else 'FAIL'} switches amp2 h0={S1} h.05={S2}; amp6 h.05={S3} h.20={S3b}; recede tris h0={tr0} h.05={tr5}")
