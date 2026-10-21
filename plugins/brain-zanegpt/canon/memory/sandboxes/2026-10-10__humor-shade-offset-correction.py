"""Humor-style self-report: does subtracting the known population shade per style fix shaded scores?
Deterministic: people from a Halton-like low-discrepancy grid, no RNG."""
import math
def halton(i,b):
    f,r=1.0,0.0
    while i>0:
        f/=b; r+=f*(i%b); i//=b
    return r
def nrm(u): # inverse-normal approx via logistic
    u=min(max(u,1e-6),1-1e-6); return math.log(u/(1-u))*0.5513
def people(n,gf):
    out=[]
    for i in range(1,n+1):
        g=nrm(halton(i,2))
        out.append([gf*g+(1-gf)*nrm(halton(i,p)) for p in (3,5,7,11)])
    return out
def rank(v):
    o=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
    for k,i in enumerate(o): r[i]=k
    return r
def corr(a,b):
    n=len(a);ma=sum(a)/n;mb=sum(b)/n
    c=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    return c/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
def top(p): return max(range(4),key=lambda i:p[i])
def run(label,gf,shade_mean,shade_spread,fix):
    P=people(400,gf)
    # shade: style 0,1 flattered (+), 2,3 (injurious) denied (-); per-person scale varies (spread)
    rep=[]
    for i,p in enumerate(P):
        s=1+shade_spread*(nrm(halton(i+1,13))) # person susceptibility
        rep.append([p[k]+s*shade_mean[k] for k in range(4)])
    if fix: rep=[[r[k]-sum(shade_mean[j]*1 for j in [k])*1.0 for k in range(4)] for r in rep]
    mis=sum(top(r)!=top(p) for r,p in zip(rep,P))/len(P)
    sp=[corr(rank([r[k] for r in rep]),rank([p[k] for p in P])) for k in range(4)]
    cs_t=corr([p[0] for p in P],[p[2] for p in P]); cs_r=corr([r[0] for r in rep],[r[2] for r in rep])
    print(f"{label:34s} misclass={mis:.3f} rank={sum(sp)/4:.3f} corr02 true={cs_t:.3f} rep={cs_r:.3f}")
    return mis,sum(sp)/4,abs(cs_t-cs_r)
sm=[0.8,0.8,-0.8,-0.8]
res={}
res['raw']=run('1 raw, uniform shade',0.5,sm,0.0,False)
res['fix']=run('1 offset-fixed, uniform shade',0.5,sm,0.0,True)
res['rawv']=run('2 raw, variable shade',0.5,sm,0.6,False)
res['fixv']=run('2 offset-fixed, variable shade',0.5,sm,0.6,True)  # BREAK: susceptibility varies
res['fixvg']=run('3 offset-fixed, var shade, gf=.8',0.8,sm,0.6,True)
ok = res['fix'][0]<1e-9 and res['fixv'][0]>res['fix'][0]+0.05 and res['fixv'][0]<res['rawv'][0]
print(f"RESULT: {'PASS' if ok else 'FAIL'} offset fix exact when shade uniform (mis {res['fix'][0]:.3f}) but leaves {res['fixv'][0]:.3f} vs raw {res['rawv'][0]:.3f} when susceptibility varies")
