# Sandbox: three "turn the knob" problems, each with a closed-form floor/ceiling. Does the closed form
# predict what a brute-force knob sweep finds? (a) dilution steps vs pipette floor, (b) thermostat band vs lag,
# (c) solder dwell vs steady-state ceiling.
from collections import deque
import math
R=0.005
def dil(n,a,F=1000.0,VF=1000.0):
    f=F**(1/n); vt=VF/f; return n*(max(R,a/vt)+R*(VF-vt)/VF)
# (a) closed form: 2 steps beat 1 step once a exceeds a* where one-step error crosses two-step error (a/1 > R region)
def a_star():
    lo,hi=0.0,1.0
    for _ in range(60):
        m=(lo+hi)/2
        (lo,hi)=(m,hi) if dil(2,m)>=dil(1,m) else (lo,m)
    return (lo+hi)/2
astar=a_star()
grid=[i*0.002 for i in range(0,41)]
a_ok=sum((min((1,2,3,6),key=lambda n:dil(n,a))!=1)==(a>astar) for a in grid)
# (b) thermostat floor = 2*rate*lag (overshoot above and below), swing = band + floor
def swing(band,lag,rate,secs=12000):
    T=20.0; on=True; buf=deque([T]*lag); out=[]
    for t in range(secs):
        buf.append(T); seen=buf.popleft()
        if on and seen>=20+band: on=False
        elif (not on) and seen<=20: on=True
        T+= rate if on else -rate
        if t>secs//2: out.append(T)
    return max(out)-min(out)
b_cells=[(band,lag,rate) for band in (0.25,1.0) for lag in (60,120,240) for rate in (0.002,0.005,0.01)]
b_ok=sum(abs(swing(*c)-(c[0]+2*c[1]*c[2]))<0.05+2*c[2] for c in b_cells)
# (c) solder pad: dT/dt=(Tss-T)/tau, Tss=Tpre+(tip-Tpre)*0.5, liquidus 217: melts iff Tss>217
def melts(tip,pre,dwell,tau=3.0,liq=217.0):
    Tss=pre+(tip-pre)*0.5; T=pre
    for _ in range(int(dwell*10)):
        T+= (Tss-T)/tau*0.1
        if T>=liq: return True
    return False
c_cells=[(tip,pre,dw) for tip in (350,400,450) for pre in (25,100,150) for dw in (5,20,60)]
def pred_melts(tip,pre,dwell,tau=3.0,liq=217.0):
    Tss=pre+(tip-pre)*0.5
    return Tss>liq and dwell>=tau*math.log((Tss-pre)/(Tss-liq))
c_ok=sum(melts(*c)==pred_melts(*c) for c in c_cells)
never_ok=sum((not melts(*c)) for c in c_cells if (c[1]+(c[0]-c[1])*0.5)<=217.0)
never_n=sum(1 for c in c_cells if (c[1]+(c[0]-c[1])*0.5)<=217.0)
naive_miss=sum(melts(*c)!=((c[1]+(c[0]-c[1])*0.5)>217.0) for c in c_cells)
print(f"a*={astar:.4f} uL: sweep agrees in {a_ok}/{len(grid)} cells; thermostat floor 2*rate*lag agrees {b_ok}/{len(b_cells)}; solder steady state plus dwell formula agrees {c_ok}/{len(c_cells)} (steady-state alone missed {naive_miss}; below-liquidus never melts {never_ok}/{never_n})")
# BREAK: a short dwell with Tss just above liquidus should NOT melt yet, so closed form needs dwell >> tau
brk=melts(450,150,0.5)
print("break (Tss 300 > 217 but 0.5 s dwell):", "melts" if brk else "does not melt yet")
ok = a_ok==len(grid) and b_ok==len(b_cells) and c_ok==len(c_cells) and never_ok==never_n and naive_miss>0 and not brk
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" closed form matched the sweep: dilution {a_ok}/{len(grid)}, thermostat {b_ok}/{len(b_cells)}, solder {c_ok}/{len(c_cells)}; steady state alone missed {naive_miss} short-dwell cells, below-liquidus never melts {never_ok}/{never_n}; a* is {astar:.4f} uL")
