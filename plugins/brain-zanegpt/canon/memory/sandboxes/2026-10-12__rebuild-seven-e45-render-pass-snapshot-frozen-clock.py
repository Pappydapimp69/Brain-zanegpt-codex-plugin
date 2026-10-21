"""Blind rebuild of seven E45 (snapshot of an animated page needs a frozen clock).
Own fixture: a page with 3 elements: a marquee at v px/s, a CSS rotation shown as
an x offset r*sin(w t), and a static header. Capture = navigation + render-pass
settle (fixed 300 ms) + capture latency jitter drawn from a seeded LCG
(uniform 0-80 ms, plus one 'GC pause' of 120 ms every 10th capture). Pixel =
round(x). A pair (baseline, check) of an UNCHANGED page 'differs' if any
element's pixel differs by >= 1. 200 pairs per speed.
PREDICTION (before running): live clock at 120 px/s -> >= 0.75 pairs differ;
frozen clock (t pinned at 300 ms) -> 0 at every speed; max diff grows with
speed; static page -> 0. Break scenario: a slow animation (5 px/s) -> live
clock passes mostly (< 0.5 differ), i.e. the defect hides at low speeds and a
'render pass only' check would look fine in review.
"""
import math, sys
print("python", sys.version.split()[0])
class LCG:
    def __init__(s, seed): s.x = seed & 0xffffffff
    def u(s):
        s.x = (1664525*s.x + 1013904223) & 0xffffffff; return s.x/2**32
def capture(t, v, static):
    if static: return (10, 20, 30)
    return (round(v*t) % 1000, round(40*math.sin(2*math.pi*0.5*t)), 30)
def run(v, frozen, static=False, n=200, seed=7):
    g = LCG(seed); diff = 0; mx = 0
    for i in range(n):
        ts = []
        for j in range(2):
            lat = g.u()*0.080 + (0.120 if (2*i+j) % 10 == 9 else 0)
            ts.append(0.300 if frozen else 0.300+lat)
        a, b = capture(ts[0], v, static), capture(ts[1], v, static)
        d = max(abs(x-y) for x, y in zip(a, b))
        diff += d >= 1; mx = max(mx, d)
    return diff/n, mx
res = {}
for v in [5, 30, 120, 480]:
    res[v] = (run(v, False), run(v, True))
    print(f"v {v:3d}: live differ {res[v][0][0]:.3f} max {res[v][0][1]:3d}px | frozen differ {res[v][1][0]:.3f}")
st = run(120, False, static=True)
print("static page live:", st)
# marquee-only (no sine element) to isolate speed effect
def run_marquee(v):
    g = LCG(7); n = 200; dcount = 0
    for i in range(n):
        t = [0.3+g.u()*0.08+(0.12 if (2*i+j) % 10 == 9 else 0) for j in range(2)]
        dcount += round(v*t[0]) != round(v*t[1])
    return dcount/n
m5 = run_marquee(5); print("break: marquee only at 5 px/s live differ", m5)
c1 = res[120][0][0] >= 0.75
c2 = all(res[v][1][0] == 0 for v in res)
mxs = [res[v][0][1] for v in sorted(res)]; c3 = all(a <= b for a, b in zip(mxs, mxs[1:]))
c4 = st[0] == 0
ok = c1 and c2 and c3 and c4
print(f"RESULT: {'PASS' if ok else 'FAIL'} live@120 {res[120][0][0]:.3f}; frozen all 0={c2}; max px {mxs}; static {st[0]}; slow marquee-only {m5:.3f}")
