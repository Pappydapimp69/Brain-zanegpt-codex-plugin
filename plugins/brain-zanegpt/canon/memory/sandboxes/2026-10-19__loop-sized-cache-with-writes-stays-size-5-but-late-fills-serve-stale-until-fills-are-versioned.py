"""RUN 1 (WEVERY=20 only) FAILED the stale prediction: stale reads were 0 for naive too, because a fill is in flight only after a miss and with one write per 20 accesses an invalidated item is refilled before the next write; the race needs writes faster than the fill latency. Revised prediction below, written before run 2 (sweep WEVERY 20, 4, 2).
Original prediction (before run 1): 1000 accesses cycling items 0..4, a write every 20 accesses to item (k mod 5) bumping its
version and invalidating it. LRU, cost hit 1 / miss 100. (1) D=0 fill latency: stale reads 0. (2) D=3 naive install
(fill installs the version it read at issue): stale reads > 0 (>= 5). (3) D=3 with versioned install (drop a fill older
than the latest invalidation): stale reads 0 at the same cost +-2%. (4) best size stays 5 in all three; size 4 has 0 hits
without invalidations. BREAK: D=3 naive with a size of 8 still serves stale reads (more slots do not cure staleness)."""
from collections import OrderedDict
N, LOOP = 1000, 5
WEVERY = 20
def run(size, D, versioned):
    ver = [0] * LOOP; lastinv = [-1] * LOOP
    cache = OrderedDict(); pend = []                      # pend: (arrive, item, ver_read, issue_time)
    hits = miss = stale = 0
    for t in range(N):
        if t and t % WEVERY == 0:
            k = (t // WEVERY) % LOOP; ver[k] += 1; lastinv[k] = t; cache.pop(k, None)
        for p in [p for p in pend if p[0] <= t]:
            pend.remove(p); _, it, v, issue = p
            if versioned and issue < lastinv[it]: continue         # fill raced a later invalidation: drop it
            if size:
                cache[it] = v; cache.move_to_end(it)
                while len(cache) > size: cache.popitem(last=False)
        it = t % LOOP
        if it in cache:
            hits += 1; cache.move_to_end(it); stale += cache[it] < ver[it]
        else:
            miss += 1
            if not any(p[1] == it for p in pend): pend.append((t + D, it, ver[it], t))
    return hits, miss, stale, hits + 100 * miss
summary = {}
for W in (20, 4, 2):
    WEVERY = W
    res = {}
    for name, (D, vz) in {"D0": (0, False), "D3 naive": (3, False), "D3 versioned": (3, True)}.items():
        res[name] = {sz: run(sz, D, vz) for sz in range(0, 9)}
    best = {n: min(r, key=lambda z: r[z][3]) for n, r in res.items()}
    summary[W] = (best, res["D0"][5][2], res["D3 naive"][5][2], res["D3 versioned"][5][2], res["D3 naive"][8][2], res["D3 naive"][5][3], res["D3 versioned"][5][3])
    print(W, summary[W])
w20, w4, w2 = summary[20], summary[4], summary[2]
ok = (w20[1:4] == (0, 0, 0) and w4[1] == 0 and w4[2] > 0 and w4[3] == 0 and w2[2] > 0 and w2[3] == 0
      and w4[4] > 0 and all(b == 5 for b in w20[0].values()))
print(("RESULT: PASS (revised claim) " if ok else "RESULT: FAIL ") +
      f"stale at size 5 (D0/naive/versioned): write/20 {w20[1:4]}, write/4 {w4[1:4]}, write/2 {w2[1:4]}; size 8 naive stale at write/4 {w4[4]}; best size at write/20 {sorted(set(w20[0].values()))}, at write/2 {sorted(set(w2[0].values()))}")
