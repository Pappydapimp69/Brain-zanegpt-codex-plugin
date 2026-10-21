import math
def pois_pmf(m,N=400):
    p=[math.exp(-m)]
    for k in range(1,N): p.append(p[-1]*m/k)
    return p
def profit(q,pm,p,c,s=0.0,K=0.0):
    e=0.0
    for d,w in enumerate(pm):
        sold=min(q,d); e+=w*(p*sold+s*(q-sold))
    return e-c*q-(K if q>0 else 0)
def best(pm,p,c,s=0,K=0,Q=300):
    return max(range(Q),key=lambda q:profit(q,pm,p,c,s,K))
def frac(pm,cr):
    a=0
    for q,w in enumerate(pm):
        a+=w
        if a>=cr: return q
ok=[]
# S1: no salvage, no fixed cost -> kernel formula equals brute force
for m,p,c in [(2,10,5),(50,10,5.5),(20,10,9.5)]:
    pm=pois_pmf(m); b=best(pm,p,c); f=frac(pm,(p-c)/p); ok.append(b==f); print("S1",m,p,c,b,f)
# S2: salvage s>0: kernel CR=(p-c)/p overorders vs correct (p-c)/(p-s)
m,p,c,s=20,10,6,4; pm=pois_pmf(m)
b=best(pm,p,c,s); fk=frac(pm,(p-c)/p); fs=frac(pm,(p-c)/(p-s))
loss=1-profit(fk,pm,p,c,s)/profit(b,pm,p,c,s)
print("S2 brute",b,"kernel",fk,"salvage-adj",fs,"loss %.2f%%"%(100*loss)); ok.append(fs==b and fk!=b)
# S3 BREAK: fixed order cost K makes ordering at fractile worse than ordering zero
m,p,c,K=2,10,5,15; pm=pois_pmf(m)
fk=frac(pm,(p-c)/p); b=best(pm,p,c,0,K)
print("S3 fractile",fk,"profit",round(profit(fk,pm,p,c,0,K),2),"best",b,"profit",round(profit(b,pm,p,c,0,K),2)); ok.append(b==0 and profit(fk,pm,p,c,0,K)<0)
# S4: mean stocking loss at CR 0.95
for m in (2,50):
    pm=pois_pmf(m); b=best(pm,20,1); print("S4",m,"loss %.1f%%"%(100*(1-profit(m,pm,20,1)/profit(b,pm,20,1))))
print("RESULT: %s fractile exact w/o salvage/fixed cost (S1); salvage shifts CR to (p-c)/(p-s) (S2); fixed cost K=15 makes optimum q=0 (S3)"%("PASS" if all(ok) else "FAIL"))
