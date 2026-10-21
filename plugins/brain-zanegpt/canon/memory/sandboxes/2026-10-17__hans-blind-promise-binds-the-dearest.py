"""Hans My Hedgehog (The StoryTeller, from Grimm KHM 108, ATU 441). The lost king promises Hans "the first thing to greet
him" at home, expecting his dog; his daughter greets him. Deterministic, stdlib, exact fractions.
Household: each greeter has a value to the king and a time to reach him in each of its states (None = cannot come).
Every combination of states is enumerated with integer weights; the first to arrive is bound by the promise.
Expected cost = sum over combinations of weight share x value of whoever arrives first (0 if nobody qualifies)."""
from fractions import Fraction as F
from itertools import product
VALUE = {"dog": 1, "servant": 5, "daughter": 100}
KIND = {"dog": "animal", "servant": "person", "daughter": "person"}
def household(daughter_w, dog_states=None, servant_states=None):
    dog_states = dog_states or [("loose", 2, 1), ("chained", None, 1)]          # (state, time, weight)
    servant_states = servant_states or [("at work", F(5, 2), 1)]
    return {"dog": dog_states,
            "servant": servant_states,
            "daughter": [("window", 1, daughter_w[0]), ("chapel", 3, daughter_w[1]), ("away", None, daughter_w[2])]}
def outcome(house, qualifies=lambda g: True):
    names = list(house)
    total, share = 0, {n: F(0) for n in names}
    combos = list(product(*[house[n] for n in names]))
    for combo in combos:
        w = 1
        for (_, _, wi) in combo:
            w *= wi
        total += w
    cost = F(0)
    for combo in combos:
        w = 1
        for (_, _, wi) in combo:
            w *= wi
        if w == 0:
            continue
        arrivals = [(t, n) for n, (_, t, _) in zip(names, combo) if t is not None and qualifies(n)]
        if arrivals:
            t, first = min(arrivals)
            share[first] += F(w, total)
            cost += F(w, total) * VALUE[first]
    return share, cost
LONG, SHORT = (2, 1, 0), (0, 1, 1)                  # lost for days: she watches from the window; a day's hunt: she does not
imagined = VALUE["dog"]
sh1, c1 = outcome(household(LONG))
sh2, c2 = outcome(household(SHORT))
c3 = F(VALUE["dog"])                                  # named promise: "my dog"
_, c4 = outcome(household(LONG), lambda g: KIND[g] == "animal")
_, c5 = outcome(household(LONG), lambda g: KIND[g] == "person")
sh7, c7 = outcome(household(LONG))                    # a day's hunt, but she watches from the window anyway: same weights
_, c8 = outcome(household((1, 0, 0), dog_states=[("chained", None, 1)], servant_states=[("away", None, 1)]))
_, b1 = outcome(household(LONG, dog_states=[("waits at the gate", 0, 1)]))
fmt = lambda s: {k: str(v) for k, v in s.items()}
print(f"1) lost for days (canon): first-greeter shares {fmt(sh1)}, expected cost {float(c1):.2f} vs imagined {imagined}")
print(f"2) a day's hunt: first-greeter shares {fmt(sh2)}, expected cost {float(c2):.2f}")
print(f"3) named promise 'my dog': cost {float(c3):.2f}")
print(f"4) class promise 'the first animal to greet me': expected cost {float(c4):.2f}")
print(f"5) class promise 'the first person to greet me': expected cost {float(c5):.2f}")
print(f"6) a day's hunt but she watches from the window anyway: expected cost {float(c7):.2f}")
print(f"7) she always watches, dog chained, servant away: expected cost {float(c8):.2f}")
print(f"BREAK) dog always waits at the gate: expected cost {float(b1):.2f} vs imagined {imagined}")
ok = (sh1["daughter"] == F(2, 3) and abs(float(c1) - 67.67) < 0.01 and c2 == 3 and sh2["daughter"] == 0
      and c3 == 1 and c4 == F(1, 2) and abs(float(c5) - 68.33) < 0.01 and c7 == c1 and c8 == 100 and b1 == 1)
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"the blind promise made while lost for days costs {float(c1):.2f} "
      f"against an imagined {imagined} because the daughter is first {sh1['daughter']} of the time and worth 100; after a "
      f"day's hunt it costs {float(c2):.2f}; naming the dog caps it at {float(c3):.2f}, 'first animal' at {float(c4):.2f}, "
      f"but 'first person' still costs {float(c5):.2f}; a day's hunt with her watching anyway costs {float(c7):.2f} "
      f"(her watching drives it, not the absence itself) and with nobody else free it reaches {float(c8):.2f}; BREAK: a dog that always waits at the gate makes it cost {float(b1):.2f}")
