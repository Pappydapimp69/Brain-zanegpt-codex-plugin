"""Rebuild of seven E30 (rescue window measured from the feet abandons by
accident; camp/sleep rule only on deliberate moves) with NON-UNIFORM plan
weights. Own fixture: 6 days (not 4), actions stay / scout 1 / scout 2 /
scout 3 / move camp (+1), member lost at 3 areas from where the rule
measures (not 2). Plans are i.i.d. daily choices under four player profiles;
exact enumeration of all 5^6 plans with weights. A loss on a move day is
deliberate, any other day accidental.
PREDICTIONS (written before running):
 P1 camp rule: 0 accidental losses under every profile
 P2 feet rule: accidental share >= 0.40 under every profile, including a
    'mover' who rarely scouts far
 P3 feet rule loses more plans than the camp rule under every profile
"""
from itertools import product
from fractions import Fraction as Fr
ACT = ["stay", "s1", "s2", "s3", "move"]; L = 3; D = 6
profiles = {
  "uniform":  [Fr(1, 5)]*5,
  "cautious": [Fr(4, 10), Fr(3, 10), Fr(15, 100), Fr(5, 100), Fr(1, 10)],
  "explorer": [Fr(1, 10), Fr(1, 10), Fr(2, 10), Fr(4, 10), Fr(2, 10)],
  "mover":    [Fr(3, 10), Fr(2, 10), Fr(5, 100), Fr(1, 100), Fr(44, 100)],
}
def lose(plan, rule):
    camp = 0
    for day, a in enumerate(plan):
        if a == "move": camp += 1
        feet = camp + (int(a[1]) if a in ("s1", "s2", "s3") else 0)
        where = feet if rule == "feet" else camp
        if where >= L:
            return "deliberate" if a == "move" else "accidental"
    return None
out = {}
for name, w in profiles.items():
    r = {}
    for rule in ("camp", "feet"):
        lost = acc = Fr(0)
        for plan in product(range(5), repeat=D):
            p = Fr(1)
            for i in plan: p *= w[i]
            res = lose([ACT[i] for i in plan], rule)
            if res: lost += p; acc += p if res == "accidental" else 0
        r[rule] = (lost, acc/lost if lost else Fr(0))
    out[name] = r
    print(f"{name:9s} camp lost {float(r['camp'][0]):.3f} acc {float(r['camp'][1]):.3f} | "
          f"feet lost {float(r['feet'][0]):.3f} acc {float(r['feet'][1]):.3f}")
checks = [all(out[n]['camp'][1] == 0 for n in out), all(out[n]['feet'][1] >= Fr(4, 10) for n in out),
          all(out[n]['feet'][0] > out[n]['camp'][0] for n in out)]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3 predictions held; feet accidental share "
      + ", ".join(f"{n} {float(out[n]['feet'][1]):.3f}" for n in out) + "; camp accidental 0 in all")
