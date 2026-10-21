"""Gap sandbox (stdlib, deterministic): what a loop-one-slot-too-big cache does to a
GENERATIONAL garbage collector.

Composes:
 - CACHE-EVICTION kernel (size the cache to the loop, not the policy): a loop one item bigger than the
   cache scores 0 hits for LRU and FIFO.
 - local__sandbox-cache-size-sweep-loop-cliff-and-ram-ceiling E1: judge size by cost, not hit rate.
 - PERFORMANCE GC kernel: throughput, pause, footprint and promptness trade off; generational GC rests on
   the weak generational hypothesis and does badly when objects live past promotion and then die.
Gap: local__gc-cost-vs-loop-sized-cache E1 priced GC as a pause linear in LIVE slots with no
generations. Hidden assumption tested here: a cache's GC cost scales with how many entries it holds.
Model (assumed constants, named): each access allocates 4 temporaries that die at the end of the
access; a miss allocates 1 cache entry and evicts 1 (it dies at that moment). Young gen collects every
Y allocations, copying survivors (cost 1 each); survivors of T=2 minor GCs are promoted to old. Old gen
collects (major) when live+garbage reaches OCAP=200, cost = old live + garbage scanned. 6000 accesses.
Metrics: throughput cost (total GC work), max pause, peak footprint, mean promptness (accesses between
an object's death and its reclaim).
PREDICTION (written before running):
 A loop 60 / cache 60 (hits): 0 majors.
 B loop 60 / cache 59 (one short, 0 hits): entries die at age 59 accesses after promotion -> 20+ majors.
 C loop 5 / cache 4 (one short, 0 hits, tiny): entries die young -> 0 majors, so thrashing alone is not
   the GC problem; entry LIFETIME vs promotion age is.
 D = B with young gen 4x bigger (Y=400): 0 majors, but higher peak footprint and worse promptness.
 E = B with cache sized up to 60: back to 0 majors (size-to-the-loop fixes the GC too).
"""
from collections import OrderedDict


def run(loop, slots, Y=100, T=2, OCAP=200, N=6000, temps=4):
    cache = OrderedDict()  # key -> object id (LRU)
    objs = {}  # id -> dict(born, dead, gen, age)
    young, old = set(), set()
    nid = 0
    alloc_since = 0
    hits = misses = minors = majors = 0
    work = 0
    max_pause = 0
    peak = 0
    prompt_sum = prompt_n = 0
    promoted = 0

    def new(t):
        nonlocal nid, alloc_since
        nid += 1
        objs[nid] = {"born": t, "dead": None, "age": 0}
        young.add(nid)
        alloc_since += 1
        return nid

    def reclaim(o, t):
        nonlocal prompt_sum, prompt_n
        prompt_sum += t - objs[o]["dead"]
        prompt_n += 1
        del objs[o]

    def minor(t):
        nonlocal minors, work, max_pause, alloc_since, promoted
        minors += 1
        cost = 0
        for o in list(young):
            if objs[o]["dead"] is not None:
                young.discard(o)
                reclaim(o, t)
            else:
                cost += 1
                objs[o]["age"] += 1
                if objs[o]["age"] >= T:
                    young.discard(o)
                    old.add(o)
                    promoted += 1
        work += cost
        max_pause = max(max_pause, cost)
        alloc_since = 0

    def major(t):
        nonlocal majors, work, max_pause
        majors += 1
        cost = len(old)
        for o in list(old):
            if objs[o]["dead"] is not None:
                old.discard(o)
                reclaim(o, t)
        work += cost
        max_pause = max(max_pause, cost)

    for t in range(N):
        key = t % loop
        tmp = [new(t) for _ in range(temps)]
        if key in cache:
            cache.move_to_end(key)
            hits += 1
        else:
            misses += 1
            if len(cache) >= slots:
                _, victim = cache.popitem(last=False)
                objs[victim]["dead"] = t
            cache[key] = new(t)
        for o in tmp:
            objs[o]["dead"] = t
        peak = max(peak, len(young) + len(old))
        if alloc_since >= Y:
            minor(t)
        if len(old) >= OCAP:
            major(t)
    return dict(hits=hits, minors=minors, majors=majors, promoted=promoted, work=work,
                max_pause=max_pause, peak=peak, prompt=prompt_sum / max(prompt_n, 1))


cases = {
    "A loop60 cache60": run(60, 60),
    "B loop60 cache59": run(60, 59),
    "C loop5 cache4": run(5, 4),
    "D loop60 cache59 Y400": run(60, 59, Y=400),
    "E loop60 cache61": run(60, 61),
}
for k, v in cases.items():
    print(f"{k:22s} hits {v['hits']:5d} minors {v['minors']:4d} majors {v['majors']:3d} promoted {v['promoted']:5d} "
          f"gc_work {v['work']:6d} max_pause {v['max_pause']:4d} peak_heap {v['peak']:4d} promptness {v['prompt']:.1f}")

# where is the GC cliff? sweep cache size on loop 60 and loop size at cache = loop-1
sweep = []
for s in (5, 10, 15, 20, 25, 30, 40, 50, 59):
    v = run(s + 1, s)
    sweep.append((s, v["majors"], v["promoted"]))
print("thrashing cache (loop = size+1): size/majors/promoted:", sweep)
first_major = next((s for s, m, _ in sweep if m > 0), None)

A, B, C, D, E = (cases[k] for k in cases)
checks = [
    ("A fits: 0 majors", A["majors"] == 0),
    ("B one short: 20+ majors and 0 hits", B["majors"] >= 20 and B["hits"] == 0),
    ("C tiny one short: 0 majors though 0 hits", C["majors"] == 0 and C["hits"] == 0),
    ("D bigger young gen: 0 majors, more footprint, worse promptness",
     D["majors"] == 0 and D["peak"] > B["peak"] and D["prompt"] > B["prompt"]),
    ("E size to loop fixes GC too", E["majors"] == 0),
]
for n, ok in checks:
    print(("ok   " if ok else "FAIL ") + n)
p = sum(ok for _, ok in checks)
print(f"RESULT: {'PASS' if p == len(checks) else 'FAIL'} {p}/{len(checks)}; loop60: cache60 majors {A['majors']} work {A['work']}, "
      f"cache59 majors {B['majors']} promoted {B['promoted']} work {B['work']}; loop5/cache4 majors {C['majors']}; "
      f"Y400 majors {D['majors']} peak {D['peak']} vs {B['peak']} promptness {D['prompt']:.1f} vs {B['prompt']:.1f}; "
      f"thrash GC cliff first at size {first_major}")
