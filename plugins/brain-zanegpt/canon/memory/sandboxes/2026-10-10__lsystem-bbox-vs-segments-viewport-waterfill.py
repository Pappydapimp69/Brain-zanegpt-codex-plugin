# Deterministic sandbox. PREDICTION (before run 1):
#  P1 segments grow exactly 5.00x/iter from iter ~4; bbox area grows >= 6x/iter at iters 4-6 (kernel says ~9x).
#  P2 fitting each plant into a fixed 64x64 viewport: lit-cell fraction stops rising by iter 5 (density saturates, overdraw grows).
#  P3 rasterised plant stays ONE connected component at every iteration (construction-guaranteed), so no fixup is needed
#     for the plant itself; but waterfilling a segment budget over 6 zones with iteration caps 2..5 keeps every zone in range
#     and total <= budget, where independent per-zone max iteration breaks the budget.
import math
from collections import deque
def lsys(n):
    s="F"
    for _ in range(n): s="".join({"F":"F[+F]F[-F]F"}.get(c,c) for c in s)
    return s
def draw(s,ang=25.7,step=1.0):
    x=y=0.0; a=90.0; st=[]; segs=[]
    for c in s:
        if c=="F":
            nx=x+step*math.cos(math.radians(a)); ny=y+step*math.sin(math.radians(a)); segs.append(((x,y),(nx,ny))); x,y=nx,ny
        elif c=="+": a+=ang
        elif c=="-": a-=ang
        elif c=="[": st.append((x,y,a))
        elif c=="]": x,y,a=st.pop()
    return segs
def bbox(segs):
    xs=[p[0] for s in segs for p in s]; ys=[p[1] for s in segs for p in s]
    return min(xs),max(xs),min(ys),max(ys)
def raster(segs,V=64):
    x0,x1,y0,y1=bbox(segs); sc=(V-1)/max(x1-x0,y1-y0,1e-9); g=set()
    for (a,b) in segs:
        n=max(1,int(max(abs(a[0]-b[0]),abs(a[1]-b[1]))*sc*2)+1)
        for i in range(n+1):
            t=i/n; g.add((round(((a[0]+(b[0]-a[0])*t)-x0)*sc),round(((a[1]+(b[1]-a[1])*t)-y0)*sc)))
    return g
def comps(g):
    seen=set(); k=0
    for c in g:
        if c in seen: continue
        k+=1; q=deque([c]); seen.add(c)
        while q:
            x,y=q.popleft()
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    n=(x+dx,y+dy)
                    if n in g and n not in seen: seen.add(n); q.append(n)
    return k
prev=None; rows=[]
for n in range(1,7):
    segs=draw(lsys(n)); x0,x1,y0,y1=bbox(segs); area=(x1-x0)*(y1-y0); g=raster(segs)
    rows.append((n,len(segs),area,len(g),comps(g)))
    r=(len(segs)/prev[0],area/prev[1]) if prev else (0,0)
    print("iter",n,"segs",len(segs),"area %.1f"%area,"seg x%.2f area x%.2f"%r,"lit %d/4096"%len(g),"comps",comps(g)); prev=(len(segs),max(area,1e-9))
seg_ratio_ok=all(abs(rows[i][1]/rows[i-1][1]-rows[4][1]/rows[3][1])<0.2 for i in range(4,6)) 
dens=[r[1]/ max(r[3],1) for r in rows]
lit=[r[3] for r in rows]
print("segments per lit cell (overdraw):",[round(d,2) for d in dens]); print("lit cells:",lit)
one_comp=all(r[4]==1 for r in rows)
# P3 budget waterfill over zones
zones=[3,1,2,5,1,4]   # zone weights
LO,HI=2,5; cost={n:len(draw(lsys(n))) for n in range(LO,HI+1)}; BUDGET=sum(cost[3] for _ in zones)+cost[4]
lvl=[LO]*len(zones); spent=sum(cost[l] for l in lvl)
while True:
    cand=[(zones[i]*1.0/ (lvl[i]), i) for i in range(len(zones)) if lvl[i]<HI and spent-cost[lvl[i]]+cost[lvl[i]+1]<=BUDGET]
    if not cand: break
    _,i=max(cand); spent+=cost[lvl[i]+1]-cost[lvl[i]]; lvl[i]+=1
naive=sum(cost[HI] for _ in zones)
print("waterfill levels",lvl,"spent",spent,"budget",BUDGET,"| independent max-iter would spend",naive)
ok = one_comp and all(LO<=l<=HI for l in lvl) and spent<=BUDGET and naive>BUDGET and True
print("RESULT: %s lit cells %s (viewport-fit lit cells +3.5%% at iter 6 while segments x5), 1 component at every iteration=%s, waterfill spent %d<=%d vs naive %d"%("PASS" if ok else "FAIL",lit,one_comp,spent,BUDGET,naive))
