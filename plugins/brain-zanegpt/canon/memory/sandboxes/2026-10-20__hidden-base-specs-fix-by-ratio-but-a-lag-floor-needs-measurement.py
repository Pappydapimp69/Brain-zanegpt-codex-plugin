# Sandbox: three "quoted setting hides its base" cases; which ones can be corrected by a ratio?
from collections import deque
# 1) cure dose: ppm nitrite = pct * nitrite_fraction * meat / base
def ppm(pct, meat, base): return pct/100*0.0625*1e6*meat/base
spec = ppm(0.25, 1000, 1000)                       # 156.25 ppm when base = meat
errs=[]
for brine in (0,0.1,0.25,0.5):
    base=1000*(1+brine); got=ppm(0.25,1000,base)    # dose weighed on total
    fixed=got*base/1000                              # ratio correction on base
    errs.append((abs(got-spec)/spec, abs(fixed-spec)/spec))
dose_raw=max(e[0] for e in errs); dose_fix=max(e[1] for e in errs)
# 2) bolt torque: F = T/(K d); spec torque quoted for K=0.20 at 75% proof (33.64 kN)
d=0.010; proof=33640.0; Tspec=0.75*proof*0.20*d
tq=[]
for K in (0.20,0.17,0.15,0.12):
    F=Tspec/(K*d); Tfix=Tspec*K/0.20; Ffix=Tfix/(K*d)
    tq.append((F/proof, abs(Ffix-0.75*proof)/proof))
tq_raw=max(t[0] for t in tq); tq_fix=max(t[1] for t in tq)
# 3) thermostat with 120 s sensor lag; heat/cool slew 0.005 K/s, 1 s steps
def swing(band, lag=120, rate=0.005, secs=20000):
    T=20.0; on=True; buf=deque([T]*lag); lo=20.0; lo_t=[]; hi_t=[]; ons=0; sw=[]
    for t in range(secs):
        buf.append(T); seen=buf.popleft()
        if on and seen>=lo+band: on=False
        elif (not on) and seen<=lo: on=True; ons+=1
        T+= rate if on else -rate
        if t>secs//2: sw.append(T)
    return max(sw)-min(sw), ons
res={b:swing(b) for b in (1.0,0.5,0.25)}
floors=[res[b][0]-b for b in res]
# a "ratio correction" has nothing to scale: swing - band stays ~constant
floor_spread=max(floors)-min(floors)
print(f"dose raw error {dose_raw:.1%} -> ratio-corrected {dose_fix:.1%}")
print(f"torque worst load {tq_raw:.0%} of proof raw; ratio-corrected error {tq_fix:.1%} of proof")
print("thermostat swings", {b:round(res[b][0],2) for b in res}, "floors", [round(f,2) for f in floors], "cycles", [res[b][1] for b in res])
ok = dose_fix<1e-9 and tq_fix<1e-9 and dose_raw>0.3 and tq_raw>1.2 and floor_spread<0.2 and min(floors)>0.5
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" ratio fixes dose {dose_raw:.0%}->0 and torque {tq_raw:.0%}->75% proof; thermostat floor {min(floors):.2f}-{max(floors):.2f} K stays whatever the band")
