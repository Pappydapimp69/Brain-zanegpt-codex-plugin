"""Prediction (before run): (1) For every pair of off-line camera positions on a 21x21 integer grid (line of action A=(0,0),
B=(6,0)... plus a slanted line), the screen-order of A and B (from a real projection: camera aims at the midpoint) flips
exactly when the sign of cross(B-A, cam-A) changes: 0 mismatches. (2) Cameras exactly ON the line: projection is degenerate
(A and B project to the same screen x), so no flip is defined; an inclusive-both-sides side test (>=0 / <=0) puts each such
camera on BOTH sides and reports a 'cut across the line' for pairs that are not crossings, while a half-open test
(>0 is left, <=0 is right) gives each camera exactly one side. Expect inclusive double-counts == number of on-line cameras (19 after excluding A and B).
ITERATION 1 FAIL: inclusive test built a set of booleans (always size 1) and the decimal points were float-exact; fixed both.
(3) Built to break: on a decimal slanted line A=(0.1,0.2) B=(0.3,0.6), float cross() calls at least one exactly-on-line
camera off-line while Fractions classify it on-line. Deterministic, stdlib only."""
from fractions import Fraction as F
from itertools import combinations
def cross(A, B, C): return (B[0]-A[0])*(C[1]-A[1]) - (B[1]-A[1])*(C[0]-A[0])
def screen_order(A, B, cam):
    m = ((A[0]+B[0])/2, (A[1]+B[1])/2)
    fx, fy = m[0]-cam[0], m[1]-cam[1]
    rx, ry = fy, -fx   # right-hand vector (forward rotated -90 deg)
    sa = (A[0]-cam[0])*rx + (A[1]-cam[1])*ry
    sb = (B[0]-cam[0])*rx + (B[1]-cam[1])*ry
    return (sa > sb) - (sa < sb)       # +1: A right of B on screen
def side_halfopen(c): return 1 if c > 0 else 0   # >0 one side, <=0 the other
def side_inclusive(c): return {s for s, ok in ((1, c >= 0), (0, c <= 0)) if ok}   # sides it belongs to
def run(A, B, cams):
    mism = 0; pairs = 0
    off = [c for c in cams if cross(A, B, c) != 0]
    for c1, c2 in combinations(off, 2):
        if (c1 == (A[0]+B[0])/2 and c1[1] == (A[1]+B[1])/2): continue
        o1, o2 = screen_order(A, B, c1), screen_order(A, B, c2)
        if o1 == 0 or o2 == 0: continue
        pairs += 1
        flip = o1 != o2
        crossing = side_halfopen(cross(A, B, c1)) != side_halfopen(cross(A, B, c2))
        mism += flip != crossing
    return pairs, mism
grid = [(x, y) for x in range(-10, 11) for y in range(-10, 11)]
grid = [c for c in grid if c not in ((0, 0), (6, 0))]
A, B = (0, 0), (6, 0)
p1, m1 = run(A, B, grid)
online = [c for c in grid if cross(A, B, c) == 0]
degenerate = all(screen_order(A, B, c) == 0 for c in online if c not in (A, B) and not (0 < c[0] < 6) or False)
dbl = sum(len(side_inclusive(cross(A, B, c))) == 2 for c in online)
once = sum(1 for c in online if side_halfopen(cross(A, B, c)) in (0, 1))
# slanted line, integer grid: A=(1,2), B=(4,8) (direction 1:2)
A2, B2 = (1, 2), (4, 8)
grid2 = [c for c in grid if c not in (A2, B2)]
p2, m2 = run(A2, B2, grid2)
online2 = [c for c in grid2 if cross(A2, B2, c) == 0]
# break: decimal line, float vs exact (iteration 2: first decimal family happened to be float-exact; 0.1..0.7 family used)
Af, Bf = (0.1, 0.2), (0.7, 0.9)
Ae, Be = (F(1, 10), F(2, 10)), (F(7, 10), F(9, 10))
pts = [(Af[0] + (Bf[0]-Af[0])*(k/10), Af[1] + (Bf[1]-Af[1])*(k/10)) for k in range(1, 60)]
ptse = [(Ae[0] + (Be[0]-Ae[0])*F(k, 10), Ae[1] + (Be[1]-Ae[1])*F(k, 10)) for k in range(1, 60)]
fl_off = sum(cross(Af, Bf, c) != 0 for c in pts)
ex_off = sum(cross(Ae, Be, c) != 0 for c in ptse)
print("horizontal line: pairs", p1, "mismatches", m1, "| on-line cams", len(online), "inclusive double-sided", dbl, "half-open single", once)
print("slanted integer line: pairs", p2, "mismatches", m2, "| on-line cams", len(online2))
print("decimal line, 59 exactly-on-line cams: float says off-line", fl_off, "exact says off-line", ex_off)
ok = m1 == 0 and m2 == 0 and dbl == len(online) == once and ex_off == 0 and fl_off >= 1
print("RESULT:", "PASS" if ok else "FAIL", "projection flip == side change (0 mismatches over %d+%d pairs); on-line cams %d double-sided under inclusive, single under half-open; float misplaces %d of 59 on-line cams, exact %d" % (p1, p2, dbl, fl_off, ex_off))
