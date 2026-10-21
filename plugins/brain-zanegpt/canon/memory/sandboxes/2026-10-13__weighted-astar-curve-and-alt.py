# Sandbox: weighted A* sweep (expansions + cost ratio) on 3 deterministic maps, plus ALT heuristic.
import heapq, math
def mkmap(kind, n=48):
    g=[[0]*n for _ in range(n)]
    if kind=="open": pass
    elif kind=="bars":   # alternating walls with gaps at alternating ends
        for i,x in enumerate(range(6,n-6,6)):
            for y in range(n):
                g[y][x]=1
            g[0 if i%2 else n-1][x]=0
            g[1 if i%2 else n-2][x]=0
    elif kind=="blocks": # deterministic pseudo-scatter, no RNG
        for y in range(n):
            for x in range(n):
                if (x*7+y*13)%11==0 and (x,y) not in((0,0),(n-1,n-1)): g[y][x]=1
    return g
def nbrs(g,p):
    n=len(g);x,y=p
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
        a,b=x+dx,y+dy
        if 0<=a<n and 0<=b<n and not g[b][a]: yield (a,b)
def astar(g,s,t,h,w):
    openq=[(w*h((s)),0,s)];best={s:0};ex=0;done=set()
    while openq:
        f,c,p=heapq.heappop(openq)
        if p in done: continue
        done.add(p);ex+=1
        if p==t: return c,ex
        for q in nbrs(g,p):
            nc=c+1
            if nc<best.get(q,1e9):
                best[q]=nc;heapq.heappush(openq,(nc+w*h(q),nc,q))
    return None,ex
def bfs(g,s):
    d={s:0};q=[s]
    for p in q:
        for r in nbrs(g,p):
            if r not in d:d[r]=d[p]+1;q.append(r)
    return d
res={}
W=[1,1.1,1.25,1.5,2,3,5,10]
for kind in("open","bars","blocks"):
    g=mkmap(kind);n=len(g);s=(0,0);t=(n-1,n-1)
    man=lambda p:abs(p[0]-t[0])+abs(p[1]-t[1])
    opt,e1=astar(g,s,t,man,1)
    rows=[]
    for w in W:
        c,e=astar(g,s,t,man,w);rows.append((w,e,c/opt))
    res[kind]=(opt,e1,rows)
    print(kind,"opt",opt,"expansions@w1",e1)
    for w,e,r in rows: print("  w=%-4s exp=%5d (%.2fx of w1) cost=%.3fx"%(w,e,e/e1,r))
# ALT with 4 corner landmarks on 'bars'
g=mkmap("bars");n=len(g);s=(0,0);t=(n-1,n-1)
lm=[(0,0),(n-1,0),(0,n-1),(n-1,n-1)];D=[bfs(g,l) for l in lm]
def alt(p): return max(abs(d.get(p,0)-d.get(t,0)) for d in D)
man=lambda p:abs(p[0]-t[0])+abs(p[1]-t[1])
c_m,e_m=astar(g,s,t,man,1);c_a,e_a=astar(g,s,t,alt,1)
print("ALT bars: manhattan exp",e_m,"ALT exp",e_a,"costs",c_m,c_a)
# Findings
ok=True
# 1) open map: any weight>1 collapses expansions (speedup sits in low band) 
o=res["open"][2]
# 2) shape differs per map: knee weight where exp ratio <0.5
def knee(rows): 
    for w,e,r in rows:
        if e/rows[0][1]<0.5: return w
    return None
knees={k:knee(v[2]) for k,v in res.items()}
print("knee weight (exp<50% of w1):",knees)
maxcost={k:max(r for _,_,r in v[2]) for k,v in res.items()}
print("max cost ratio:",maxcost)
shape_differs=len(set(knees.values()))>1 or any(v is None for v in knees.values())
alt_ok=e_a<=e_m and c_a==c_m
print("RESULT: %s knees=%s maxcost=%s ALT exp %d vs %d same cost=%s"%("PASS" if (shape_differs and alt_ok) else "FAIL",knees,{k:round(v,2) for k,v in maxcost.items()},e_a,e_m,c_a==c_m))
