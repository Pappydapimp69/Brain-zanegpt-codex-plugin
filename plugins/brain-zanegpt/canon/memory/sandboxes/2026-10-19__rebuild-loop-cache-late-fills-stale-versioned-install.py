"""Rebuild: LRU cache on a loop of 5 items; writes invalidate; fills land D accesses late.
Own fixture: loop of 5 over N=600 accesses, write hits item (3*k+1)%5 every W accesses. No RNG."""
from collections import OrderedDict
L, N = 5, 600
def run(size, W, D, versioned):
    ver = [0]*L                      # current version of each item
    cache = OrderedDict()            # item -> version held
    pend = {}                        # item -> (land_at, version_when_started)
    hits = stale = 0
    for i in range(N):
        if i and i % W == 0:
            w = (3*(i//W)+1) % L
            ver[w] += 1
            cache.pop(w, None)       # write invalidates the cached copy
        for it, (land, v) in list(pend.items()):
            if land <= i:
                del pend[it]
                if versioned and v < ver[it]: continue   # reject fill older than last invalidation
                if size > 0:
                    cache[it] = v; cache.move_to_end(it)
                    while len(cache) > size: cache.popitem(last=False)
        x = i % L
        if x in cache:
            hits += 1
            if cache[x] < ver[x]: stale += 1
            cache.move_to_end(x)
        elif x not in pend and size > 0:
            pend[x] = (i + D, ver[x])
    return hits, stale
R = {}
for W in (20, 4, 2):
    for size in range(0, 9):
        R[(W, size, 'n')] = run(size, W, 3, False)
        R[(W, size, 'v')] = run(size, W, 3, True)
best = {W: max(range(9), key=lambda s: (R[(W, s, 'v')][0], -s)) for W in (20, 4, 2)}
for W in (20, 4, 2):
    print(f"W={W}: naive stale at size5={R[(W,5,'n')][1]} size8={R[(W,8,'n')][1]}; versioned stale size5={R[(W,5,'v')][1]} size8={R[(W,8,'v')][1]}; best size (versioned hits)={best[W]}")
ok = (R[(2,5,"n")][1] >= 1 and R[(2,8,'n')][1] >= R[(2,5,'n')][1]
      and all(R[(W,s,'v')][1] == 0 for W in (20,4,2) for s in range(9)) and best[20] == 5)
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" naive stale W20/4/2 at size5 = {R[(20,5,'n')][1]}/{R[(4,5,'n')][1]}/{R[(2,5,'n')][1]}; size8 W2 = {R[(2,8,'n')][1]}; versioned stale all 0; best size W20={best[20]} W4={best[4]} W2={best[2]}")
