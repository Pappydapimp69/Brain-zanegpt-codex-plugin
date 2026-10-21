"""Rebuild of seven E23 with a different fixture and a different noise model.
Fixture: missing prior 0.25 (not 0.15), real call rate 0.7 (not 0.9). The player
hears 8 directions. A real member sits at a fixed true bearing; each call is
true bearing + Gaussian noise sigma 25 deg, rounded to the nearest of 8
directions (so calls share the true bearing and are NOT independent across
pairs). False calls: uniform bearing. Consistent = same or adjacent direction.
All exact by 1-degree numerical integration (deterministic).
PREDICTIONS (written before running):
 P1 F = 0 gives posterior exactly 1.0
 P2 F for posterior 0.6 equals prior*c*(1/0.6-1)/(1-prior) (~0.156 here, so
    'about 0.1' does not transfer across priors - structural form does)
 P3 a consistent pair at that F stays under 0.85 (consistency is not proof)
 P4 real pairs look consistent more often than false pairs (0.375)
 P5 over 3 nights, real calls: P(both pairs consistent) > P(pair)^2 (pairs are
    positively correlated); false calls: exactly P(pair)^2
"""
import math
PRIOR, CALL, SIG = 0.25, 0.7, 25.0
def q8(deg): return int(((deg % 360) + 22.5) // 45) % 8
# distribution of heard direction offset (heard - true-direction) given true bearing t
noise = [math.exp(-0.5*(d/SIG)**2) for d in range(-180, 181)]
Z = sum(noise); noise = [w/Z for w in noise]
def heard_dist(t):
    h = [0.0]*8
    for i, d in enumerate(range(-180, 181)):
        h[q8(t+d)] += noise[i]
    return h
def cons(a, b): return min((a-b) % 8, (b-a) % 8) <= 1
p_pair = p_trip = 0.0
for t in range(360):
    h = heard_dist(t)
    pp = sum(h[a]*h[b] for a in range(8) for b in range(8) if cons(a, b))
    pt = sum(h[a]*h[b]*h[c] for a in range(8) for b in range(8) for c in range(8)
             if cons(a, b) and cons(b, c))
    p_pair += pp/360; p_trip += pt/360
f_pair = sum(1 for a in range(8) for b in range(8) if cons(a, b))/64
f_trip = sum(1 for a in range(8) for b in range(8) for c in range(8) if cons(a, b) and cons(b, c))/512
def post(F): return PRIOR*CALL/(PRIOR*CALL + (1-PRIOR)*F)
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo+hi)/2
    if post(mid) > 0.6: lo = mid
    else: hi = mid
Fs = hi; formula = PRIOR*CALL*(1/0.6-1)/(1-PRIOR)
def post_pair(F):
    r = PRIOR*CALL*CALL*p_pair; f = (1-PRIOR)*F*F*f_pair
    return r/(r+f)
pp = post_pair(Fs)
print(f"post F=0 {post(0):.3f}; F* {Fs:.4f} formula {formula:.4f}; consistent-pair post {pp:.3f}")
print(f"real pair {p_pair:.3f} trip {p_trip:.3f} pair^2 {p_pair**2:.3f}; false pair {f_pair:.3f} trip {f_trip:.4f} pair^2 {f_pair**2:.4f}")
lr_true = p_trip/f_trip; lr_ind = (p_pair/f_pair)**2
print(f"3-night LR true {lr_true:.3f} vs independent-pairs {lr_ind:.3f}")
checks = [abs(post(0)-1) < 1e-12, abs(Fs-formula) < 1e-6 and Fs > 0.13, pp < 0.85,
          p_pair > f_pair, p_trip > p_pair**2 + 1e-6 and abs(f_trip - f_pair**2) < 1e-12]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 5 else 'FAIL'} {held}/5 predictions held; F* {Fs:.3f}; pair post {pp:.3f}; "
      f"real pair {p_pair:.3f} vs false {f_pair:.3f}; 3-night LR true {lr_true:.2f} vs indep {lr_ind:.2f}")
