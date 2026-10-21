"""Sandbox: Pareto front over the GC kernel's goals (throughput cost, pause, footprint) for a 5-item loop cache.
Configs: plain LRU size 0..5, pinned size 0..5; GC every 2/10/50 accesses; pause per collection = 10 x live slots.
Objectives (all minimized): total time (hits*1 + misses*100 + collections*pause), max pause, footprint (slots).
Prediction (before running): plain LRU sizes 1-4 are strictly dominated by size 0 (same hits, more footprint and pause),
so the LRU front is {0, 5} at each GC interval; pinned sizes 1-4 are NOT dominated, so the pinned front has all 6 sizes
at the 50-access interval. Wrong if any pinned partial size is dominated, or if LRU 1-4 reach the front."""
from collections import OrderedDict
N,ACC=5,1000
def hits(size,pin):
    pinned=[]; lru=OrderedDict(); h=0
    for t in range(ACC):
        x=t%N
        if x in pinned or x in lru:
            h+=1
            if x in lru: lru.move_to_end(x)
            continue
        if size==0: continue
        if len(pinned)<pin: pinned.append(x); continue
        room=size-len(pinned)
        if room<=0: continue
        if len(lru)>=room: lru.popitem(last=False)
        lru[x]=1
    return h
def objs(size,pin,every):
    h=hits(size,pin); pause=10*size
    return (h+(ACC-h)*100+(ACC//every)*pause, pause, size)
def front(pts):
    keep=[]
    for k,v in pts.items():
        dom=any(all(a<=b for a,b in zip(u,v)) and u!=v for j,u in pts.items() if j!=k)
        if not dom: keep.append(k)
    return keep
res={}
for every in (2,10,50):
    for mode in ("lru","pin"):
        pts={s:objs(s,s if mode=="pin" else 0,every) for s in range(6)}
        res[(every,mode)]=front(pts)
        print(f"GC every {every:2d} {mode}: front sizes {res[(every,mode)]}")
checks=[all(res[(e,"lru")]==[0,5] for e in (2,10,50)),
        res[(50,"pin")]==[0,1,2,3,4,5],
        all(set(res[(e,"lru")])<=set(res[(e,"pin")]) for e in (2,10,50))]
print("checks",checks)
print("RESULT:","PASS" if all(checks) else "FAIL",f"LRU fronts {[res[(e,'lru')] for e in (2,10,50)]}, pinned fronts {[res[(e,'pin')] for e in (2,10,50)]}")
