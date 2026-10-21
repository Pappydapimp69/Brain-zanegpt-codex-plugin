# Composes the severe-harm-needs-distance / mild-needs-closeness dial, escalation-needs-matching-distance
# and my decaying-safe-cue sandbox. Compare, for the flat-at-ceiling schedule and a rule-of-three one:
#   A) fixed grounded d=0.3 + cue c0=0.7 decaying by r per beat (r in 1.0, 0.6, 0.3)
#   B) matched distance (d = severity), no cue
#   C) matched distance + decaying cue
# PREDICTION (before run): B beats A at every r (matched wins by >= 1.0 on flat), C == B within 0.01
# (cue inert when distance matches), and A's gap to B widens as r falls (monotone).
import math
C = 10.0
SCHED = {"flat": [10]*6, "three": [2,6,10,10,10,10]}
def score(seq, d_mode, r, c0=0.7):
    X = tot = 0.0
    for k, I in enumerate(seq):
        c = c0 * r**k
        d = 0.3 if d_mode == "fixed" else (I/C - 0.2 if d_mode == "off" else I/C)
        g = math.exp(-((d - I/C)/0.25)**2); g = g + c*(1-g)
        tot += math.exp(-0.2*X)*(I/C)*g; X += 1/(1+I/5)
    return tot
res = {}
for name, s in SCHED.items():
    B = score(s, "matched", 0.0, 0.0)
    for r in (1.0, 0.6, 0.3):
        A = score(s, "fixed", r); Cc = score(s, "matched", r)
        res[(name, r)] = (A, B, Cc)
        print(f"{name:5s} r={r}: fixed+cue {A:.2f} matched {B:.2f} matched+cue {Cc:.2f}")
flat_gaps = [res[("flat", r)][1] - res[("flat", r)][0] for r in (1.0, 0.6, 0.3)]
# BREAK: matching is imperfect (distance 0.2 too close at every beat). The built-in algebra no longer gives g=1,
# so a permanent cue (r=1.0) should now help: off+cue > off alone, and still below perfect matching.
off0 = score(SCHED["flat"], "off", 0.0, 0.0); off1 = score(SCHED["flat"], "off", 1.0)
print(f"imperfect match (-0.2): no cue {off0:.2f}, permanent cue {off1:.2f}, perfect {res[('flat',1.0)][1]:.2f}")
ok = (all(g >= 1.0 for g in flat_gaps) and all(abs(v[2]-v[1]) < 0.01 for v in res.values())
      and flat_gaps[0] < flat_gaps[1] < flat_gaps[2] and off1 > off0 + 0.3 and off1 < res[("flat",1.0)][1])
print(f"RESULT: {'PASS' if ok else 'FAIL'} flat gap matched minus fixed+cue at r 1.0/0.6/0.3: {[round(g,2) for g in flat_gaps]}; perfect matching makes the cue inert by construction; imperfect match {off0:.2f} -> {off1:.2f} with cue")
