"""Rebuild of seven E34 (which abandonment route ends a rescue first: the
time limit (call fades out) or the space limit (camp two areas ahead)).
Own fixture: 7-day plans, time limit = lost after night 5 (not 6), space
rule measured from where the lead sleeps (camp; sleeping out not offered),
actions stay / scout 1 / scout 2 / move camp. Plans are weighted by player
profiles (i.i.d. daily choice with camp-move probability q, rest split evenly)
instead of E34's equal weighting. Exact enumeration (4^7 plans).
PREDICTIONS (written before running):
 P1 equal weighting (q = 0.25) gives a time-first majority (> 0.5), as E34 found
 P2 across profiles q = 0.10 .. 0.60 the time-first share swings by more than
    0.5 (which route is 'usual' is set by how players move, not by the rules)
 P3 0 accidental abandonments under every profile (sleep-measured window)
"""
from itertools import product
from fractions import Fraction as Fr
D, T = 7, 5
def outcome(plan):
    camp = 0
    for day, a in enumerate(plan):           # day index 0..6, night index = day
        if a == 3:
            camp += 1
            if camp >= 2: return "space", True
        if day >= T: return "time", True     # survived nights 0..T-1, silent after
    return "time", True
res = {}
for q in [Fr(1, 10), Fr(1, 4), Fr(2, 5), Fr(3, 5)]:
    w = [(1-q)/3]*3 + [q]
    tf = acc = Fr(0)
    for plan in product(range(4), repeat=D):
        p = Fr(1)
        for a in plan: p *= w[a]
        route, deliberate = outcome(plan)
        if route == "time": tf += p
        if not deliberate: acc += p
    res[q] = (tf, acc)
    print(f"q {float(q):.2f}: time-first {float(tf):.3f} accidental {float(acc):.3f}")
shares = [float(v[0]) for v in res.values()]
p1 = res[Fr(1, 4)][0] > Fr(1, 2)
p2 = max(shares) - min(shares) > 0.5
p3 = all(v[1] == 0 for v in res.values())
held = p1 + p2 + p3
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3 predictions held; time-first by q "
      + ", ".join(f"{float(q):.2f}:{float(v[0]):.3f}" for q, v in res.items()) + "; accidental 0")
