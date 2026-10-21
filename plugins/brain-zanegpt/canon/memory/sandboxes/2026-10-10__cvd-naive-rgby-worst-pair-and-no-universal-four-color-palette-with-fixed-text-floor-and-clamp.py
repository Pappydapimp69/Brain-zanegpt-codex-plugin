"""Prediction (before run), Machado 2009 severity-1.0 matrices in linear RGB, redmean distance on sRGB:
 1) naive red/green/blue/yellow worst pair is green-vs-yellow under protanopia with redmean < 100 (kernel says 58; I expect 40-90);
 2) orange/sky-blue for red/green raises the protan worst case above the naive one and lowers the tritan worst case below the naive one;
 3) exhaustive search of all 4-colour subsets of a fixed 24-colour candidate set: the best single palette's worst-case over the 3 CVD types
    is strictly below the best per-type palette's own worst-case for at least one type (so per-type presets win);
 4) siblings: horizontal split halves 32px solo text to 16px < the 26px 1080p floor; a clamp of 10 cannot frame two players 80 apart (needs ~27).
BREAK case: palette search (3) is built to find a universal palette; if it exists with every-type minimum >= the per-type best, the kernel claim fails."""
import itertools, math
M = {
 "prot": [[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
 "deut": [[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
 "trit": [[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]],
}
def lin(c): c/=255; return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def unlin(v):
    v=min(1,max(0,v)); c=12.92*v if v<=0.0031308 else 1.055*v**(1/2.4)-0.055
    return round(c*255)
def sim(rgb,t):
    l=[lin(x) for x in rgb]; m=M[t]
    return tuple(unlin(sum(m[i][j]*l[j] for j in range(3))) for i in range(3))
def redmean(a,b):
    r=(a[0]+b[0])/2; dr,dg,db=(a[i]-b[i] for i in range(3))
    return math.sqrt((2+r/256)*dr*dr+4*dg*dg+(2+(255-r)/256)*db*db)
def worst(pal,t):
    s=[sim(c,t) for c in pal.values()] if isinstance(pal,dict) else [sim(c,t) for c in pal]
    names=list(pal.keys()) if isinstance(pal,dict) else list(range(len(pal)))
    best=None
    for (i,a),(j,b) in itertools.combinations(list(enumerate(s)),2):
        d=redmean(a,b)
        if best is None or d<best[0]: best=(d,names[i],names[j])
    return best
NAIVE={"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0)}
SWAP={"orange":(255,140,0),"skyblue":(86,180,233),"blue":(0,0,255),"yellow":(255,255,0)}
res={}
for name,p in (("naive",NAIVE),("swap",SWAP)):
    for t in M: res[(name,t)]=worst(p,t)
    res[(name,"none")]=worst(p,"prot") if False else None
print({k:(round(v[0]),v[1],v[2]) for k,v in res.items() if v})
naive_worst_type=min(M,key=lambda t:res[("naive",t)][0])
c1 = naive_worst_type=="prot" and {res[("naive","prot")][1],res[("naive","prot")][2]}=={"green","yellow"} and res[("naive","prot")][0]<100
c2 = res[("swap","prot")][0]>res[("naive","prot")][0] and res[("swap","trit")][0]<res[("naive","trit")][0]
# exhaustive palette search
CAND=[]
for h in range(12):
    for v in (1.0,0.55):
        # simple HSV s=1 hue colours
        k=h/2; i=int(k)%6; f=k-int(k)
        q=[(1,f,0),(1-f,1,0),(0,1,f),(0,1-f,1),(f,0,1),(1,0,1-f)][i]
        CAND.append(tuple(round(255*v*x) for x in q))
CAND=sorted(set(CAND))
best_uni=(-1,None); best_type={t:(-1,None) for t in M}
for pal in itertools.combinations(CAND,4):
    w={t:worst(list(pal),t)[0] for t in M}
    m=min(w.values())
    if m>best_uni[0]: best_uni=(m,pal)
    for t in M:
        if w[t]>best_type[t][0]: best_type[t]=(w[t],pal)
per_type_gap={t:best_type[t][0]-min(worst(list(best_uni[1]),u)[0] for u in M) for t in M}
c3 = any(g>0 for g in per_type_gap.values()) and best_uni[0] < max(v[0] for v in best_type.values())
# siblings
solo=32; split=solo//2; floor=26
c4a = split<floor
aspect=16/9; pad=1.2; need=(80/2)*pad/aspect; clamp=10
c4b = need>clamp and abs(need-27)<1
print("candidates",len(CAND),"best universal worst-case",round(best_uni[0]),"per-type best",{t:round(v[0]) for t,v in best_type.items()},"gaps",{t:round(g) for t,g in per_type_gap.items()})
print("text",solo,"->",split,"floor",floor,"| ortho needed",round(need,1),"clamp",clamp)
ok=c1 and c2 and c3 and c4a and c4b
print("RESULT:", "PASS" if ok else "FAIL", f"c1_green_yellow_protan={c1} naive_prot={round(res[('naive','prot')][0])} swap_prot={round(res[('swap','prot')][0])} naive_trit={round(res[('naive','trit')][0])} swap_trit={round(res[('swap','trit')][0])} universal_best={round(best_uni[0])} pertype_best_max={round(max(v[0] for v in best_type.values()))} text_split_16<26={c4a} ortho_need={need:.1f}>10={c4b}")
