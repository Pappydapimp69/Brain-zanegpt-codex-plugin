import random, math
# Pick the top of 8 ad variants by measured IPM (conversions/impressions). Batch A: 8 reskins of one engine
# (true IPM spread small, sd 0.05 around 1.0). Batch B: 8 different engines (spread sd 0.25 around 1.0).
# Measure: winner's-curse (measured - true of the pick) and regret vs the oracle pick, by impressions.
def binom(r,n,p):
    # exact via sum of Bernoulli for small n, normal approx for big n (deterministic given seed)
    if n<=400: return sum(r.random()<p for _ in range(n))
    m=n*p; s=math.sqrt(n*p*(1-p)); return max(0,round(r.gauss(m,s)))
def study(sd, n, seed, trials=1500, base=0.04):
    r=random.Random(seed); curse=0; regret=0; gain=0
    for _ in range(trials):
        true=[base*max(0.2,r.gauss(1.0,sd)) for _ in range(8)]
        meas=[binom(r,n,p)/n for p in true]
        i=max(range(8),key=lambda k:meas[k]); o=max(range(8),key=lambda k:true[k])
        curse+=(meas[i]-true[i])/base; regret+=(true[o]-true[i])/base; gain+=(true[i]-sum(true)/8)/base
    return curse/trials, regret/trials, gain/trials
rows={}
for name,sd in (("reskin",0.05),("diverse",0.25)):
    for n in (300,1000,5000):
        rows[(name,n)]=study(sd,n,7)
        c,rg,g=rows[(name,n)]; print(f"{name:8s} n={n:5d} curse={c:+.3f} regret={rg:.3f} gain-over-mean={g:+.3f}")
# claims: at small n the reskin batch picks mostly noise (gain tiny, curse big relative to gain), diverse gets real gain.
res_small=rows[("reskin",300)]; div_small=rows[("diverse",300)]; res_big=rows[("reskin",5000)]
ok = res_small[2]<0.5*div_small[2] and res_small[0]>res_small[2]*2 and res_big[0]<res_small[0] and div_small[2]>0.1
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" at n=300 reskin gain {res_small[2]:+.3f} vs curse {res_small[0]:+.3f}; diverse gain {div_small[2]:+.3f}; reskin curse falls to {res_big[0]:+.3f} at n=5000")
