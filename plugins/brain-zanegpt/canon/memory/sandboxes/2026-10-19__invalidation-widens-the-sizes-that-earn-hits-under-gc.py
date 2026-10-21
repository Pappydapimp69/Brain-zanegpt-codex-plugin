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
def sweep(every):
    return {sz: run(sz, L, N, every) for sz in range(0, 62)}
a, b = sweep(0), sweep(10)
def best_nonzero(r):
    # cheapest GC work among sizes that earn at least one hit; ties go to the smaller cache
    c = [(v["work"], sz) for sz, v in r.items() if v["hits"] > 0]
    return min(c)
bw0, bs0 = best_nonzero(a); bw1, bs1 = best_nonzero(b)
hit_sizes0 = sorted(sz for sz, v in a.items() if v["hits"] > 0)
hit_sizes1 = sorted(sz for sz, v in b.items() if v["hits"] > 0)
print("no invalidation: sizes with hits", hit_sizes0[:3], "..", hit_sizes0[-1], "count", len(hit_sizes0), "| cheapest hit size", bs0, "work", bw0)
print("invalidate/10  : sizes with hits", hit_sizes1[:3], "..", hit_sizes1[-1], "count", len(hit_sizes1), "| cheapest hit size", bs1, "work", bw1)
print("size 0 work", a[0]["work"], "size 30", a[30], b[30], "size 58", a[58], b[58])
# prediction: without invalidation only size 60+ earns hits; with it, partial sizes (>=1) also earn hits,
# and the cheapest hit-earning size moves below 60 only if its work is lower than size 60's work under invalidation
ok = len(hit_sizes0) == 2 and len(hit_sizes1) > len(hit_sizes0) and bs0 == 60 and b[60]["work"] > a[60]["work"]
print(f"RESULT: {'PASS' if ok else 'FAIL'} sizes earning hits {len(hit_sizes0)} -> {len(hit_sizes1)}; cheapest hit-earning size {bs0} (work {bw0}) -> {bs1} (work {bw1})")
