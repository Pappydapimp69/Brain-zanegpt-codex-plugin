# 365-day faucet/sink model, 100 players. Each day each player earns FAUCET coins. Sinks:
#  flat: each player spends min(wealth, FLAT) per day (fixed crafting fee, kernel "flat fees")
#  prop: each player spends RATE * wealth per day (percentage cost, kernel "percentage costs scale")
# Coverage = sink volume / faucet volume in the LAST 30 days. Price index = mean wealth / mean wealth at day 30.
# Prediction (written first): flat sinks at coverage 80% -> wealth grows without bound (index > 5 by day 365),
# 95% -> index > 2, 100-105% -> bounded (index < 1.5); proportional sinks reach coverage 100.0% at ANY faucet
# level, so the coverage ratio cannot distinguish healthy from inflated and the equilibrium wealth FAUCET/RATE does.
N=100; DAYS=365; FAUCET=100.0
def sim(kind,param):
    w=[0.0]*N; hist=[]; fa=sk=0.0; log=[]
    for d in range(DAYS):
        tot_f=tot_s=0.0
        for i in range(N):
            w[i]+=FAUCET; tot_f+=FAUCET
            s=min(w[i],param) if kind=="flat" else param*w[i]
            w[i]-=s; tot_s+=s
        log.append((tot_f,tot_s,sum(w)/N))
    last=log[-30:]; cov=sum(x[1] for x in last)/sum(x[0] for x in last)
    base=log[29][2] or 1.0
    return cov,log[-1][2]/base,log[-1][2]
print("kind param coverage wealth_index final_wealth")
res={}
for cov in (0.80,0.95,1.00,1.05,1.20):
    r=sim("flat",FAUCET*cov); res[("flat",cov)]=r; print("flat %.2f %.3f %.2f %.1f"%((cov,)+r))
for rate in (0.05,0.10,0.50):
    r=sim("prop",rate)
    res[("prop",rate)]=r; print("prop %.2f %.3f %.2f %.1f"%((rate,)+r))
c1=res[("flat",0.80)][1]>5 and res[("flat",0.95)][1]>2
c2=all(res[("flat",c)][1]<1.5 for c in (1.00,1.05,1.20))
# BREAK: proportional sinks all report coverage ~1.0 yet very different wealth levels
cp=[res[("prop",r)] for r in (0.05,0.10,0.50)]
c3=all(abs(c[0]-1)<0.02 for c in cp) and cp[0][2]/cp[2][2]>5
# starvation side: flat 120% -> wealth pinned at 0 leftover
c4=res[("flat",1.20)][2]==0.0
print("RESULT: %s flat sinks: cov80 index %.1f, cov95 %.1f, cov100/105/120 bounded (%s, wealth at 120%% = %.1f starving=%s); proportional sinks read coverage %.3f/%.3f/%.3f but equilibrium wealth %.0f/%.0f/%.0f (%s)"%(
 "PASS" if c1 and c2 and c3 and c4 else "FAIL",res[("flat",0.80)][1],res[("flat",0.95)][1],c2,res[("flat",1.20)][2],c4,cp[0][0],cp[1][0],cp[2][0],cp[0][2],cp[1][2],cp[2][2],c3))
