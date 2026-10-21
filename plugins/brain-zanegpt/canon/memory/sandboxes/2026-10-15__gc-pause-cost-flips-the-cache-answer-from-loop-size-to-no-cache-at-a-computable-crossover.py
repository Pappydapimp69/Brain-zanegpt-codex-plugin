# Sandbox: loop-sized cache (cache-size-sweep E1) + latency costs (hit 1, miss 100)
# + garbage-collection tradeoff (pause ~ live set; frequency ~ allocation / headroom).
# Trace: 1000 accesses cycling 5 items. LRU. Cost = hits*1 + misses*100 + GC pauses.
# GC: every ALLOC_PER_GC accesses a stop-the-world pause of GCSLOT * live_slots.
# PREDICTION (before run): at small GC cost the best size stays 5; sizes 1-4 are
# never best (0 hits, only GC cost); best size flips to 1 (or 0) when GCSLOT exceeds
# a crossover I expect near 95*99/(slots*collections) = 9405*10/(5*20)... computed below.
from collections import OrderedDict
T, LOOP, ALLOC_PER_GC = 1000, 5, 50
def hits_for(size):
    c = OrderedDict(); h = 0
    for i in range(T):
        k = i % LOOP
        if k in c: c.move_to_end(k); h += 1
        else:
            if size and len(c) >= size: c.popitem(last=False)
            if size: c[k] = 1
    return h
def cost(size, gcslot):
    h = hits_for(size); gcs = T // ALLOC_PER_GC
    return h * 1 + (T - h) * 100 + gcs * gcslot * size
sizes = range(0, 9)
def best(g): return min(sizes, key=lambda s: cost(s, g))
rows = {g: best(g) for g in (0, 1, 10, 50, 90, 94, 96, 200)}
print("best size by GC cost per live slot:", rows)
# analytic crossover: size 5 vs size 0
saved = cost(0, 0) - cost(5, 0)                 # miss savings with no GC
gcs = T // ALLOC_PER_GC
cross = saved / (gcs * 5)
print(f"saving {saved}, collections {gcs}, crossover GC cost per slot {cross:.2f}")
mid = [best(g) for g in (0, 1, 10, 50, 90)]
never_small = all(best(g) not in (1, 2, 3, 4) for g in range(0, 400))
# BREAK scenario: allocation-heavy program, a collection every 2 accesses
ALLOC_PER_GC = 2
cross2 = (cost(0, 0) - cost(5, 0)) / ((T // ALLOC_PER_GC) * 5)
flip2 = best(int(cross2) + 2)
print(f"allocation-heavy (GC every 2 accesses): crossover {cross2:.1f}, best size at {int(cross2)+2} per slot = {flip2}")
ALLOC_PER_GC = 50
ok = (flip2 == 0 and all(m == 5 for m in mid) and best(int(cross) - 1) == 5 and best(int(cross) + 2) == 0
      and never_small and cost(6, 10) > cost(5, 10))
print(f"RESULT: {'PASS' if ok else 'FAIL'} best size 5 until GC cost per slot passes {cross:.1f} (every 50 accesses) or {cross2:.1f} (every 2), then 0 (never 1-4); size 6 costs {cost(6,10)-cost(5,10)} more than 5 at GC 10")
