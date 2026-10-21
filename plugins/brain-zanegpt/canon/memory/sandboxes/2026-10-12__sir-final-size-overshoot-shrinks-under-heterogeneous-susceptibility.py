# PREDICTION (before run): homogeneous: z(R0=2)=0.797, z(1.1)=0.176, peak cumulative infection = HIT within 1e-3.
# Heterogeneous susceptibility (half pop s=1.8, half s=0.2, same R0_eff=2): final size well below 0.797 (<0.70) and
# cumulative infected at the I peak below HIT=0.5 -- so the homogeneous overshoot table is NOT safe for burden quoting.
import math
def final(R0):
    lo,hi=1e-9,1.0
    for _ in range(200):
        m=(lo+hi)/2
        if m-1+math.exp(-R0*m)<0: lo=m
        else: hi=m
    return (lo+hi)/2
def rk4(R0,groups,I0=1e-6,dt=0.01,T=400):
    # groups: [(weight, susceptibility)], beta*mean-s2 normalised so growth rate matches R0
    S=[w*(1-I0) for w,s in groups]; I=I0; R=0.0
    norm=sum(w*s*s for w,s in groups)/sum(w*s for w,s in groups)
    b=R0/norm
    def f(S,I):
        lam=b*I
        dS=[-lam*s*Si for Si,(w,s) in zip(S,groups)]
        return dS, -sum(dS)-I
    peakI=0; cum_at_peak=0; n=int(T/dt)
    for _ in range(n):
        k1=f(S,I)
        k2=f([a+dt/2*d for a,d in zip(S,k1[0])],I+dt/2*k1[1])
        k3=f([a+dt/2*d for a,d in zip(S,k2[0])],I+dt/2*k2[1])
        k4=f([a+dt*d for a,d in zip(S,k3[0])],I+dt*k3[1])
        S=[a+dt/6*(p+2*q+2*r+u) for a,p,q,r,u in zip(S,k1[0],k2[0],k3[0],k4[0])]
        I+=dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        if I>peakI: peakI=I; cum_at_peak=1-sum(S)
    return 1-sum(S), cum_at_peak
ok=True
for R0 in (2.0,1.1):
    z=final(R0); zr,cp=rk4(R0,[(1.0,1.0)])
    print("homog R0",R0,"z %.3f rk4 %.3f cum@peak %.3f HIT %.3f"%(z,zr,cp,1-1/R0))
    ok&=abs(z-zr)<1e-3
    if R0==2.0: ok&=abs(z-0.797)<1e-3 and abs(cp-0.5)<1e-2
zh,cph=rk4(2.0,[(0.5,1.8),(0.5,0.2)])
mean_s=0.5*1.8+0.5*0.2; es2=0.5*1.8**2+0.5*0.2**2
print("hetero R0_eff 2: final %.3f cum@peak %.3f (homog 0.797 / 0.500); E[s^2]=%.2f"%(zh,cph,es2))
ok&=zh<0.70 and cph<0.45
# mild heterogeneity: should be close
zm,cm=rk4(2.0,[(0.5,1.1),(0.5,0.9)]); print("mild hetero final %.3f cum@peak %.3f"%(zm,cm)); ok&=0.78<zm<0.80
print("RESULT: %s homogeneous final size 0.797 matches RK4 to 1e-3 but strong heterogeneity at the same R0 gives %.3f (peak cum %.3f vs HIT 0.5); mild gives %.3f"%("PASS" if ok else "FAIL",zh,cph,zm))
