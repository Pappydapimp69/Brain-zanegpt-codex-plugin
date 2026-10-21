# Settling the open fork: when should a held selector release on a veto? Deterministic 40-tick toy, switch cost 3.
T=40; COST=3
def run(policy, refused, start="A"):
    cur=start; work=0; switches=0; busy_until=-1; hist=[]; streak=0
    for t in range(T):
        if t<busy_until: continue
        r=refused(cur,t); hist.append(r); hist=hist[-6:]
        streak = streak+1 if r else 0
        if r:
            if policy(hist,streak):
                cur="B" if cur=="A" else "A"; switches+=1; busy_until=t+COST; hist=[]; streak=0
            continue
        work+=1
    return work, switches
HOLD=lambda h,s: False
FIRST=lambda h,s: True
MARGIN=lambda h,s: sum(h)>=3 and sum(h)>len(h)-sum(h)
def RUN(k): return lambda h,s: s>=k
pols={"HOLD":HOLD,"FIRST":FIRST,"MARGIN":MARGIN,"RUN2":RUN(2),"RUN3":RUN(3),"RUN4":RUN(4)}
def block(L,start=5): return lambda c,t: c=="A" and start<=t<start+L
sc={
 "permanent block A":      lambda c,t: c=="A",
 "transient 2":            block(2),
 "transient 3":            block(3),
 "transient 5":            block(5),
 "transient 12":           block(12),
 "both noisy 1-in-4":      lambda c,t: t%4==0,
 "A noisy, B free":        lambda c,t: c=="A" and t%4==0,
 "A blocked, B busy to 20":lambda c,t: (c=="A") or (c=="B" and t<20),
}
tab={}
print(f"{'scenario':26}"+"".join(f"{n:>12}" for n in pols))
for s,f in sc.items():
    row={n:run(p,f) for n,p in pols.items()}; tab[s]=row
    print(f"{s:26}"+"".join(f"{row[n][0]:>7}/{row[n][1]:<4}" for n in pols))
wins={n:sum(1 for s in sc if tab[s][n][0]==max(v[0] for v in tab[s].values())) for n in pols}
loss={n:sum(max(v[0] for v in tab[s].values())-tab[s][n][0] for s in sc) for n in pols}
print("best-or-tied scenarios:",wins); print("total work lost vs best:",loss)
best=min(loss,key=loss.get)
dominated = all(tab[s][best][0]==max(v[0] for v in tab[s].values()) for s in sc)
print("minimum-loss policy:",best,"dominates every scenario:",dominated)
ok = tab["permanent block A"]["HOLD"][0]==0 and tab["permanent block A"]["FIRST"][0]>20 and (not dominated)
print("RESULT:","PASS" if ok else "FAIL",f"no release rule dominates: {wins}; lowest total loss {best}={loss[best]}; HOLD livelocks (0 work) on a permanent block; both-noisy: FIRST {tab['both noisy 1-in-4']['FIRST']} vs RUN3 {tab['both noisy 1-in-4']['RUN3']}")
