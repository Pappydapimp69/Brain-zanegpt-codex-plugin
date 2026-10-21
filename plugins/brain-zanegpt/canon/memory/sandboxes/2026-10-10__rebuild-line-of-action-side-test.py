"""Rebuild: 180-degree rule side test vs real screen projection.
PREDICTION (written before running):
 P1 projection order flip == side-sign change, 0 mismatches over ~180k camera pairs (exact rational projection AND float projection),
    for cameras off the line with both subjects in front of the lens.
 P2 inclusive test (cross>=0 -> left, cross<=0 -> right) double-assigns 100% of on-line cameras; half-open assigns each exactly once.
 P3 float cross product misclassifies >=1 exactly-on-line decimal camera (exact Fraction says 0); I expect a fraction of roughly 15-50%.
 P4 (breaker) with dyadic coordinates (exact in binary) float misclassifies 0 -> the failure is about decimal representation, not about floats per se.
 P5 (breaker) half-open on exact cross never yields 'both' or 'neither' for any camera, on-line or not.
Fixture is my own: subjects A=(0.3,0.1) B=(0.9,0.7) (45-degree line), cameras on a 0.01 grid from an LCG seed 7,
lenses aimed with rational aim vectors (no trig), not the original's layout.
"""
from fractions import Fraction as F
from decimal import Decimal

def parse(s): return F(Decimal(s))
A_s = ("0.3", "0.1"); B_s = ("0.9", "0.7")
A = tuple(parse(v) for v in A_s); B = tuple(parse(v) for v in B_s)
Af = tuple(float(v) for v in A_s); Bf = tuple(float(v) for v in B_s)

def cross_exact(c):  # cross(B-A, C-A)
    return (B[0]-A[0])*(c[1]-A[1]) - (B[1]-A[1])*(c[0]-A[0])
def cross_float(cs):
    c = (float(cs[0]), float(cs[1]))
    return (Bf[0]-Af[0])*(c[1]-Af[1]) - (Bf[1]-Af[1])*(c[0]-Af[0])
def inclusive(x):  # returns set of sides claimed
    s = set()
    if x >= 0: s.add("L")
    if x <= 0: s.add("R")
    return s
def half_open(x):
    return {"L"} if x > 0 else {"R"}   # zero goes to R

# LCG deterministic
state = 7
def rnd(n):
    global state
    state = (state * 1103515245 + 12345) % (2**31)
    return (state >> 8) % n

def dot(u, v): return u[0]*v[0] + u[1]*v[1]

def screen_order(c, aim, num=F):
    """+1 if A is left of B on screen, -1 if right; None if a subject is not in front of lens."""
    d = aim; r = (d[1], -d[0])  # right vector
    va = (A[0]-c[0], A[1]-c[1]); vb = (B[0]-c[0], B[1]-c[1])
    da, db = dot(va, d), dot(vb, d)
    if da <= 0 or db <= 0: return None
    xa, xb = dot(va, r)/da, dot(vb, r)/db
    if xa == xb: return 0
    return 1 if xa < xb else -1

def screen_order_float(c, aim):
    cf = (float(c[0]), float(c[1])); d = (float(aim[0]), float(aim[1])); r = (d[1], -d[0])
    va = (Af[0]-cf[0], Af[1]-cf[1]); vb = (Bf[0]-cf[0], Bf[1]-cf[1])
    da, db = dot(va, d), dot(vb, d)
    if da <= 0 or db <= 0: return None
    xa, xb = dot(va, r)/da, dot(vb, r)/db
    if xa == xb: return 0
    return 1 if xa < xb else -1

# --- P1 / P5: random cameras off the line
cams = []
mid = ((A[0]+B[0])/2, (A[1]+B[1])/2)
while len(cams) < 600:
    c = (F(rnd(2001)-1000, 100), F(rnd(2001)-1000, 100))
    if cross_exact(c) == 0: continue
    aim = (mid[0]-c[0] + F(rnd(201)-100, 50), mid[1]-c[1] + F(rnd(201)-100, 50))
    if aim == (0, 0): continue
    o = screen_order(c, aim)
    if o is None or o == 0: continue
    of = screen_order_float(c, aim)
    cams.append((c, o, of, half_open(cross_exact(c))))
skipped_note = len(cams)
pairs = mism_exact = mism_float = both_or_neither = 0
for i in range(len(cams)):
    ci, oi, fi, hi = cams[i]
    if len(hi) != 1: both_or_neither += 1
    for j in range(i+1, len(cams)):
        cj, oj, fj, hj = cams[j]
        pairs += 1
        side_change = hi != hj
        if (oi != oj) != side_change: mism_exact += 1
        if (fi != fj) != side_change: mism_float += 1
print("pairs", pairs, "mismatch_exact_proj", mism_exact, "mismatch_float_proj", mism_float, "half_open_not_single", both_or_neither)

# --- P2/P3: exactly-on-line decimal cameras A + k*(0.06,0.06)*..., written as decimal strings
online = []
for k in range(-300, 301):   # x = 0.3 + 0.01k, y = 0.1 + 0.01k  (on line y = x - 0.2)
    xs = Decimal("0.3") + Decimal("0.01")*k; ys = Decimal("0.1") + Decimal("0.01")*k
    online.append((str(xs), str(ys)))
n = len(online)
exact_zero = sum(1 for c in online if cross_exact((parse(c[0]), parse(c[1]))) == 0)
incl_double = sum(1 for c in online if len(inclusive(cross_exact((parse(c[0]), parse(c[1]))))) == 2)
half_single = sum(1 for c in online if len(half_open(cross_exact((parse(c[0]), parse(c[1]))))) == 1)
float_wrong = sum(1 for c in online if cross_float(c) != 0)
float_incl_wrong = sum(1 for c in online if len(inclusive(cross_float(c))) != 2)
float_half_move = sum(1 for c in online if half_open(cross_float(c)) != half_open(0))
print("online", n, "exact_zero", exact_zero, "inclusive_double", incl_double, "half_open_single", half_single,
      "float_nonzero", float_wrong, f"({float_wrong/n:.3f})", "float_half_open_misplaced", float_half_move)

# --- P4 breaker: dyadic coordinates exact in binary
Ad, Bd = (F(1, 4), F(1, 8)), (F(7, 8), F(5, 8))
dy_wrong = 0; dy_n = 0
for k in range(-200, 201):
    t = F(k, 16)
    c = (Ad[0] + t*(Bd[0]-Ad[0]), Ad[1] + t*(Bd[1]-Ad[1]))
    x = (float(Bd[0]-Ad[0]))*(float(c[1]-Ad[1])) - (float(Bd[1]-Ad[1]))*(float(c[0]-Ad[0]))
    dy_n += 1; dy_wrong += (x != 0)
print("dyadic", dy_n, "float_nonzero", dy_wrong)

# --- near-line cameras (offset 1e-9 off the line): float should still agree with exact sign
near_bad = 0; near_n = 0
for k in range(-300, 301):
    for off in (F(1, 10**9), F(-1, 10**9)):
        c = (F(3, 10) + F(k, 100) , F(1, 10) + F(k, 100) + off)
        near_n += 1
        if (cross_exact(c) > 0) != (cross_float((float(c[0]), float(c[1]))) > 0): near_bad += 1
print("near_line", near_n, "float_sign_disagree", near_bad)

ok = (pairs >= 170000 and mism_exact == 0 and mism_float == 0 and both_or_neither == 0
      and exact_zero == n and incl_double == n and half_single == n
      and float_wrong >= 1 and dy_wrong == 0)
frac = float_wrong / n
print("RESULT: %s pairs=%d proj_mismatch=%d/%d inclusive_double=%d/%d half_open_single=%d/%d float_online_misclass=%d/%d(%.2f) dyadic_misclass=%d near_line_disagree=%d"
      % ("PASS" if ok else "FAIL", pairs, mism_exact, mism_float, incl_double, n, half_single, n, float_wrong, n, frac, dy_wrong, near_bad))
