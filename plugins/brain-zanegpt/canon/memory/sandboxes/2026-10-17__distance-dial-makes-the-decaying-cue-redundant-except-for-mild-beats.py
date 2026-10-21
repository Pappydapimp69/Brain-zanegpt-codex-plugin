# Composes ideas:COMEDY/severe-harm-needs-distance-mild-harm-needs-closeness (ideal distance d* = I/C: severe far,
# mild close), escalation-needs-matching-distance/E1 (fixed d=0.3 kills go-big; matched distance restores it) and
# decaying-safe-cue-flips-go-big-back-to-mild/E1 (a cue habituates as c0*r**age and covers g' = g + c*(1-g)).
# Same escalation model as those sandboxes: h=exp(-0.2X), X += 1/(1+I/5), response h*I/C, benign gate
# g=exp(-((d-I/C)/0.25)^2). Framings: close (d=0.3), far (d=0.9), matched (d=I/C). Cue c0=0.7, r in {1.0,0.6,0.3}.
# PREDICTION (before run): (1) under matched distance the cue changes the total by < 0.01 (g is already 1);
# (2) under far framing the kernel's second half holds: the mild schedule scores < 0.05, flat wins;
# (3) a decaying cue (r=0.6) lifts the mild schedule under far framing by more than 3x but not above flat's score;
# BREAK: under close framing with r=0.3 the cue still lets mild beat flat (cue only helps when it lasts).
import math
C = 10.0
SCHED = {"flat": [10]*6, "three": [2,6,10,10,10,10], "mild": [3,3.5,4,4,4.5,5], "linear": [2+8*k/5 for k in range(6)]}
def score(seq, framing, r=None, c0=0.7):
    X = tot = 0.0
    for k, I in enumerate(seq):
        d = {"close": 0.3, "far": 0.9, "matched": I/C}[framing]
        g = math.exp(-((d - I/C)/0.25)**2)
        c = 0.0 if r is None else c0 * r**k
        g = g + c*(1-g)
        tot += math.exp(-0.2*X) * (I/C) * g
        X += 1/(1+I/5)
    return tot
res = {}
for f in ("close", "far", "matched"):
    for r in (None, 1.0, 0.6, 0.3):
        sc = {n: score(s, f, r) for n, s in SCHED.items()}
        res[(f, r)] = sc
        print(f"{f:7s} cue r={r}: " + "  ".join(f"{n}={v:.2f}" for n, v in sc.items()) + f"  best={max(sc, key=sc.get)}")
best = lambda f, r: max(res[(f, r)], key=res[(f, r)].get)
p1 = max(abs(res[("matched", r)][n] - res[("matched", None)][n]) for r in (1.0, 0.6, 0.3) for n in SCHED)
p2 = res[("far", None)]["mild"] < 0.05 and best("far", None) == "flat"
lift = res[("far", 0.6)]["mild"] / max(res[("far", None)]["mild"], 1e-9)
p3 = lift > 3 and res[("far", 0.6)]["mild"] < res[("far", 0.6)]["flat"]
brk = best("close", 0.3)
print(f"matched max cue effect {p1:.4f}; far mild no-cue {res[('far', None)]['mild']:.3f}; far mild lift at r0.6 {lift:.1f}x; close r0.3 best {brk}")
ok = p1 < 0.01 and p2 and p3
print(f"RESULT: {'PASS' if ok else 'FAIL'} matched-distance cue effect {p1:.4f} (redundant); far framing mild {res[('far', None)]['mild']:.3f} -> {res[('far', 0.6)]['mild']:.2f} with r0.6 cue ({lift:.1f}x, flat still ahead {res[('far', 0.6)]['flat']:.2f}); close r0.3 winner {brk}")
