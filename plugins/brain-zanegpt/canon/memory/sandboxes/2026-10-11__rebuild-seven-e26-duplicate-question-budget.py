"""Rebuild of seven E26 (two at the fire: ask one vs ask both; is 1-of-2 accuracy
derived). Own fixture: a day has 8 binary facts, the fake bends exactly one
(uniform), a question covers 3 facts, memory per fact: recalls true value m,
blank otherwise; each fact's true value is an unknown fair bit; variant with a wrongly-sure memory w (recalls the flipped
value). The player decides BAYES-OPTIMALLY from everything observed: exact
enumeration over (who is fake, bent fact, memory states), group worlds by the
observation, pick the more probable identity. Exact fractions.
PREDICTIONS (written before running):
 P1 ask-both accuracy = 1/2 + 1/2*c*m (c = 3/8, m = 0.7) -> 0.631
 P2 ask-ONE, read Bayes-optimally (a match with memory is evidence too), is
    EQUAL to ask-both: the edge ratio is 1.0, not E26's 2.0
 P3 with no memory both budgets are exactly 1/2
 P4 three at the fire, one fake, all asked, no memory: majority beats 1/3
 P5 with wrongly-sure memory (w = 0.1, m = 0.6) ask-both is still no better
    than ask-one read optimally (ratio <= 1.05)
"""
from fractions import Fraction as Fr
from itertools import product
from collections import defaultdict
NF, COV = 8, (0, 1, 2)
def accuracy(asked, m, w, cast=2, use_mem=True):
    obs = defaultdict(lambda: defaultdict(Fr))
    states = [("t", m), ("f", w), ("b", 1-m-w)] if use_mem else [("b", Fr(1))]
    for fake in range(cast):
        for bent in range(NF):
            pw = Fr(1, cast*NF)
            for truth in product((0, 1), repeat=len(COV)):
              for mem in product(states, repeat=len(COV)):
                p = pw / 2**len(COV)
                for _, q in mem: p *= q
                if p == 0: continue
                mview = tuple(None if s == "b" else (t if s == "t" else 1-t)
                              for (s, _), t in zip(mem, truth))
                ans = tuple(tuple((1-t) if (who == fake and f == bent) else t
                                  for f, t in zip(COV, truth)) for who in asked)
                obs[(mview, ans)][fake] += p
    return sum(max(d.values()) for d in obs.values())
m, w = Fr(7, 10), Fr(0)
one = accuracy((0,), m, w); both = accuracy((0, 1), m, w)
c = Fr(len(COV), NF)
print(f"ask one {float(one):.4f}; ask both {float(both):.4f}; formula {float(Fr(1,2)+Fr(1,2)*c*m):.4f}")
nm1 = accuracy((0,), m, w, use_mem=False); nm2 = accuracy((0, 1), m, w, use_mem=False)
three = accuracy((0, 1, 2), m, w, cast=3, use_mem=False)
m2, w2 = Fr(6, 10), Fr(1, 10)
one_w = accuracy((0,), m2, w2); both_w = accuracy((0, 1), m2, w2)
print(f"no memory: one {float(nm1):.3f} both {float(nm2):.3f}; three-at-fire no memory {float(three):.3f}")
print(f"wrong-sure memory: one {float(one_w):.4f} both {float(both_w):.4f}")
r = (both - Fr(1, 2)) / (one - Fr(1, 2))
rw = (both_w - Fr(1, 2)) / (one_w - Fr(1, 2))
checks = [both == Fr(1, 2)+Fr(1, 2)*c*m, one == both, nm1 == nm2 == Fr(1, 2), three > Fr(1, 3), rw <= Fr(105, 100)]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 5 else 'FAIL'} {held}/5 predictions held; ask-one(optimal) {float(one):.4f} "
      f"ask-both {float(both):.4f} edge ratio {float(r):.2f}; wrong-sure ratio {float(rw):.2f}; "
      f"three no-memory {float(three):.3f}")
