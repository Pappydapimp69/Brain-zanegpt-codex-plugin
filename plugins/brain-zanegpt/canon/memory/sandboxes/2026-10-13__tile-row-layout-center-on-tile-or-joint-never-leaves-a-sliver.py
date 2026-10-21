"""Prediction (before run): tile width t=300, grout g=3, pitch p=303, room width W integer mm from 1500 to 4500 (3001 widths).
Edge cut = length of the partial tile at a wall (0 if a joint or a full tile ends at the wall).
P1 wall-start (grid begins at the left wall) leaves a right-wall cut that is a sliver (0 < cut < t/4 = 75) for 20-30% of widths.
P2 centering on a tile (symmetric, equal cuts) leaves a sliver for 20-30% of widths too (the sliver just moves to both ends, or a mirrored pair).
P3 choosing the better of center-on-tile and center-on-joint (a half-pitch shift) leaves NO sliver under 75 mm in any width; the minimum over widths of the smaller nonzero cut is >= 75.
P4 (BREAK) the guarantee depends on the threshold: with threshold 100 (t/3) the better-of-two rule still leaves slivers in at least 1 width; report the worst-case smallest cut and the largest threshold with zero slivers.
Stdlib, deterministic exhaustive sweep."""
t, g = 300, 3
p = t + g
def cuts(W, o):
    # tiles occupy [o + i*p, o + i*p + t]; room [0, W]; return (left cut, right cut) lengths of partial tiles at the walls
    x0 = o % p
    # a tile starts at x0 - p (partial, if x0 > 0) ending at x0 - p + t = x0 - g
    left = max(0, x0 - g) if x0 > 0 else 0
    if left >= t: left = 0
    # right wall
    k = (W - o) // p          # last tile index starting at or before W... use floor
    start = o + k * p
    right = W - start if W - start < t else 0   # partial tile at right wall
    if W - start >= t: right = 0
    return left, right
def smallest_nonzero(cs): 
    z = [c for c in cs if c > 0]
    return min(z) if z else None
def opt_wall(W): return 0
def opt_center_tile(W):
    # a tile centered on the room centre: its left edge at W/2 - t/2 -> o (doubled to stay integer)
    return (W - t) / 2
def opt_center_joint(W):
    return W / 2 + g / 2   # a joint centred on the room centre: the tile right of the joint starts at W/2 + g/2
def sliver(W, o, th=75):
    c = cuts(W, o); s = smallest_nonzero(c); return s is not None and s < th, c
def frac(fn, th=75):
    Ws = range(1500, 4501); n = 0
    for W in Ws:
        n += sliver(W, fn(W), th)[0]
    return n / len(Ws)
def best(W, th):
    cand = [opt_center_tile(W), opt_center_joint(W)]
    res = []
    for o in cand:
        c = cuts(W, o); s = smallest_nonzero(c)
        res.append((s if s is not None else 10**9, o))
    return max(res)[0]
def frac_best(th=75):
    Ws = range(1500, 4501)
    return sum(1 for W in Ws if best(W, th) < th) / len(Ws)
f_wall = frac(opt_wall); f_ct = frac(opt_center_tile); f_cj = frac(opt_center_joint); f_best = frac_best()
worst = min(best(W, 0) for W in range(1500, 4501))
th_zero = max(th for th in range(1, 200) if frac_best(th) == 0)
f100 = frac_best(100)
print(f"sliver<75: wall {f_wall:.3f} center-tile {f_ct:.3f} center-joint {f_cj:.3f} best-of-two {f_best:.3f}; worst smallest cut best-of-two {worst}; largest zero-sliver threshold {th_zero}; at 100: {f100:.3f}")
p1 = .20 <= f_wall <= .30; p2 = .20 <= f_ct <= .30; p3 = f_best == 0 and worst >= 75; p4 = f100 > 0
print("P1", p1, "P2", p2, "P3", p3, "P4", p4)
print("RESULT:", "PASS" if all([p1, p2, p3, p4]) else "FAIL", f"{sum([p1,p2,p3,p4])}/4 held; sliver fractions wall {f_wall:.3f} center-tile {f_ct:.3f} center-joint {f_cj:.3f} best-of-two {f_best:.3f}; worst smallest cut {worst}; zero-sliver threshold up to {th_zero}")
