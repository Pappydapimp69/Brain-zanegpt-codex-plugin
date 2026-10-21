# Prediction (before run): on a 6-node DAG with ties, a rank-pull force layout driven by toposort index gives
# node positions that depend on declaration order when ties are broken by declaration order (>=3 distinct
# layouts over all 720 permutations; some node moves > 1 unit) and exactly 1 layout with lexicographic
# tie-break. BREAK: a graph with a total order (chain) has no ties, so both tie-breaks give 1 layout.
import itertools, math
EDGES = [("a","c"),("b","c"),("c","d"),("c","e"),("d","f"),("e","f")]
NODES = ["a","b","c","d","e","f"]
def toposort(decl, edges, mode):
    indeg = {n:0 for n in decl}
    for u,v in edges: indeg[v]+=1
    ready = [n for n in decl if indeg[n]==0]; out=[]
    while ready:
        n = min(ready) if mode=="lex" else ready[0]
        ready.remove(n); out.append(n)
        for u,v in edges:
            if u==n:
                indeg[v]-=1
                if indeg[v]==0: ready.append(v)
    return out
def layout(order, edges, steps=200):
    rank = {n:i for i,n in enumerate(order)}
    # 1D deterministic: x starts at declared (alphabetical) slot, spring edges + rank-pull to rank*1.0
    x = {n: float(i)*0.3 for i,n in enumerate(sorted(rank))}
    for _ in range(steps):
        f = {n:0.0 for n in x}
        for n in x: f[n] += 0.2*(rank[n]-x[n])           # rank pull
        for u,v in edges:
            d = x[v]-x[u]; f[u]+=0.02*(d-1); f[v]-=0.02*(d-1)  # edge spring rest 1
        for n in x: x[n]+=f[n]
    return {n:round(x[n],3) for n in x}
def study(edges, nodes, mode):
    seen = {}
    for perm in itertools.permutations(nodes):
        lay = layout(toposort(list(perm), edges, mode), edges)
        seen.setdefault(tuple(sorted(lay.items())), 0); seen[tuple(sorted(lay.items()))]+=1
    ks = list(seen)
    maxmove = max(max(abs(dict(a)[n]-dict(b)[n]) for n in nodes) for a in ks for b in ks)
    return len(ks), round(maxmove,3)
d_n, d_m = study(EDGES, NODES, "decl")
l_n, l_m = study(EDGES, NODES, "lex")
print("S1 declared tie-break: %d distinct layouts, max node move %.3f" % (d_n, d_m))
print("S2 lexicographic tie-break: %d distinct layouts, max node move %.3f" % (l_n, l_m))
CH = [("a","b"),("b","c"),("c","d"),("d","e"),("e","f")]
c_n, c_m = study(CH, NODES, "decl")
print("S3 BREAK chain (no ties) declared tie-break: %d layouts, max move %.3f" % (c_n, c_m))
ok = d_n >= 3 and d_m > 1.0 and l_n == 1 and c_n == 1
print("RESULT: %s rank-pull layout over 720 declaration orders: declared tie-break %d layouts (max move %.2f), lexicographic %d, tie-free chain %d"
      % ("PASS" if ok else "FAIL", d_n, d_m, l_n, c_n))
