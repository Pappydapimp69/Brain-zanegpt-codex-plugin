"""Sandbox: loop of 5 keys, LRU cache of 5, late fills (latency L), invalidating writes,
toy generational GC. Compare: unversioned fills, versioned fills that allocate BEFORE the
version check, versioned fills that allocate AFTER it. No RNG, no timing."""
from collections import OrderedDict
NURSERY, MAJOR_AT, LOOP, SIZE = 10, 20, 5, 5

def run(policy, L, W, n=600):
    cache = OrderedDict()          # key -> (read_version, entry_id)
    dbver = [0] * LOOP
    pending = {}                   # key -> (arrive_at, read_version)
    young, old = set(), set()
    garbage = allocs = work = majors = stale = hits = nid = 0
    def kill(e):
        nonlocal garbage
        if e in old: old.discard(e); garbage += 1
        else: young.discard(e)
    def alloc():
        nonlocal allocs, work, old, young, nid
        nid += 1; allocs += 1; young.add(nid)
        if allocs % NURSERY == 0:
            work += len(young); old |= young; young = set()
        return nid
    for i in range(n):
        if W and i and i % W == 0:                      # write + invalidate
            v = (i // W * 7) % LOOP; dbver[v] += 1
            if v in cache: kill(cache.pop(v)[1])
        for k, (at, rv) in list(pending.items()):       # late fills arrive
            if at != i: continue
            del pending[k]
            if policy == "versioned_after":
                if rv < dbver[k]: continue              # reject, nothing allocated
                e = alloc()
            else:
                e = alloc()
                if policy == "versioned_before" and rv < dbver[k]:
                    kill(e); continue                   # allocated, then dropped
            if len(cache) >= SIZE:
                _, (_, old_e) = cache.popitem(last=False); kill(old_e)
            cache[k] = (rv, e); cache.move_to_end(k)
        k = i % LOOP
        if k in cache:
            hits += 1; cache.move_to_end(k)
            if cache[k][0] < dbver[k]: stale += 1
        elif k not in pending:
            pending[k] = (i + L, dbver[k])
        if garbage >= MAJOR_AT:
            work += len(old) + garbage; majors += 1; garbage = 0
    return dict(stale=stale, allocs=allocs, gc=work, majors=majors, hits=hits)

POL = ("unversioned", "versioned_before", "versioned_after")
Ls, Ws = (1, 2, 3, 5, 8, 12), (0, 3, 4, 6, 7, 9, 11, 13, 17)
grid = {(L, W, p): run(p, L, W) for L in Ls for W in Ws for p in POL}
cells = [(L, W) for L in Ls for W in Ws]
wr = [(L, W) for L, W in cells if W]
unv_stale = [c for c in wr if grid[c + ("unversioned",)]["stale"] > 0]
ver_stale = [c for c in wr if grid[c + ("versioned_before",)]["stale"] or grid[c + ("versioned_after",)]["stale"]]
gc_diff = [c for c in wr if grid[c + ("versioned_before",)]["gc"] != grid[c + ("versioned_after",)]["gc"]]
alloc_diff = [c for c in wr if grid[c + ("versioned_before",)]["allocs"] != grid[c + ("versioned_after",)]["allocs"]]
nowrite_tie = all(grid[(L, 0, "versioned_before")] == grid[(L, 0, "versioned_after")] == {**grid[(L, 0, "unversioned")]} for L in Ls)
ex = max(wr, key=lambda c: grid[c + ("versioned_before",)]["gc"] - grid[c + ("versioned_after",)]["gc"])
print("write cells:", len(wr), "| unversioned stale in", len(unv_stale), "| versioned stale in", len(ver_stale))
print("alloc-before differs in allocs in", len(alloc_diff), "cells, in gc work in", len(gc_diff), "cells; largest gc gap", ex,
      grid[ex + ("versioned_before",)]["gc"], "vs", grid[ex + ("versioned_after",)]["gc"])
print("no-write cells identical across policies:", nowrite_tie)
ok = nowrite_tie and len(ver_stale) == 0 and len(unv_stale) > 0 and len(gc_diff) > 0
print("RESULT: %s versioned fills gave 0 stale reads in all %d write cells while unversioned went stale in %d; allocating before the check changed GC work in only %d cells (largest gap %d vs %d); no-write cells tie"
      % ("PASS" if ok else "FAIL", len(wr), len(unv_stale), len(gc_diff),
         grid[ex + ("versioned_before",)]["gc"], grid[ex + ("versioned_after",)]["gc"]))
