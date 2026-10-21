# Own fixture: 5x5 WFC, 3 tiles, separate horizontal/vertical allowed-pair matrices (9 bits each), no backtracking.
# PREDICTION (before run): ~20-40% of sets fail initial AC; among survivors 1-4% contradict after collapse;
# 10-50% of completed grids have disconnected walkable regions (tile 0 = wall); self-compatible-tile sets still contradict sometimes.
N=5; T=3
def rel(bits): return [[(bits>>(3*a+b))&1 for b in range(T)] for a in range(T)]
def propagate(dom,H,V):
    q=[(r,c) for r in range(N) for c in range(N)]
    while q:
        r,c=q.pop()
        for dr,dc,M,fwd in ((0,1,H,1),(0,-1,H,0),(1,0,V,1),(-1,0,V,0)):
            rr,cc=r+dr,c+dc
            if not(0<=rr<N and 0<=cc<N): continue
            new={b for b in dom[rr][cc] if any((M[a][b] if fwd else M[b][a]) for a in dom[r][c])}
            if new!=dom[rr][cc]:
                dom[rr][cc]=new
                if not new: return False
                q.append((rr,cc))
    return all(dom[r][c] for r in range(N) for c in range(N))
def regions(g):
    seen=set(); n=0
    for r in range(N):
        for c in range(N):
            if g[r][c]!=0 and (r,c) not in seen:
                n+=1; st=[(r,c)]; seen.add((r,c))
                while st:
                    y,x=st.pop()
                    for dy,dx in((1,0),(-1,0),(0,1),(0,-1)):
                        yy,xx=y+dy,x+dx
                        if 0<=yy<N and 0<=xx<N and g[yy][xx]!=0 and (yy,xx) not in seen: seen.add((yy,xx)); st.append((yy,xx))
    return n
def run(hb,vb):
    H,V=rel(hb),rel(vb)
    dom=[[set(range(T)) for _ in range(N)] for _ in range(N)]
    if not propagate(dom,H,V): return "init"
    while True:
        cand=[(len(dom[r][c]),r,c) for r in range(N) for c in range(N) if len(dom[r][c])>1]
        if not cand: break
        _,r,c=min(cand); dom[r][c]={min(dom[r][c])}
        if not propagate(dom,H,V): return "contra"
    g=[[min(d) for d in row] for row in dom]
    walk=sum(1 for row in g for v in row if v!=0)
    return ("disc" if regions(g)>1 else "ok", walk)
STRIDE=75
sets=[(h,v) for i,(h,v) in enumerate((h,v) for h in range(512) for v in range(512)) if i%STRIDE==0]
st={"init":0,"contra":0,"ok":0,"disc":0}; sc={"n":0,"contra":0}; comp=0
for h,v in sets:
    res=run(h,v); k=res if isinstance(res,str) else res[0]; st[k]+=1
    H,V=rel(h),rel(v)
    selfc=any(H[t][t] and V[t][t] for t in range(T))
    if k!="init":
        if selfc:
            sc["n"]+=1; sc["contra"]+= (k=="contra")
nontriv=len(sets)-st["init"]; done=st["ok"]+st["disc"]
print("sets",len(sets),st,"non-trivial",nontriv)
print("self-compatible subset",sc)
pi=st["init"]/len(sets); pc=st["contra"]/nontriv; pd=st["disc"]/done
print("init-fail %.1f%% contradiction %.1f%% of non-trivial, disconnected %.1f%% of completed"%(pi*100,pc*100,pd*100))
ok = 0.2<=pi<=0.4 and 0.01<=pc<=0.04 and 0.10<=pd<=0.50 and sc["contra"]>0
print("RESULT: %s init-fail %.1f%%, contradiction %.1f%%, disconnected %.1f%%, self-compatible sets contradicting %d of %d"%("PASS" if ok else "FAIL",pi*100,pc*100,pd*100,sc["contra"],sc["n"]))
