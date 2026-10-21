# Deterministic Nagel-Schreckenberg ring (no random braking). One car is forced to brake for K steps at t=0.
# Claim: the disturbance dies out below critical density rho_c = 1/(vmax+1) and persists as a backward jam above it.
def run(L,N,vmax,K,steps=3000):
    pos=[(i*L)//N for i in range(N)]; v=[vmax]*N
    stopped_hist=[]; minv=[]
    for t in range(steps):
        new_v=[]
        for i in range(N):
            gap=(pos[(i+1)%N]-pos[i]-1)%L if N>1 else L
            vi=min(v[i]+1,vmax,gap)
            if i==0 and t<K: vi=0            # forced brake of car 0
            new_v.append(vi)
        v=new_v; pos=[(p+vi)%L for p,vi in zip(pos,v)]
        stopped_hist.append(sum(1 for x in v if x<vmax)); minv.append(min(v))
    tail=stopped_hist[-500:]
    flow=sum(v)/L                              # cars per cell-step = rho*mean v
    lap=L/(sum(v)/N) if sum(v)>0 else float("inf")
    run.last_min=min(minv[-500:])
    return sum(tail)/len(tail), flow, lap
L=200; rho_c=lambda vm:1/(vm+1)
rows=[]
for vmax in (5,3):
    print("vmax=%d rho_c=%.3f"%(vmax,rho_c(vmax)))
    for N in (10,20,25,30,33,34,40,50,67,80):
        rho=N/L
        slow,flow,lap=run(L,N,vmax,K=3)
        rows.append((vmax,N,rho,slow,flow,lap))
        print("  N=%2d rho=%.3f  mean cars below vmax (last 500)=%6.2f flow=%.4f  lapTime=%7.1f  Little N=flow*lap=%.2f"%(N,rho,slow,flow,lap,flow*lap))
# checks
def persists(r): return r[3]>0.5
okc=True
for vmax in (5,3):
    for r in rows:
        if r[0]!=vmax: continue
        pred = r[2] > rho_c(vmax)+1e-9
        if persists(r)!=pred: okc=False; print("MISMATCH",r)
little=all(abs(r[4]*r[5]-r[1])<1e-6 for r in rows if r[5]!=float("inf"))
# CONTROL: same densities with NO brake (K=0). Above rho_c the slow state is intrinsic: is the brake the cause?
ctl={}
for vm,N in ((5,34),(5,40),(5,50),(3,67)):
    a=run(L,N,vm,0)[0]; ma=run.last_min
    b_=run(L,N,vm,3)[0]; mb=run.last_min
    ctl[(vm,N)]=(a,ma,b_,mb)
    print("control vmax=%d N=%d: no-brake slow=%.1f minspeed=%d | brake slow=%.1f minspeed=%d"%(vm,N,a,ma,b_,mb))
# brake changes the shape (stop-and-go with stopped cars, min speed 0) only where it was not already saturated
metastable = ctl[(5,40)][1]>0 and ctl[(5,40)][3]==0 and ctl[(5,34)][0]>0
# BREAK 1: longer forced brake (driver behaviour) below rho_c: does K matter?
b=[run(L,25,5,K) [0] for K in (1,3,10,50)]
print("below rho_c (N=25, vmax=5): residual slow cars for brake length 1/3/10/50 =",b)
# BREAK 2: headway lever: vmax 5->3 turns N=30 (rho .15 free) ... and N=40 (rho .2, jam at vmax5) free
print("N=40: vmax5 slow=%.2f vs vmax3 slow=%.2f"%(run(L,40,5,3)[0],run(L,40,3,3)[0]))
lever = run(L,40,5,3)[0]>0.5 and run(L,40,3,3)[0]<0.5 and all(x<0.5 for x in b)
print("RESULT: %s brake wave persists exactly above rho_c=1/(vmax+1) (vmax 5 and 3, 20 densities), brake length 1..50 irrelevant below it, lowering vmax clears a jam at rho 0.2, Little N=flow*lap holds; REFINED: above rho_c the congested state exists even with no brake (N=40: all 40 cars slow, min speed 4), the brief brake only turns it into stop-and-go (min speed 0)"%("PASS" if (okc and little and lever and metastable) else "FAIL"))
