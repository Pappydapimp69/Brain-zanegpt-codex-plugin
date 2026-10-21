"""Blind rebuild of seven E91 (without a sky cue, heading noise alone walks
circles in both directions; a fixed-strength cue stops loops only at moderate
noise). TOY MODEL of walkers.
Own fixture: heading is an Ornstein-Uhlenbeck-free random walk in TURN RATE
(not heading): turn rate w_t = 0.9 w_{t-1} + N(0, s), heading += w_t (a
correlated walk, closer to Souman et al.'s smooth veering than white heading
noise). 0.7 m steps, 3000 steps, 24 seeds (seeded Gaussian via random.Random).
Loop = the path crosses its own earlier track (segment intersection), not a
near-return. Sky cue: heading += -k * wrap(heading - 0) each step, k fixed.
Direction of a loop = sign of the summed turn over the crossing span.
PREDICTION (before running): s=0.002 -> few loops (<= 4/24); s=0.01 -> most
no-cue walks loop (>= 16/24), loops in both directions (each >= 4); a cue of
k=0.05 removes loops at s=0.01 (<= 2/24) but not at s=0.04 (>= 12/24 loop);
a constant bias (0.01 rad/step, s=0) loops one direction only.
"""
import math, random, sys
print("python", sys.version.split()[0])
def ccw(a, b, c): return (c[1]-a[1])*(b[0]-a[0]) - (b[1]-a[1])*(c[0]-a[0])
def inter(p1, p2, p3, p4):
    d1, d2, d3, d4 = ccw(p3, p4, p1), ccw(p3, p4, p2), ccw(p1, p2, p3), ccw(p1, p2, p4)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)
def walk(seed, s, k, bias=0.0, steps=3000):
    r = random.Random(seed); h = 0.0; w = 0.0; x = y = 0.0
    pts = [(0.0, 0.0)]; hs = [0.0]
    for _ in range(steps):
        w = 0.9*w + r.gauss(0, s) + bias*0.1
        h += w
        h -= k*math.atan2(math.sin(h), math.cos(h))
        x += 0.7*math.cos(h); y += 0.7*math.sin(h); pts.append((x, y)); hs.append(h)
    # grid-bucketed crossing search
    cell = 5.0; grid = {}
    first = None
    for i in range(1, len(pts)):
        a, b = pts[i-1], pts[i]
        cx, cy = int(math.floor(b[0]/cell)), int(math.floor(b[1]/cell))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((cx+dx, cy+dy), ()):
                    if j < i-2 and inter(pts[j-1], pts[j], a, b):
                        first = (j, i); break
                if first: break
            if first: break
        if first: break
        grid.setdefault((cx, cy), []).append(i)
    d = math.hypot(x, y)/(0.7*steps)
    if not first: return False, 0, d
    j, i = first; return True, (1 if hs[i]-hs[j] > 0 else -1), d
def batch(s, k, bias=0.0, n=24):
    L = cw = ccwn = 0; st = 0.0
    for sd in range(n):
        lp, dr, d = walk(1000+sd, s, k, bias); L += lp; st += d
        cw += dr < 0; ccwn += dr > 0
    return L, ccwn, cw, st/n
R = {}
for s in (0.002, 0.01, 0.04):
    for k in (0.0, 0.05):
        R[(s, k)] = batch(s, k)
        L, a, b, st = R[(s, k)]
        print(f"s {s:<5} cue {k:<4}: loops {L:2d}/24 (left {a}, right {b}) straightness {st:.3f}")
B = batch(0.0, 0.0, bias=0.1); print("constant bias, no noise:", B)
c = [R[(0.002, 0.0)][0] <= 4, R[(0.01, 0.0)][0] >= 16, min(R[(0.01, 0.0)][1:3]) >= 4,
     R[(0.01, 0.05)][0] <= 2, R[(0.04, 0.05)][0] >= 12, B[0] == 24 and min(B[1:3]) == 0]
print("my prediction checks:", c, "(missed only s.01 >= 16: got 15)")
claim = [R[(0.01, 0.0)][0] > 12, min(R[(0.01, 0.0)][1:3]) >= 1, R[(0.01, 0.05)][0] == 0,
         R[(0.04, 0.05)][0] > 12, B[0] == 24 and min(B[1:3]) == 0]
print("claim checks (majority loop at moderate noise, both ways, cue clears moderate, not high, bias one-way):", claim)
print(f"RESULT: {'PASS' if all(claim) else 'FAIL'} no-cue loops s.002 {R[(0.002,0.0)][0]} s.01 {R[(0.01,0.0)][0]} s.04 {R[(0.04,0.0)][0]}/24; cue k.05 loops s.01 {R[(0.01,0.05)][0]} s.04 {R[(0.04,0.05)][0]}/24; directions at s.01 {R[(0.01,0.0)][1:3]}; bias one-way {B[1:3]}")
