"""Sandbox: Road-Runner rule card (write-the-rules-before-the-gags) + per-beat benign-violation check + matched-distance escalation.
Hand-written model, no real audience: it tests how the three rules interact, not whether people laugh.
Candidate gag = (source in tool/gravity/self/outside, harm 0-3, humiliation 0-3). Violation v = harm + 2 if source is outside else harm.
Beat is 'funny' iff v >= 1 and v <= benign, benign = distance + humiliation//2  (distance = cartoon/grounded framing 0-3).
Rule card (Jones): drop outside-force sources and any gag with harm > humiliation.
Schedule: 5 beats with target violation 1..5 (go-big escalation); each picks the pool gag whose v is closest to the target (ties: lowest index).
PREDICTION (before run): at distance 1 the unfiltered pool scores <= 2/5 funny, the rule-card pool >= 3/5 (the card helps);
at distance 3 the rule-card pool scores 5/5 is NOT expected: its violations stop at 3, so beats 4-5 under-escalate - the card caps escalation (hidden assumption: more rules = safer without cost);
FIRST RUN REFUTED TWO PARTS: card at distance 1 scored 2/5 (not >=3) and at distance 3 scored 5/5 (the cap did not cost funny beats, it flattened escalation: v 1,2,3,3,3). Corrected expectation checked below: card >= raw at every distance, card gains 3 beats at distance 2, card escalates strictly on only 2 of 4 steps vs raw 4 of 4.
BREAK: at distance 0 both pools score <= 1/5, so the card cannot substitute for distance."""
import itertools

SRC = ["tool", "gravity", "self", "outside"]
POOL = [(s, h, m) for s, h, m in itertools.product(SRC, range(4), range(4))]

def v(g): return g[1] + (2 if g[0] == "outside" else 0)
def funny(g, d): return 1 <= v(g) <= d + g[2] // 2
def card(g): return g[0] != "outside" and g[1] <= g[2]

def schedule(pool, d):
    out = []
    for target in range(1, 6):
        best = min(range(len(pool)), key=lambda i: (abs(v(pool[i]) - target), i))
        out.append(pool[best])
    return out

res = {}
for d in (0, 1, 2, 3):
    for name, pool in (("raw", POOL), ("card", [g for g in POOL if card(g)])):
        sch = schedule(pool, d)
        res[(name, d)] = sum(funny(g, d) for g in sch)
        print("distance", d, name, "funny", res[(name, d)], "of 5, v", [v(g) for g in sch])
def steps(pool): 
    vs = [v(g) for g in schedule(pool, 0)]
    return sum(b > a for a, b in zip(vs, vs[1:]))
cp = [g for g in POOL if card(g)]
ok = (all(res[("card", d)] >= res[("raw", d)] for d in range(4)) and res[("card", 2)] - res[("raw", 2)] == 3
      and res[("raw", 0)] == res[("card", 0)] == 0 and steps(cp) == 2 and steps(POOL) == 4)
print("escalation steps raw", steps(POOL), "card", steps(cp))
print("RESULT: %s funny/5 raw d0..3 %s, card d0..3 %s" % ("PASS" if ok else "FAIL",
      [res[("raw", d)] for d in range(4)], [res[("card", d)] for d in range(4)]))
