# Composition: ad-length crossover (cut keeps ending?) x IPM*D1 ranking x engine variety.
# Prediction (written before run): with a truncated 15s cut (loses fixable-fail ending -> D1 x0.7),
# IPM alone picks the 15s cut for every drop-off rate d>=1.5%/s, IPM*D1 picks the 30s master for d in 1..4%/s
# (crossover ~4.6%/s), so the two rankings disagree on >=3 of 8 grid drop-offs. Hidden assumption: cut D1 penalty is
# independent of comic engine. Break case: engine fatigue 5%/repeat on the reskinned top engine.
import random
def comp(d, L): return (1-d)**L
def ipm(d, L, cr): return 1000*comp(d, L)*cr
def d1(keep_end, base=0.30): return base if keep_end else base*0.7
def score(v, d): return ipm(d, v["L"], v["cr"])*d1(v["end"])*v["fat"]
def best(vs, d, key):
    return max(vs, key=lambda v: key(v, d))["name"]
DS = [0.01,0.02,0.03,0.04,0.05,0.06,0.08,0.10]
def batch(engines, fat_per_repeat, cut_end):
    vs=[]; seen={}
    for e, cr in engines:
        n=seen.get(e,0); seen[e]=n+1; fat=(1-fat_per_repeat)**n
        vs.append(dict(name=f"{e}#{n}-30",L=30,cr=cr,end=True,fat=fat))
        vs.append(dict(name=f"{e}#{n}-15",L=15,cr=cr*1.0,end=cut_end,fat=fat))
    return vs
diverse=[("a",.020),("b",.018),("c",.017),("d",.016)]
reskin=[("a",.020)]*4
res={}
# S1 truncated cut, diverse
vs=batch(diverse,0.0,False)
dis=sum(best(vs,d,lambda v,d:ipm(d,v["L"],v["cr"]))!=best(vs,d,score) for d in DS)
print("S1 truncated-cut rank disagreements IPM vs IPM*D1:",dis,"of",len(DS))
ipm_pick=[best(vs,d,lambda v,d:ipm(d,v["L"],v["cr"])) for d in DS]
d1_pick=[best(vs,d,score) for d in DS]
print(" ipm picks",ipm_pick); print(" ipm*d1 picks",d1_pick)
# S2 cut keeps ending: rankings should agree
vs2=batch(diverse,0.0,True)
dis2=sum(best(vs2,d,lambda v,d:ipm(d,v["L"],v["cr"]))!=best(vs2,d,score) for d in DS)
print("S2 ending-kept disagreements:",dis2)
# S3 break: reskin top engine with 5% fatigue vs diverse; total batch value of top-4 by IPM*D1 at d=0.03
def topval(vs,d,k=4):
    s=sorted((score(v,d) for v in vs),reverse=True); return sum(s[:k])
a=topval(batch(reskin,0.05,False),0.03); b=topval(batch(diverse,0.0,False),0.03)
print("S3 reskin5%% top4 value %.3f vs diverse %.3f"%(a,b))
# S4 flat: truncated cut at D1 penalty 0 -> no disagreement
orig=d1
def d1(keep_end, base=0.30): return base
dis4=sum(best(vs,d,lambda v,d:ipm(d,v["L"],v["cr"]))!=best(vs,d,score) for d in DS)
print("S4 flat-D1 disagreements:",dis4)
ok = dis>=3 and dis2==0 and dis4==0 and a<b
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"truncated-cut disagreements {dis}/8, ending-kept {dis2}, flat-D1 {dis4}, reskin {a:.3f} vs diverse {b:.3f}")
