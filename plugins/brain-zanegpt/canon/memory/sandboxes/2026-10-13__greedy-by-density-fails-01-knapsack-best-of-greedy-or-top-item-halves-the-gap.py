# 0/1 knapsack: greedy by value/weight density vs exact DP vs "best of greedy and single most valuable item". Exhaustive grid, no RNG.
from itertools import product
def dp(items,cap):
    best=[0]*(cap+1)
    for w,v in items:
        for c in range(cap,w-1,-1): best[c]=max(best[c],best[c-w]+v)
    return best[cap]
def greedy(items,cap):
    tot=0;used=0
    for w,v in sorted(items,key=lambda x:-x[1]/x[0]):
        if used+w<=cap: used+=w;tot+=v
    return tot
def fixed(items,cap):
    top=max((v for w,v in items if w<=cap),default=0)
    return max(greedy(items,cap),top)
worst_g=(1.0,None);worst_f=(1.0,None);n_inst=0;n_g_bad=0;n_f_bad=0
for cap in range(5,13):
    for ws in product(range(1,cap+1),repeat=3):
        for vs in product(range(1,13),repeat=3):
            items=list(zip(ws,vs)); opt=dp(items,cap); n_inst+=1
            if opt==0: continue
            g=greedy(items,cap);f=fixed(items,cap)
            if g<opt: n_g_bad+=1
            if f<opt: n_f_bad+=1
            if g/opt<worst_g[0]: worst_g=(g/opt,(cap,items,g,opt))
            if f/opt<worst_f[0]: worst_f=(f/opt,(cap,items,f,opt))
print("instances",n_inst,"greedy suboptimal",n_g_bad,"fixed suboptimal",n_f_bad)
print("worst greedy ratio %.3f"%worst_g[0],worst_g[1]); print("worst fixed ratio %.3f"%worst_f[0],worst_f[1])
# scale test: classic family items (1,2) and (cap, cap-1... ) -> greedy ratio -> 1/cap-ish
fam=[]
for cap in (10,100,1000):
    items=[(1,2),(cap,cap)]            # density 2 vs 1: greedy takes item1 then item2 does not fit
    fam.append((cap,greedy(items,cap)/dp(items,cap),fixed(items,cap)/dp(items,cap)))
print("adversarial family (greedy ratio, fixed ratio):",fam)
# fractional relaxation: greedy with a split last item is optimal
def frac(items,cap):
    tot=0.0;used=0
    for w,v in sorted(items,key=lambda x:-x[1]/x[0]):
        t=min(w,cap-used); tot+=v*t/w; used+=t
    return tot
ok_frac=all(frac([(w,v) for w,v in zip(ws,vs)],cap)>=dp(list(zip(ws,vs)),cap)-1e-9 for cap in (7,10) for ws in product(range(1,cap+1),repeat=3) for vs in product(range(1,9),repeat=3))
ok = n_g_bad>0 and worst_g[0]<0.55 and worst_f[0]>=0.5-1e-9 and fam[-1][1]<0.01 and fam[-1][2]>=0.5 and ok_frac
print("RESULT: %s greedy-by-density suboptimal on %d of %d small 0/1 instances, worst ratio %.3f (family -> %.4f at cap 1000); best-of(greedy, top item) never below %.3f and fails exact optimum on %d; fractional greedy never below DP"%("PASS" if ok else "FAIL",n_g_bad,n_inst,worst_g[0],fam[-1][1],worst_f[0],n_f_bad))
