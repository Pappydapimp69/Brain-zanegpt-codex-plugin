# Same content, different reveal order (gap = discourse, not content), ranked on IPM vs IPM*D1.
# Prediction (before run): variants A=gap opened at 2s resolved honestly at 25s; B=gap opened at 2s, payoff misrepresents the game
# (bait); C=no gap (content shown in story order). Expected: IPM alone ranks B first in >=80% of 40 seeded 2000-impression runs
# (curiosity lift keeps viewers to the end, bait inflates install intent); IPM*D1 ranks A first in >=80%; with the bait D1 penalty
# set to 1.0 (no cost) both rankings pick B in >=80%. Hidden assumption: bait costs D1 and not conversion.
# Break: gap opened but never resolved inside the 30s film (late close at 40s) -> A should lose its edge to C on IPM*D1.
import random
SEC=30
def run_variant(rng, n, v):
    inst=0; ret=0
    for _ in range(n):
        alive=True
        for t in range(SEC):
            gap_open = v["open"] is not None and v["open"]<=t<v["close"]
            h = v["h_open"] if gap_open else v["h_base"]
            if rng.random()<h: alive=False; break
        if not alive: continue
        # viewer reached the end: converts with p; bait raises p
        if rng.random()<v["cr"]:
            inst+=1
            if rng.random()<v["d1"]: ret+=1
    return inst, ret
VARS={
 "A_honest_gap":dict(open=2,close=25,h_open=0.006,h_base=0.03,cr=0.10,d1=0.30),
 "B_bait_gap":  dict(open=2,close=25,h_open=0.006,h_base=0.03,cr=0.14,d1=0.30*0.55),
 "C_no_gap":    dict(open=None,close=0,h_open=0,h_base=0.03,cr=0.10,d1=0.30),
}
def trial(seed, n, vars_):
    rng=random.Random(seed); ipm={}; ipmd1={}
    for k,v in vars_.items():
        inst,ret=run_variant(rng,n,v); ipm[k]=inst/n*1000; ipmd1[k]=ret/n*1000
    return max(ipm,key=ipm.get), max(ipmd1,key=ipmd1.get)
def share(vars_, n, runs=40):
    a=b=0
    res=[trial(s,n,vars_) for s in range(runs)]
    return res
out={}
for n in (300,2000):
    res=share(VARS,n)
    out[n]=(sum(r[0]=="B_bait_gap" for r in res)/40, sum(r[1]=="A_honest_gap" for r in res)/40)
    print("n=%d IPM picks B %.2f ; IPM*D1 picks A %.2f"%(n,*out[n]))
free=dict(VARS); free["B_bait_gap"]=dict(VARS["B_bait_gap"],d1=0.30)
res=share(free,2000); freeB=sum(r[1]=="B_bait_gap" for r in res)/40
print("no-cost bait: IPM*D1 picks B %.2f"%freeB)
late=dict(VARS); late["A_honest_gap"]=dict(VARS["A_honest_gap"],close=40)
res=share(late,2000); lateA=sum(r[1]=="A_honest_gap" for r in res)/40
print("late-close (40s) IPM*D1 picks A %.2f"%lateA)
ok = out[2000][0]>=0.8 and out[2000][1]>=0.8 and freeB>=0.8 and lateA<0.5
print("RESULT:","PASS" if ok else "FAIL","n=2000 IPM->B %.2f, IPM*D1->A %.2f; n=300 %.2f/%.2f; free-bait ->B %.2f; late-close ->A %.2f"%(out[2000][0],out[2000][1],out[300][0],out[300][1],freeB,lateA))
