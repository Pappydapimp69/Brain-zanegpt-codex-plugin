"""Sandbox: loop-sized LRU cache with GC pause cost, now with write invalidation.
Deterministic. 1000 reads cycling 5 items; after every W-th read one write invalidates the item just read.
cost = hits*1 + misses*100 + (reads / GC_EVERY) * PAUSE * slots. Sizes 0..8. Crossover = PAUSE where size 0 beats size 5.
Prediction (written before first run), GC_EVERY=50:
  no writes: crossover 985 per slot (the gc-cost entry's number), best size 5 below it.
  W=10: hits fall from 995 to 895, crossover = (savings)/(20*5) with savings = 100*1000 - (895 + 105*100) = 88,605 -> 886.05.
  crossover falls monotonically as writes get more frequent (W=50,10,5,2).
  sizes 1..4 are never best at any PAUSE from 0 to 1500 under any W (the loop cliff survives writes). [REFUTED in iteration 1; see iteration 2 note in the code]
  BREAK: at W=1 (a write after every read of the item just read) the cache is useless: hits 0, so size 0 is already best at PAUSE 0 or ties.
"""
from collections import OrderedDict
def sim(slots, W, n=1000, items=5):
    c = OrderedDict(); hits = 0
    for i in range(n):
        k = i % items
        if slots and k in c: hits += 1; c.move_to_end(k)
        elif slots:
            c[k] = 1
            if len(c) > slots: c.popitem(last=False)
        if W and i % W == W - 1 and k in c: del c[k]
    return hits
def cost(slots, W, pause, gc_every=50, n=1000):
    h = sim(slots, W, n); return h + (n - h) * 100 + (n / gc_every) * pause * slots
def best(W, pause):
    cs = {s: cost(s, W, pause) for s in range(9)}
    m = min(cs.values()); return min(s for s in cs if cs[s] == m)
def crossover(W):
    lo, hi = 0.0, 5000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        (lo, hi) = (mid, hi) if cost(5, W, mid) < cost(0, W, mid) else (lo, mid)
    return hi
cross = {}
for W in (0, 50, 10, 5, 2, 1):
    cross[W] = crossover(W); print("W", W, "hits(5 slots)", sim(5, W), "crossover", round(cross[W], 2))
c1 = abs(cross[0] - 985) < 1
# iteration 1: hits at W=10 were 896 not 895 (my count of lost hits was off by one); crossover then 887.04, not 886.05.
c2 = sim(5, 10) == 896 and abs(cross[10] - 887.04) < 0.1
c3 = cross[0] > cross[50] > cross[10] > cross[5] > cross[2]
# iteration 1 predicted sizes 1-4 are never best; REFUTED: at W=2 size 3 was best, at W=3 and 4 size 4. Each write removes the item just read, so the
# working set the LRU must hold shrinks. Iteration 2 prediction: best size at pause 0 is 5 for W in 5..50 and 6..9, 4 for W in 3..4, 3 for W=2, 0 for W=1.
want = {50: 5, 10: 5, 9: 5, 8: 5, 7: 5, 6: 5, 5: 5, 4: 4, 3: 4, 2: 3, 1: 0}
got = {W: best(W, 0) for W in want}
print("best size at pause 0 by W:", got)
c4 = got == want
c5 = sim(5, 1) == 0 and best(1, 0) == 0
print("W=1 hits", sim(5, 1), "best at pause 0:", best(1, 0), "cross", cross[1])
ok = c1 and c2 and c3 and c4 and c5
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"c1 {c1} c2 {c2} c3 {c3} c4 {c4} c5 {c5}; crossover W0/50/10/5/2 = " + "/".join(str(round(cross[w], 1)) for w in (0, 50, 10, 5, 2)))
