# Sandbox: composes COMEDY dark-humor distance dial (severe harm needs distance, mild needs
# closeness), escalation-needs-matching-distance/E1 (fixed d=0.3 flips go-big to mild) and
# rule-card-lifts-benign-ceiling/E1 (a card adds benign cover). Cover model (assumed, stated):
# g' = g + c*(1-g), c = card cover in [0,1]. Beat response = habituated level x g'.
# PREDICTION (before run): at fixed close d=0.3 a card with c=0.5 flips the winner from mild to
# flat-at-ceiling; at fixed FAR d=0.9 the card is not needed (flat already wins, ratio >= 0.8)
# but a mild-only schedule keeps under 0.4 of its ungated score even with c=0.5.
import math
C = 10.0
SCHED = {"flat": [10]*6, "three": [2,6,10,10,10,10], "mild": [3,3.5,4,4,4.5,5],
         "linear": [2+8*k/5 for k in range(6)]}
def score(seq, d_mode, c):
    X = tot = 0.0
    for I in seq:
        h = math.exp(-0.2*X); base = h*(I/C)
        d = d_mode if isinstance(d_mode, float) else I/C
        g = math.exp(-((d - I/C)/0.25)**2); g = g + c*(1-g)
        tot += base*g; X += 1/(1+I/5)
    return tot
def ungated(seq): return score(seq, "m", 1.0)       # g'=1
rows = {}
for name, d in (("close0.3", 0.3), ("far0.9", 0.9), ("matched", "m")):
    for c in (0.0, 0.5, 0.8):
        rows[(name, c)] = {n: score(s, d, c) for n, s in SCHED.items()}
        w = max(rows[(name, c)], key=rows[(name, c)].get)
        print(f"{name:9s} c={c}: winner {w:6s} " + " ".join(f"{n}={v:.2f}" for n, v in rows[(name, c)].items()))
win = lambda k: max(rows[k], key=rows[k].get)
mild_far0 = rows[("far0.9", 0.0)]["mild"] / ungated(SCHED["mild"])
mild_far_ratio = rows[("far0.9", 0.5)]["mild"] / ungated(SCHED["mild"])
flat_far_ratio = rows[("far0.9", 0.0)]["flat"] / ungated(SCHED["flat"])
inert = rows[("matched", 0.0)] == rows[("matched", 0.5)] == rows[("matched", 0.8)]
ok = (win(("close0.3", 0.0)) == "mild" and win(("close0.3", 0.5)) == "flat"
      and flat_far_ratio >= 0.8 and mild_far0 < 0.05 and mild_far_ratio >= 0.4 and inert)
print(f"RESULT: {'PASS' if ok else 'FAIL'} close d: c0 {win(('close0.3',0.0))} -> c0.5 {win(('close0.3',0.5))}; "
      f"far d=0.9 mild keeps {mild_far0:.2f} uncarded -> {mild_far_ratio:.2f} with c=0.5, flat keeps {flat_far_ratio:.2f} uncarded; matched framing: card inert={inert}")
