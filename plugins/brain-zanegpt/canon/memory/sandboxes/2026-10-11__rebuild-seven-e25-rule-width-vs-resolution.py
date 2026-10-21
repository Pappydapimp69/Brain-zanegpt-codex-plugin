"""Rebuild of seven E25: is the strength of the call-consistency tell set by the
WIDTH of the consistency rule rather than hearing resolution, and does silence
signal abandonment only when the call was strong?
Own fixture: 72 internal sectors (5 deg). Real second call = first + offset,
offset kernel triangular over -8..+8 internal sectors (+-40 deg, weight
9-|d|). False calls: two uniform bearings. Heard resolutions R = 24, 12, 8, 6,
4; a rule accepts heard difference <= k steps. Exact fractions.
Silence: prior 0.3 (not 0.5) that the member is beyond reach; inside the
window they call at c per night.
PREDICTIONS (written before running):
 P1 at (nearly) equal false-consistency rate f, LR differs by under 15% across
    resolutions (width, not resolution, sets strength)
 P2 at fixed resolution 8, the narrower rule (k=0) has a higher LR than k=1
 P3 c=0.9: two silent nights give >= 0.85 belief of 'beyond reach' at prior 0.3
 P4 c=0.3: three silent nights stay under 0.80
"""
from fractions import Fraction as Fr
M = 72
ker = {d: 9-abs(d) for d in range(-8, 9)}; KZ = sum(ker.values())
def q(s, R): return ((s*R*2 + M) // (2*M)) % R   # round to nearest of R centres
def stats(R, k):
    def cons(a, b): return min((a-b) % R, (b-a) % R) <= k
    real = Fr(sum(ker[d] for s in range(M) for d in ker if cons(q(s, R), q((s+d) % M, R))), M*KZ)
    false = Fr(sum(1 for a in range(M) for b in range(M) if cons(q(a, R), q(b, R))), M*M)
    return real, false, real/false
rows = []
for R, k in [(24, 4), (12, 2), (8, 1), (24, 1), (8, 0), (6, 1), (4, 0), (24, 2), (12, 1)]:
    r, f, lr = stats(R, k); rows.append((R, k, r, f, lr))
    print(f"R{R:2d} k{k}: real {float(r):.3f} false {float(f):.3f} LR {float(lr):.2f}")
by = {(R, k): (f, lr) for R, k, r, f, lr in rows}
# equal-f groups: f=3/8 -> (24,4)? 9/24; (12,2)? 5/12; (8,1) 3/8 ; f=1/8 -> (24,1) 3/24,(8,0) 1/8
g1 = [by[(24, 4)][1], by[(8, 1)][1]]          # both f = 3/8
g2 = [by[(24, 1)][1], by[(8, 0)][1]]          # both f = 1/8
g3 = [by[(24, 2)][1], by[(12, 1)][1]]         # both f = 5/24 vs 3/12 (near)
def spread(g): return float(max(g)/min(g) - 1)
print(f"equal-f spreads: f=3/8 {spread(g1):.3f}; f=1/8 {spread(g2):.3f}; f~0.21-0.25 {spread(g3):.3f}")
def sil(c, n, prior=Fr(3, 10)): return prior/(prior + (1-prior)*(1-c)**n)
s1, s2 = sil(Fr(9, 10), 2), sil(Fr(3, 10), 3)
print(f"silence c0.9 n2 {float(s1):.3f}; c0.3 n3 {float(s2):.3f}; c0.9 n1 {float(sil(Fr(9,10),1)):.3f}")
checks = [spread(g1) < 0.15 and spread(g2) < 0.15, by[(8, 0)][1] > by[(8, 1)][1], s1 >= Fr(85, 100), s2 < Fr(8, 10)]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4 predictions held; equal-f LR spread "
      f"{spread(g1):.3f} (f=3/8) {spread(g2):.3f} (f=1/8); R8 k0 {float(by[(8,0)][1]):.2f} vs k1 "
      f"{float(by[(8,1)][1]):.2f}; silence c0.9 n2 {float(s1):.3f}, c0.3 n3 {float(s2):.3f}")
