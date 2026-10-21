import random
# 8 ad variants of one concept per trial. Each has 4 beats; a beat introduces a new thing that is either
# derived from the game (legit) or foreign (second game). Variants with a foreign thing ("X") get an IPM novelty
# boost but their installs do not find the advertised game, so true D1 collapses.
def trial(r):
    vs=[]
    for _ in range(8):
        new=[r.random()<0.5 for _ in range(4)]            # beat names a new noun
        derived=[n and r.random()<0.6 for n in new]       # of those, follows from the game
        foreign=any(n and not d for n,d in zip(new,derived))
        base=r.uniform(0.8,1.2)                            # underlying quality
        ipm=base*(1.25 if foreign else 1.0)*r.uniform(0.95,1.05)
        d1=base*(0.35 if foreign else 1.0)
        naive_flag=any(new); fixed_flag=foreign
        vs.append(dict(ipm=ipm,d1=d1,true=base*(0.35 if foreign else 1.0),naive=naive_flag,fixed=fixed_flag,base=base))
    return vs
def pick(vs,gate):
    pool=[v for v in vs if not (gate and v[gate])] or vs
    return max(pool,key=lambda v:v["ipm"])               # rank on IPM only at first impressions (D1 unseen)
def pick_d1(vs,gate):
    pool=[v for v in vs if not (gate and v[gate])] or vs
    return max(pool,key=lambda v:v["ipm"]*v["d1"])
def score(seed,n=3000,fn=pick):
    r=random.Random(seed); out={None:0,"naive":0,"fixed":0}; best=0
    for _ in range(n):
        vs=trial(r); best+=max(v["true"] for v in vs)
        for g in out: out[g]+=fn(vs,g)["true"]
    return {g:v/best for g,v in out.items()}
a=score(11); b=score(12); c=score(11,fn=pick_d1)
print("IPM-only rank, share of oracle value:",{k:round(v,3) for k,v in a.items()})
print("seed12:",{k:round(v,3) for k,v in b.items()}," IPM*D1 rank seed11:",{k:round(v,3) for k,v in c.items()})
ok = a["fixed"]>a[None]+0.1 and b["fixed"]>b[None]+0.1 and a["fixed"]>a["naive"] and c[None]>=0.9 and c["fixed"]-c[None]<a["fixed"]-a[None]
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" IPM-only: none {a[None]:.3f} naive-gate {a['naive']:.3f} fixed-gate {a['fixed']:.3f}; once D1 is in the rank the gate adds {c['fixed']-c[None]:.3f}")
