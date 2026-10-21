"""Versioned vs naive fill install under random (Poisson-like) writes, skewed access,
fill latency D above the write gap, with an install (allocation/GC) cost G per install.
Stdlib only, deterministic (seeded)."""
import random
from collections import OrderedDict

HIT, MISS = 1, 100

def run(mode, size, D, gap, G, seed, n=3000, items=5, skew=False):
    rng = random.Random(seed)
    ver = [0] * items
    cache = OrderedDict()          # key -> version held
    flight = {}                    # key -> (install_time, version_read)
    hits = misses = stale = installs = dropped = 0
    nextw = rng.randint(1, 2 * gap)
    for t in range(n):
        for k in [k for k, (ti, _) in flight.items() if ti <= t]:
            ti, v = flight.pop(k)
            if mode == "versioned" and v != ver[k]:
                dropped += 1
                continue
            if size == 0:
                continue
            if k in cache:
                cache.move_to_end(k)
            elif len(cache) >= size:
                cache.popitem(last=False)
            cache[k] = v
            installs += 1
        if t >= nextw:
            k = rng.randrange(items)
            ver[k] += 1
            cache.pop(k, None)
            nextw = t + rng.randint(1, 2 * gap)
        k = rng.choices(range(items), weights=[8, 4, 2, 1, 1])[0] if skew else t % items
        if k in cache:
            hits += 1
            cache.move_to_end(k)
            if cache[k] < ver[k]:
                stale += 1
        else:
            misses += 1
            if size and k not in flight:
                flight[k] = (t + D, ver[k])
    cost = hits * HIT + misses * MISS + installs * G
    return dict(cost=cost, stale=stale, dropped=dropped, installs=installs, hits=hits)

def avg(mode, **kw):
    rs = [run(mode, seed=s, **kw) for s in range(20)]
    return {k: sum(r[k] for r in rs) / len(rs) for k in rs[0]}

cells = []
for skew in (False, True):
    for D in (3, 8, 16):
        for gap in (2, 4, 20):
            for G in (0, 30):
                nv = avg("naive", size=5, D=D, gap=gap, G=G, skew=skew)
                vr = avg("versioned", size=5, D=D, gap=gap, G=G, skew=skew)
                cells.append((skew, D, gap, G, nv, vr))

stale_v = sum(1 for c in cells if c[5]["stale"] > 0)
stale_n = sum(1 for c in cells if c[4]["stale"] > 0)
v_cheaper = sum(1 for c in cells if c[5]["cost"] < c[4]["cost"])
v_dearer = [c for c in cells if c[5]["cost"] > c[4]["cost"] * 1.02]
worst = max(cells, key=lambda c: c[5]["cost"] / c[4]["cost"])
print(f"cells {len(cells)}; naive stale in {stale_n}; versioned stale in {stale_v}")
print(f"versioned cheaper in {v_cheaper}; dearer by >2% in {len(v_dearer)}")
print("worst ratio cell (skew,D,gap,G):", worst[:4],
      "naive", round(worst[4]["cost"]), "versioned", round(worst[5]["cost"]),
      "dropped", round(worst[5]["dropped"], 1))
ok = stale_v == 0 and stale_n > 0 and len(v_dearer) <= 6
print(f"RESULT: {'PASS' if ok else 'FAIL'} versioned stale in {stale_v}/{len(cells)} cells vs naive {stale_n}; "
      f"versioned cheaper in {v_cheaper}, dearer by >2% in {len(v_dearer)}; worst cost ratio {worst[5]['cost']/worst[4]['cost']:.3f}")
