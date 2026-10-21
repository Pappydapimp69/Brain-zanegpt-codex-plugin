# Rebuild: independent wall-open density vs connectivity guarantee. Own fixture: 12x12 and 20x20 grids, LCG seeds 1..200.
def lcg(seed):
    s = seed * 2654435761 % 2**32
    while True:
        s = (s * 1664525 + 1013904223) % 2**32
        yield s / 2**32
def edges(n):
    return [((r,c),(r,c+1)) for r in range(n) for c in range(n-1)] + [((r,c),(r+1,c)) for r in range(n-1) for c in range(n)]
def reach(n, open_edges):
    adj = {}
    for a,b in open_edges: adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    seen={(0,0)}; st=[(0,0)]
    while st:
        x=st.pop()
        for y in adj.get(x,[]):
            if y not in seen: seen.add(y); st.append(y)
    return len(seen)
def indep(n, p, seed):
    g=lcg(seed); return [e for e in edges(n) if next(g)<p]
def dfs_tree(n, seed):
    g=lcg(seed); seen={(0,0)}; st=[(0,0)]; out=[]
    while st:
        x=st[-1]; nb=[(x[0]+dr,x[1]+dc) for dr,dc in ((0,1),(1,0),(0,-1),(-1,0)) if 0<=x[0]+dr<n and 0<=x[1]+dc<n and (x[0]+dr,x[1]+dc) not in seen]
        if not nb: st.pop(); continue
        y=nb[int(next(g)*len(nb))]; seen.add(y); out.append((x,y)); st.append(y)
    return out
res={}
for n in (12,20):
    E=len(edges(n)); pm=(n*n-1)/E
    full=0; fr=[]
    for s in range(1,201):
        o=indep(n,pm,s); r=reach(n,o); fr.append(r/(n*n)); full+= r==n*n
    tree_ok=all(reach(n,dfs_tree(n,s))==n*n for s in range(1,201))
    # break attempt: raise density until independent walls connect everything in all seeds
    need=None
    for p10 in range(5,100):
        p=p10/100
        if all(reach(n,indep(n,p,s))==n*n for s in range(1,201)): need=p; break
    print(f"n={n} matched p={pm:.3f} full={full}/200 meanReach={sum(fr)/200:.3f} minReach={min(fr):.3f} tree_all_connected={tree_ok} p_for_200_of_200={need}")
    res[n]=(full,sum(fr)/200,tree_ok,need)
ok = all(v[0]==0 and v[2] for v in res.values()) and all(v[3] is None or v[3] > 0.5 for v in res.values())
print("RESULT: %s matched-density independent walls never fully connected in 200 seeds (n=12 reach %.2f, n=20 reach %.2f), DFS tree always connected; independent walls need p=%s (n=12) / %s (n=20) for 200/200, far above the matched density" % ("PASS" if ok else "FAIL", res[12][1], res[20][1], res[12][3], res[20][3]))
