# Toy: film "cold open" (show the payoff moment first) as a variant axis, ranked on IPM vs IPM*D1.
# Assumption: a cold open lifts IPM by promising a payoff, but D1 falls with how far the promise
# exceeds what the game delivers (promise gap). Prediction written before run:
# IPM-only picks the max-promise variant; IPM*D1 picks a mid-promise one; with flat D1 both agree;
# BREAK case: if D1 penalty is cliffed beyond gap 0.5, IPM*D1 picks the cliff edge, not the middle.
import itertools
def ipm(h, promise): return 10*h*(1+0.8*promise)
def d1(promise, delivered, pen, cliff=None):
    gap = max(0.0, promise-delivered)
    if cliff is not None and gap > cliff: return 0.05
    return max(0.05, 0.30 - pen*gap)
hooks = [0.8, 1.0, 1.2]; promises = [0.0,0.25,0.5,0.75,1.0]; delivered = 0.5
def best(score, vs): return max(vs, key=score)
V = list(itertools.product(hooks, promises))
res = {}
for name, pen, cliff in [("linear",0.3,None),("flat",0.0,None),("cliff",0.3,0.25),("steep",0.8,None)]:
    a = best(lambda v: ipm(*v), V)
    b = best(lambda v: ipm(v[0],v[1])*d1(v[1],delivered,pen,cliff), V)
    res[name] = (a, b)
    print(name, "IPM->", a, "IPM*D1->", b)
ok = (res["linear"][0][1]==1.0 and res["linear"][1][1]<1.0
      and res["flat"][0]==res["flat"][1]
      and res["cliff"][1][1]==0.75 and res["steep"][1][1]<=0.5)
# prediction check on specifics
print("linear D1-pick promise", res["linear"][1][1], "cliff pick promise", res["cliff"][1][1], "steep", res["steep"][1][1])
print("RESULT: %s IPM->promise %.2f; IPM*D1 linear %.2f, steep %.2f, cliff %.2f, flat agrees %s" % (
  "PASS" if ok else "FAIL", res["linear"][0][1], res["linear"][1][1], res["steep"][1][1], res["cliff"][1][1], res["flat"][0]==res["flat"][1]))
