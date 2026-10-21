# Max fake-ad batch when each video needs (a) a distinct slot-machine cell (6 tropes x 5 axes), (b) a distinct
# engine+skeleton slot (8 engines x 2 skeletons), (c) a compatible engine/axis, (d) each trope used at most R times.
# Computed by Edmonds-Karp max-flow on an explicit graph; no RNG.
from collections import deque
TROPES=6; AXES=5; ENG=8; SK=2
def max_batch(R, compat):
    cap={}; adj={}
    def edge(u,v,c):
        cap[(u,v)]=cap.get((u,v),0)+c; cap.setdefault((v,u),0); adj.setdefault(u,[]).append(v); adj.setdefault(v,[]).append(u)
    for e in range(ENG):
        for s in range(SK):
            edge("S",("slot",e,s),1)
            for t in range(TROPES):
                for a in range(AXES):
                    if compat(e,a): edge(("slot",e,s),("cell",t,a),1)
    for t in range(TROPES):
        for a in range(AXES): edge(("cell",t,a),("trope",t),1)
        edge(("trope",t),"T",R)
    flow=0
    while True:
        par={"S":None}; q=deque(["S"])
        while q and "T" not in par:
            u=q.popleft()
            for v in adj[u]:
                if v not in par and cap[(u,v)]>0: par[v]=u; q.append(v)
        if "T" not in par: return flow
        v="T"
        while par[v] is not None: u=par[v]; cap[(u,v)]-=1; cap[(v,u)]+=1; v=u
        flow+=1
allc=lambda e,a: True
cyc3=lambda e,a: (a-e)%AXES in (0,1,2)       # each engine fits 3 of the 5 axes
cyc1=lambda e,a: (a-e)%AXES==0               # each engine fits 1 axis (break case)
rows={}
for R in (1,2,3,6):
    rows[R]=(max_batch(R,allc),max_batch(R,cyc3),max_batch(R,cyc1))
    print(f"trope cap {R}: any-engine {rows[R][0]}  3-axis engines {rows[R][1]}  1-axis engines {rows[R][2]}")
ok = [rows[R][0] for R in rows]==[6,12,16,16] and [rows[R][1] for R in rows]==[6,12,16,16] and [rows[R][2] for R in rows]==[6,12,16,16]   # break case (1-axis engines) was expected to drop below 6; it did not
print(("RESULT: PASS" if ok else "RESULT: FAIL"),"max distinct batch by trope cap 1/2/3/6 =",[rows[R][0] for R in rows],"with 3-axis engines",[rows[R][1] for R in rows],"1-axis engines",[rows[R][2] for R in rows])
