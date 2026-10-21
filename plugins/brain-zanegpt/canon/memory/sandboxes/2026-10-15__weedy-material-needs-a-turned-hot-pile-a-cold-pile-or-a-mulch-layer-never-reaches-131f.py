# Deterministic pile model: weed seeds (>=131F for 3+ days) and pathogens (>=140F for 3+ days) by zone, turning, pile type.
# Stdlib only, no RNG. Zones: 0=core,1=middle,2=rim; zone temp = core - offset[z]. Turning rotates rim->core.
DAYS=56; OFF=(0,10,25)
def core_temp(day, last_turn, kind):
    if kind=="cold": return 90 if day>=5 else 70+4*day
    if kind=="mulch": return 80                      # thin surface layer decomposing in place, no insulation
    since=day-last_turn
    if since<10: return 150 if (day>=3 or last_turn>0) else 70+27*day  # ramp 3 days, then hold while aerated
    return max(70,150-4*(since-9))                  # oxygen runs out ~10 days after the last turn
def run(kind, turn_every):
    pos=[0,1,2]                                      # zone of each seed batch (A,B,C)
    hot=[[0]*3,[0]*3]; last=0
    for d in range(DAYS):
        if turn_every and d>0 and d%turn_every==0:
            pos=[(p-1)%3 for p in pos]; last=d
        ct=core_temp(d,last,kind)
        off=OFF if kind in("hot","cold") else (0,0,0)
        for i,p in enumerate(pos):
            t=ct-off[p]
            if t>=131: hot[0][i]+=1
            if t>=140: hot[1][i]+=1
    seeds=sum(1 for x in hot[0] if x>=3); path=sum(1 for x in hot[1] if x>=3)
    return seeds,path
cases=[("hot turned every 5d","hot",5),("hot turned every 7d","hot",7),("hot turned every 14d","hot",14),
       ("hot never turned","hot",0),("cold pile","cold",0),("mulch layer 2-4in","mulch",0)]
res={}
for n,k,t in cases:
    res[n]=run(k,t); print(f"{n:22s} seed batches killed {res[n][0]}/3  pathogen batches killed {res[n][1]}/3")
ok=(res["hot turned every 5d"]==(3,3) and res["hot turned every 7d"]==(3,3)
    and res["hot never turned"][0]<3 and res["cold pile"]==(0,0) and res["mulch layer 2-4in"]==(0,0)
    and res["hot turned every 14d"]==(3,3))  # break case: expected 14d to leave the rim cool; it did not (refuted, see proposal)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),"turned hot 5d/7d",res["hot turned every 5d"],res["hot turned every 7d"],"| 14d",res["hot turned every 14d"],"| never",res["hot never turned"],"| cold",res["cold pile"],"| mulch",res["mulch layer 2-4in"])
