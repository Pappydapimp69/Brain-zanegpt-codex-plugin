"""Sandbox 2 (reuses the model of 2026-10-19__versioned-fills-on-a-loop-cache-allocate-after-the-check.py).
Loop of 5 keys, LRU cache of `size`, late fills (latency L), invalidating writes,
toy generational GC. Compare: unversioned fills, versioned fills that allocate BEFORE the
version check, versioned fills that allocate AFTER it. No RNG, no timing."""
from collections import OrderedDict
NURSERY, MAJOR_AT, LOOP = 10, 20, 5

def run(policy, L, W, size=5, n=600):
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
            if len(cache) >= size:
                _, (_, old_e) = cache.popitem(last=False); kill(old_e)
            cache[k] = (rv, e); cache.move_to_end(k)
        k = i % LOOP
        if k in cache:
            hits += 1; cache.move_to_end(k)
            if cache[k][0] < dbver[k]: stale += 1
        elif size and k not in pending:
            pending[k] = (i + L, dbver[k])
        if garbage >= MAJOR_AT:
            work += len(old) + garbage; majors += 1; garbage = 0
    return dict(stale=stale, allocs=allocs, gc=work, majors=majors, hits=hits)


N = 600
MISS = 500          # cost of one miss (a refill from the source), arbitrary units
def total(policy, L, W, size, pause):
    r = run(policy, L, W, size, N)
    return (N - r["hits"]) * MISS + r["gc"] * pause, r

def breakeven(pol, L, W):
    none = run(pol, L, W, 0, N); c5 = run(pol, L, W, 5, N)
    saved = (c5["hits"] - none["hits"]) * MISS
    return saved / c5["gc"] if c5["gc"] else float("inf")
Ls, Ws = (1, 2, 3, 5, 8), (3, 4, 6, 7, 9, 13, 29)
tab = {(L, W): (breakeven("versioned_before", L, W), breakeven("versioned_after", L, W)) for L in Ls for W in Ws}
moved = {k: v for k, v in tab.items() if v[0] != v[1]}
for k, v in sorted(moved.items()): print("L=%d W=%2d break-even pause: alloc-before %.1f, alloc-after %.1f (x%.2f)" % (k + v + (v[1] / v[0],)))
nowrite = [(L, breakeven("versioned_before", L, 0), breakeven("versioned_after", L, 0)) for L in Ls]
print("no-write break-even (before, after):", nowrite)
# partial caches (size 1-4): cheapest anywhere across pauses?
partial_wins = cells = ties = 0
for L in (1, 3, 8):
    for W in (0, 7, 29):
        for pause in (0.5, 5, 50, 500, 5000):
            costs = {sz: (N - run("versioned_after", L, W, sz, N)["hits"]) * MISS + run("versioned_after", L, W, sz, N)["gc"] * pause for sz in range(0, 7)}
            cells += 1; bs = min(costs, key=costs.get)
            if bs in (1, 2, 3, 4): ties += 1; partial_wins += costs[bs] < min(costs[5], costs[0]); print('partial cache ties/leads: L=%d W=%d pause=%s size=%d cost %.0f vs size5 %.0f vs none %.0f' % (L, W, pause, bs, costs[bs], costs[5], costs[0]))
print("cells where a partial cache strictly beats both size 5 and no cache:", partial_wins, "| ties with size 5:", ties, "| of", cells)
ratios = [v[1] / v[0] for v in moved.values() if v[0] not in (0, float("inf"))]
ok = len(moved) > 0 and all(v[0] == v[1] for v in [(b, a2) for _, b, a2 in nowrite])
print("RESULT: %s allocation order moved the size-5 versus no-cache break-even pause in %d of %d (latency, write period) cells, by up to x%.2f when it moved, and never with no writes; partial caches strictly beat size 5 and no cache in %d of %d cells (%d exact ties with size 5)"
      % ("PASS" if ok else "FAIL", len(moved), len(tab), max(ratios) if ratios else 1.0, partial_wins, cells, ties))
