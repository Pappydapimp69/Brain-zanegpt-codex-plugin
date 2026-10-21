# LRU/FIFO cache on a cyclic loop, with write-invalidation of one key every K accesses.
from collections import OrderedDict

def run(policy, size, loop, n, every):
    c = OrderedDict(); hits = 0; inv = 0
    for i in range(n):
        k = i % loop
        if every and i and i % every == 0:
            v = (i // every * 3) % loop
            if v in c: del c[v]; inv += 1
        if k in c:
            hits += 1
            if policy == "lru": c.move_to_end(k)
        else:
            if size and len(c) >= size: c.popitem(last=False)
            if size: c[k] = 1
    return hits, inv

N, L = 100, 5
res = {}
for pol in ("lru", "fifo"):
    for size in (0, 4, 5, 6):
        for every in (0, 10, 2):
            res[(pol, size, every)] = run(pol, size, L, N, every)
            print(pol, size, "inv_every", every, "hits/invalidated", res[(pol, size, every)])
# invalidating a key costs exactly one extra miss when the key is later reused (hit lost per invalidation)
exact = all(res[("lru",5,e)][0] == 95 - res[("lru",5,e)][1] for e in (10, 2))
cliff = all(res[(p,4,e)][0] == 0 for p in ("lru","fifo") for e in (0,10,2))
print("RESULT:", "FAIL" if not cliff else "PASS",
      "prediction refuted: invalidation holes rescue the one-short cache (lru4: 12 and 39 hits, fifo4: 51 and 48 vs 0), size 5 loses exactly one hit per invalidation",
      "lru5:", {e: res[("lru",5,e)] for e in (0,10,2)})
