"""Sandbox: multi-signature book plan + folded-signature imposition (stdlib, deterministic)."""
def impose(n):  # sheet faces of a fold-in-half signature of n pages: outer sheet first; returns list of (a,b) facing-on-sheet-face pairs
    faces=[]
    for i in range(n//4):
        lo, hi = 1+2*i, n-2*i
        faces.append((hi, lo)); faces.append((lo+1, hi-1))
    return faces
def plan_greedy(P, sizes):
    out=[]; left=P
    for s in sorted(sizes, reverse=True):
        while left>=s: out.append(s); left-=s
    if left>0: out.append(min(s for s in sizes if s>=left) if any(s>=left for s in sizes) else min(sizes))
    return out
def plan_dp(P, sizes):
    best={0:(0,[])}
    for p in range(1,P+sizes[0]*2+1):
        cands=[(best[p-s][0]+0,best[p-s][1]+[s]) for s in sizes if p-s>=0 and (p-s) in best]
        if cands: best[p]=min(cands,key=lambda c:(len(c[1]),))
    tot=min(t for t in best if t>=P and (t-P)<min(sizes)*3)  # fewest blanks, then fewest signatures
    tot=min((t for t in best if t>=P),key=lambda t:(t-P,len(best[t][1])))
    return best[tot][1]
# 1) local rule across all signature sizes
local_ok=all(a+b==n+1 for n in (4,8,12,16,32) for a,b in impose(n))
# 2) global rule across a plan: facing pairs in global page numbers
def global_sums(plan):
    off=0; sums=set()
    for n in plan:
        for a,b in impose(n): sums.add(a+b+2*off)
        off+=n
    return sums
g=global_sums([8,8,8]); gl=global_sums([8])
# 3) greedy vs DP on chain sizes and non-chain sizes
def blanks(plan,P): return sum(plan)-P
chain=(32,16,8,4); nonchain=(12,16)
bad_chain=sum(1 for P in range(1,200) if blanks(plan_greedy(P,chain),P)!=(-P)%4)
worse=sum(1 for P in range(1,200) if blanks(plan_greedy(P,nonchain),P)>blanks(plan_dp(P,nonchain),P))
print(f"local sum n+1 holds for every size: {local_ok}; one signature sums {sorted(gl)}, three 8-page signatures sum {sorted(g)}")
print(f"greedy off minimum on chain sizes (1..199 pages): {bad_chain}; greedy worse than DP on sizes (12,16): {worse} of 199")
ok = local_ok and len(g)>1 and len(gl)==1 and bad_chain==0 and worse>0
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" local sum constant per signature, global sums {sorted(g)} over 3 signatures; greedy chain misses {bad_chain}/199; non-chain greedy worse {worse}/199")
