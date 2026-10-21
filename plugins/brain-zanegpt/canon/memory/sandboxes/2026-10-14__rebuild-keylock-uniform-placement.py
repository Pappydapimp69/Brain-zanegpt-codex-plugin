# Prediction (written first): on an H x W open room split by a one-cell door at column c, key placed on each
# free cell in turn (exhaustive, no RNG): unsolvable fraction = cells strictly beyond the door / free cells,
# restricted-to-pre-lock-reachable placement gives 0, and the fraction grows as the door moves toward the start.
from collections import deque
def build(H,W,c):
    free={(r,x) for r in range(H) for x in range(W) if x!=c or r==H//2}
    return free,(H//2,0),(H//2,W-1),(H//2,c)
def reach(free,start,blocked=None):
    seen={start};q=deque([start])
    while q:
        r,x=q.popleft()
        for n in((r+1,x),(r-1,x),(r,x+1),(r,x-1)):
            if n in free and n not in seen and n!=blocked: seen.add(n);q.append(n)
    return seen
def solvable(free,start,exit_,door,key):
    pre=reach(free,start,blocked=door)
    if key not in pre: return False
    return exit_ in reach(free,start)   # door opens with key
def stats(H,W,c):
    free,start,exit_,door=build(H,W,c)
    cands=[k for k in free if k not in(start,exit_,door)]
    bad=sum(not solvable(free,start,exit_,door,k) for k in cands)
    pre=reach(free,start,blocked=door)-{start,door}
    rbad=sum(not solvable(free,start,exit_,door,k) for k in pre)
    beyond=sum(1 for k in cands if k not in reach(free,start,blocked=door))
    return bad,len(cands),rbad,beyond
res=[]
for (H,W,c) in [(5,12,3),(5,12,6),(5,12,9),(3,20,2),(7,7,3)]:
    bad,n,rbad,beyond=stats(H,W,c); res.append((H,W,c,bad,n,rbad,beyond)); print(H,W,c,f"unsolvable {bad}/{n}={bad/n:.3f} restricted {rbad} beyond-door {beyond}")
ok=all(r[3]==r[6] and r[5]==0 and r[3]>0 for r in res) and res[0][3]/res[0][4]>res[1][3]/res[1][4]>res[2][3]/res[2][4]
print("RESULT:","PASS" if ok else "FAIL",f"uniform key placement unsolvable in {min(r[3]/r[4] for r in res):.3f}-{max(r[3]/r[4] for r in res):.3f} of placements across 5 rooms, always equal to the beyond-door share; restricted placement 0 in all")
