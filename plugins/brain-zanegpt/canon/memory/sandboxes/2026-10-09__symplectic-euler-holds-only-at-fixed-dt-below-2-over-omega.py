import math
W=1.0  # omega; k=m=1
def energy(x,v): return 0.5*v*v+0.5*W*W*x*x
def explicit(x,v,dt): return x+v*dt, v-W*W*x*dt
def semi(x,v,dt):
    v=v-W*W*x*dt; return x+v*dt, v
def run(step,dts,x=1.0,v=0.0):
    e0=energy(x,v); emax=e0; emin=e0
    for dt in dts:
        x,v=step(x,v,dt); e=energy(x,v); emax=max(emax,e); emin=min(emin,e)
        if not math.isfinite(e) or e>1e150: return float('inf'),emin/e0
    return emax/e0,emin/e0
N=2000
# S1 reproduce E1: dt=0.1
ex,_=run(explicit,[0.1]*N); se,_=run(semi,[0.1]*N)
print("S1 dt=0.1 explicit max E/E0=%.3g semi=%.4f"%(ex,se))
# S2 fixed dt sweep around 2/omega (boundary, built to BREAK)
for dt in (1.0,1.9,1.99,2.01,2.5):
    m,_=run(semi,[dt]*N); print("S2 dt=%.2f semi max E/E0=%.4g"%(dt,m))
s2_ok = run(semi,[1.99]*N)[0]<1e3 and run(semi,[2.01]*N)[0]==float('inf')
# S3 variable dt: deterministic schedule alternating 0.1 / 1.9 (mean 1.0) and 0.5/1.5
for name,sched in (("0.1/1.9",[0.1,1.9]*(N//2)),("0.5/1.5",[0.5,1.5]*(N//2)),("fixed1.0",[1.0]*N)):
    m,_=run(semi,sched); print("S3 %s semi max E/E0=%.4g"%(name,m))
v1=run(semi,[0.1,1.9]*(N//2))[0]; v2=run(semi,[1.0]*N)[0]
# S4 fixed-step accumulator over variable frame times restores the bound
def accum(frames,h=0.1):
    x,v,acc=1.0,0.0,0.0; e0=energy(x,v); emax=e0
    for f in frames:
        acc+=f
        while acc>=h-1e-12:
            x,v=semi(x,v,h); acc-=h; emax=max(emax,energy(x,v))
    return emax/e0
a=accum([0.016,0.020]*2000); print("S4 accumulator h=0.1 over 16/20ms frames max E/E0=%.4f"%a)
# determinism: rerun identical
same = run(semi,[0.1,1.9]*(N//2))==run(semi,[0.1,1.9]*(N//2))
ok = ex>1e6 and se<1.06 and s2_ok and v1>v2*10 and a<1.06 and same
print("RESULT: %s semi-implicit bounded at fixed dt=0.1 (%.3f) and dt=1.99, diverges at 2.01; variable dt 0.1/1.9 (mean 1.0) max %.3g vs fixed 1.0 %.3g; fixed-step accumulator %.3f"%("PASS" if ok else "FAIL",se,v1,v2,a))
