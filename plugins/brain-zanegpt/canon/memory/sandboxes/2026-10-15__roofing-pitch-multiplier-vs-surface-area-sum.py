# Roofing: material area = plan area * sqrt(1+(p/12)^2) ("pitch multiplier"). Check it against an
# independent surface-area sum from 3D vertices (cross products), then try to break it.
import math

def tri(a, b, c):
    u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
    w = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
    return 0.5 * math.sqrt(sum(x*x for x in w))
def quad(a, b, c, d): return tri(a, b, c) + tri(a, c, d)
def mult(p): return math.sqrt(1 + (p / 12.0) ** 2)

def gable(W, L, p, ov=0.0):
    """ridge along length; overhang ov added on all four plan sides; rise measured at pitch p over half-span incl. overhang"""
    hw = W / 2 + ov; Le = L + 2 * ov
    h = hw * p / 12.0
    A = (-hw, -Le/2, 0); B = (-hw, Le/2, 0); R1 = (0, Le/2, h); R0 = (0, -Le/2, h)
    C = (hw, Le/2, 0); D = (hw, -Le/2, 0)
    return quad(A, B, R1, R0) + quad(D, C, R1, R0)
def hip(W, L, p):
    hw, hl = W/2, L/2; h = hw * p / 12.0; rl = hl - hw      # square-ish hip: ridge length L-W
    A=(-hw,-hl,0);B=(-hw,hl,0);C=(hw,hl,0);D=(hw,-hl,0); R0=(0,-rl,h); R1=(0,rl,h)
    return quad(A,B,R1,R0)+quad(D,C,R1,R0)+tri(A,D,R0)+tri(B,C,R1)

W, L = 30.0, 40.0
res = {}
errs_g = [abs(gable(W, L, p) - W*L*mult(p)) / (W*L*mult(p)) for p in (4, 6, 9, 12)]
errs_h = [abs(hip(W, L, p) - W*L*mult(p)) / (W*L*mult(p)) for p in (4, 6, 9, 12)]
# BREAK 1: overhang of 1 ft means the roof's plan is 32x42, not the house footprint 30x40
gab_ov = gable(W, L, 6, ov=1.0); naive = W*L*mult(6)
err_ov = (gab_ov - naive) / gab_ov
# BREAK 2: a 10x12 shed dormer at 3/12 on a 6/12 main roof: single pitch multiplier applied to whole plan
main_plan = W*L - 10*12; dorm_plan = 10*12
true_area = main_plan*mult(6) + dorm_plan*mult(3)
naive2 = W*L*mult(6)
err_mix = (naive2 - true_area) / true_area
# BREAK 3: ordering of squares: 100 sq ft per square, 10% waste -> bundles rounding is a separate step
squares = math.ceil(W*L*mult(6)*1.10/100)
print("max rel err gable %.2e hip %.2e over 4/12..12/12" % (max(errs_g), max(errs_h)))
print("overhang 1ft: footprint-based estimate short by %.1f%%" % (100*err_ov))
print("mixed pitch dormer: single multiplier off by %.2f%%" % (100*err_mix))
print("squares to order at 6/12 with 10%% waste: %d" % squares)
ok = max(errs_g) < 1e-9 and max(errs_h) < 1e-9 and err_ov > 0.05 and abs(err_mix) > 0.003
print("RESULT: %s pitch multiplier exact for gable and hip (err <1e-9), but footprint-only estimate is %.1f%% short with a 1 ft overhang and a 3/12 dormer shifts it %.2f%%"
      % ("PASS" if ok else "FAIL", 100*err_ov, 100*err_mix))
