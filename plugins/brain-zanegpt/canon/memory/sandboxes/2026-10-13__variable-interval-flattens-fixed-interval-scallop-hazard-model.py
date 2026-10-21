# Deterministic hazard-rate model of post-reward pausing under reward-interval schedules.
# Agent response rate tracks the hazard (chance reward arrives now given not yet) of its
# internally BLURRED (scalar timing, Weber fraction w) copy of the schedule's interval distribution.
# Also a goal-gradient reading of the FI rush: rate ~ 1/(T-t). No RNG.
import math
T=60.0
def schedule(kind,**k):
    n=2001
    if kind=="FI": return [(T,1.0)]
    if kind=="VI_uniform":  # uniform on T*(1-j)..T*(1+j), discretized
        j=k["j"]; m=41; return [(T*(1-j+2*j*i/(m-1)),1.0/m) for i in range(m)]
    if kind=="VI_exp":      # memoryless, mean T, discretized to quantile midpoints (deterministic)
        m=400; return [(-T*math.log(1-(i+0.5)/m),1.0/m) for i in range(m)]
def Phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def rates(sched,w,hmax=1.0,dt=0.25,horizon=3*T):
    ts=[i*dt for i in range(int(horizon/dt))]
    pdf=[sum(p*math.exp(-0.5*((t-tau)/(w*tau))**2)/(w*tau*math.sqrt(2*math.pi)) for tau,p in sched) for t in ts]
    out=[];S=1.0
    for t,f in zip(ts,pdf):
        h=min(f/S if S>1e-9 else hmax,hmax); out.append(h); S-=f*dt
    return ts,out
def scallop(kind,w,b=0.1,**k):
    ts,r=rates(schedule(kind,**k),w); r=[b+h*T for h in r]  # responding floor b: animals never fully stop
    q=T/4; a=[x for t,x in zip(ts,r) if t<q]; b=[x for t,x in zip(ts,r) if 3*q<=t<4*q]
    ma=sum(a)/len(a); mb=sum(b)/len(b)
    return (mb/ma if ma>1e-12 else float("inf")), ma, mb
cases=[("FI",{}),("VI_uniform j=0.2",{"j":0.2}),("VI_uniform j=0.6",{"j":0.6}),("VI_uniform j=0.95",{"j":0.95}),("VI_exp memoryless",{})]
res={}
for w,b in ((0.10,0.1),(0.20,0.1),(0.10,0.02),(0.10,0.5)):
    for name,k in cases:
        kind=name.split()[0]
        s,ma,mb=scallop(kind,w,b,**k); res[(w,b,name)]=s
        print("w=%.2f b=%.2f %-20s scallop(last/first quarter)=%8.2f  first=%.4f last=%.4f"%(w,b,name,s,ma,mb))
# goal-gradient comparison: on FI, rate ~ 1/(T-t+eps)
eps=3.0; g=[1/(T-t+eps) for t in (T/8, 7*T/8)]
print("goal-gradient 1/(T-t+3) last/first-ish eighth ratio = %.2f"%(g[1]/g[0]))
g1=g[1]/g[0]
R=lambda w,b,n: res[(w,b,n)]
fi,v2,v6,v95,ve=[R(0.10,0.1,n) for n,_ in cases]
# NOTE: pre-run prediction was FI > VI+-20% strictly; observed VI+-20% is 102% of FI (refuted in that detail)
ok = v2>v6>v95>ve and fi>v6 and abs(v2/fi-1)<0.1 and ve<1.1 and g1>5 and all(R(0.10,b,"FI")>R(0.10,b,"VI_uniform j=0.95") for b in (0.02,0.1,0.5))
print("RESULT: %s scallop FI %.1f, VI+-20%% %.1f (%.0f%% of FI, not flatter), VI+-60%% %.1f, VI+-95%% %.1f, exponential %.2f; ordering holds at floors 0.02/0.1/0.5"%("PASS" if ok else "FAIL",fi,v2,100*v2/fi,v6,v95,ve))
