# Deterministic model: DB value per key, cache with fill path and invalidate path.
# Every interleaving of (reader: read-db, fill-cache) vs (writer: write-db, invalidate)
# is enumerated exhaustively, no RNG, no timing.
import itertools
from collections import OrderedDict

def run(order, policy, cap=None):
    db = {"x": 42}; ver = {"x": 1}; cache = OrderedDict()
    st = {}
    for step in order:
        if step == "R1":   # reader reads db (value+version) at this moment
            st["rv"] = (db["x"], ver["x"])
        elif step == "R2": # reader fills cache
            v, vv = st["rv"]
            if policy == "versioned":
                cur = cache.get("x")
                if cur is not None and cur[1] > vv: continue
                if cur is None and vv < ver["x"]: continue   # stale fill rejected
            cache["x"] = (v, vv)
        elif step == "W1":
            db["x"] = 43; ver["x"] = 2
        elif step == "W2":
            cache.pop("x", None)
    c = cache.get("x")
    return c is not None and c[0] != db["x"]  # stale forever

def orders():
    for p in itertools.permutations(["R1","R2","W1","W2"]):
        if p.index("R1")<p.index("R2") and p.index("W1")<p.index("W2"):
            yield p

tot = list(orders())
res = {}
for pol in ("naive","versioned"):
    bad = [o for o in tot if run(o, pol)]
    res[pol] = bad
print("interleavings", len(tot))
for pol, bad in res.items():
    print(pol, "permanently stale:", len(bad), [" ".join(b) for b in bad])

# Scenario 3 (built to BREAK): bounded staleness (TTL) heals what naive leaves broken,
# but costs refills. Loop of 5 keys over a capacity-5 LRU (gc-cost-vs-loop-sized-cache shape);
# latency-numbers ratio: miss=500000ns (network), hit=100ns (memory).
HIT, MISS = 100, 500000
def loop_cost(ttl, writes_every, n=1000, keys=5, cap=5):
    cache = OrderedDict(); t=0; cost=0; stale=0; dbv={k:0 for k in range(keys)}
    for i in range(n):
        k = i % keys
        if writes_every and i % writes_every == 0:
            dbv[k] += 1   # write WITHOUT invalidation (the lost-invalidate race outcome)
        e = cache.get(k)
        if e and (ttl is None or i - e[1] < ttl):
            cost += HIT; cache.move_to_end(k)
            if e[0] != dbv[k]: stale += 1
        else:
            cost += MISS; cache[k] = (dbv[k], i); cache.move_to_end(k)
            if len(cache) > cap: cache.popitem(last=False)
    return cost, stale
for ttl in (None, 50, 10, 5):
    print("ttl", ttl, "cost,stale-reads", loop_cost(ttl, 7))

nb, vb = len(res["naive"]), len(res["versioned"])
c_none = loop_cost(None,7); c5=loop_cost(5,7)
ok = nb>0 and vb==0 and c_none[1]>0 and c5[1]<=c_none[1] and c5[0]>c_none[0]
print(f"RESULT: {'PASS' if ok else 'FAIL'} naive stale interleavings={nb}/6 versioned={vb}/6; TTL=5 cuts stale reads {c_none[1]}->{c5[1]} at cost {c_none[0]}->{c5[0]}")
