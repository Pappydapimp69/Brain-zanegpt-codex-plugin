# Loop cache (LRU) under a toy generational GC, with and without invalidation.
# Each miss allocates one entry. Minor GC every NURSERY allocations promotes live entries (cost 1 each).
# Promoted entries that later die (evicted/invalidated) are old garbage; a major GC (cost = old size)
# runs when old garbage reaches MAJOR_AT.
from collections import OrderedDict
NURSERY, MAJOR_AT = 10, 20

def run(size, loop, n, every):
    cache = OrderedDict(); young = set(); old = set(); garbage = 0
    allocs = work = majors = hits = 0; nid = 0
    def kill(eid):
        nonlocal garbage
        if eid in old: old.discard(eid); garbage += 1
        else: young.discard(eid)
    for i in range(n):
        k = i % loop
        if every and i and i % every == 0:
            v = (i // every * 7) % loop
            if v in cache: kill(cache.pop(v))
        if k in cache:
            hits += 1; cache.move_to_end(k); continue
        if size and len(cache) >= size:
            _, e = cache.popitem(last=False); kill(e)
        if size:
            nid += 1; cache[k] = nid; young.add(nid)
        allocs += 1
        if allocs % NURSERY == 0:
            work += len(young); old |= young; young = set()
        if garbage >= MAJOR_AT:
            work += len(old) + garbage; majors += 1; garbage = 0
    return dict(hits=hits, work=work, majors=majors)

N, L = 600, 60
r = {}
for size in (0, 30, 59, 60):
    for every in (0, 10):
        r[(size, every)] = run(size, L, N, every)
        print("size", size, "inv_every", every, r[(size, every)])
# prediction: invalidation makes the exactly-sized cache (60) cost more GC work than without it,
# and 59 stays the costliest per hit-less configuration without invalidation.
inv_up = r[(60,10)]["work"] > r[(60,0)]["work"]
s59_worse = r[(59,0)]["work"] > r[(60,0)]["work"]
print("RESULT:", "PASS" if inv_up and s59_worse else "FAIL",
      "work60 no-inv", r[(60,0)]["work"], "inv", r[(60,10)]["work"],
      "work59 no-inv", r[(59,0)]["work"], "inv", r[(59,10)]["work"],
      "majors59", r[(59,0)]["majors"], "->", r[(59,10)]["majors"])
