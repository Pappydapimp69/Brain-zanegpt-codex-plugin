"""Prediction (before run): with 16 slots per video (10 kit + comic-engine slot + 5 other variable slots, all variable
slots fresh except the engine drawn from 8), a fixed kit gives mean pair similarity
(10 + P(same engine))/16: engine-first round-robin on 10 ideas -> 0.6278 (2 same-engine pairs of 45), topic-first
random -> about 0.6328 (P=1/8). So the difference between assignment methods is under 0.01,
while rotating 3 kit assets drops the score by more than 0.10 (to <= 0.5). Also, a 10-cell batch from
the 30-cell slot machine contains one of the 6 cells with the mislabelled axis name with probability 1-C(24,10)/C(30,10)=0.935."""
import itertools, math
from random import Random
def sim(vs):
    tot = 0; n = 0
    for a, b in itertools.combinations(vs, 2):
        tot += sum(x == y for x, y in zip(a, b)) / len(a); n += 1
    return tot / n
def batch(k, engines, rot, uid):
    out = []
    for i in range(k):
        kit = [0] * 10
        for j in range(rot): kit[j] = (i % 6) + 1          # rotated kit assets drawn from a pool of 6 variants
        out.append(kit + [engines[i]] + [uid + i * 10 + s for s in range(5)])   # unique values for fresh slots
    return out
def avg(k, rot, method, seeds=300):
    rng = Random(7); s = 0
    for z in range(seeds):
        eng = [i % 8 for i in range(k)] if method == "first" else [rng.randrange(8) for _ in range(k)]
        s += sim(batch(k, eng, rot, 1000))
    return s / seeds
ef0, tf0 = avg(10, 0, "first"), avg(10, 0, "topic")
ef3, tf3 = avg(10, 3, "first"), avg(10, 3, "topic")
p_mis = 1 - math.comb(24, 10) / math.comb(30, 10)
print(round(ef0, 4), round(tf0, 4), round(ef3, 4), round(tf3, 4), round(p_mis, 3))
ok = (abs(ef0 - 0.6278) < .002 and abs(tf0 - ef0) < .01 and ef0 - ef3 > .10 and ef3 <= .5 and abs(p_mis - .935) < .001)
print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"fixed kit: engine-first {ef0:.4f} vs topic-first {tf0:.4f} (diff {abs(tf0-ef0):.4f}); +3 kit rotated {ef3:.4f}/{tf3:.4f}; P(mislabelled-axis cell in 10-cell batch)={p_mis:.3f}")
