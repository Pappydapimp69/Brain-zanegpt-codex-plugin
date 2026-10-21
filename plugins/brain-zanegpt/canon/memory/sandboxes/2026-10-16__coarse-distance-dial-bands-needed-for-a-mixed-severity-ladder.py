"""Severe-harm-needs-distance + mild-harm-needs-closeness + matched-distance escalation,
with the distance dial quantised into B bands over a BFS walkable map (sandbox-distance).
Assumption: a continuous dial is needed. Beat with severity s in 1..10 wants distance target
t(s) = s/10 for severe beats (s>=6, further = safer) and ALSO t(s) = s/10 for mild beats but the
gate for mild beats is one-sided-narrow (closeness: gate width 0.10 vs 0.25 for severe), as in the
two-sided finding. Dial position p in [0,1] = BFS distance / max BFS distance, snapped to the centre
of one of B equal bands. Fit = mean over a mixed ladder of exp(-((p - t)/w)^2).
Prediction (before run): 4 bands retain >= 0.85 of the continuous fit; 2 bands < 0.75; and on a
serpentine map (BFS span large) the 4-band result is the same as on an open map within 0.02 because
bands are in normalised units. Breaker: 1 band (no dial) < 0.5."""
import math
from collections import deque
N = 21
def bfs_span(walls):
    d = {(0, 0): 0}; q = deque([(0, 0)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n = (x+dx, y+dy)
            if 0 <= n[0] < N and 0 <= n[1] < N and n not in walls and n not in d:
                d[n] = d[(x, y)] + 1; q.append(n)
    return d
serp = set()
for i, x in enumerate(range(3, 20, 4)):
    serp |= {(x, y) for y in (range(0, 19) if i % 2 == 0 else range(2, 21))}
maps = {"open": set(), "serpentine": serp}
ladder = [(2, .10), (3, .10), (4, .10), (6, .25), (8, .25), (10, .25)]   # (severity, gate width)
def fit(B, d):
    cells = list(d); mx = max(d.values()); tot = 0
    for s, w in ladder:
        t = s / 10
        if B is None:
            p = min((d[c] / mx for c in cells), key=lambda p: abs(p - t))
        else:
            # snapped dial: only B levels exist
            levels = [(k + .5) / B for k in range(B)]
            p = min(levels, key=lambda l: abs(l - t))
        tot += math.exp(-((p - t) / w) ** 2)
    return tot / len(ladder)
R = {}
for name, w in maps.items():
    d = bfs_span(w)
    R[name] = {"cont": fit(None, d), **{B: fit(B, d) for B in (1, 2, 3, 4, 6)}}
    print(name, {k: round(v, 3) for k, v in R[name].items()})
o = R["open"]; sp = R["serpentine"]
a = o[4] / o["cont"] >= 0.85
b = o[2] / o["cont"] < 0.75
c = abs(o[4] - sp[4]) <= 0.02
e = o[1] < 0.5
print(f"RESULT: {'PASS' if a and b and c and e else 'FAIL'} b4_ratio={o[4]/o['cont']:.3f} b2_ratio={o[2]/o['cont']:.3f} "
      f"b4_open_vs_serp={abs(o[4]-sp[4]):.3f} b1={o[1]:.3f}")
