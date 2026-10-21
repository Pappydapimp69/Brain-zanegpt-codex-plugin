"""Toy emulsion: oil added at rate r per tick; whisking makes interface area A per unit oil.
Lecithin coats at most C area per tick (kinetic limit) and L area in total (yolk capacity).
Uncoated area that is not coated within the tick coalesces (oil lost to the greasy layer). Deterministic ticks.
Prediction (before run): (1) slow addition below C/A holds (0% lost); (2) dumping at 4x C/A loses most oil;
(3) slow addition still breaks once total oil*A passes L (capacity, not rate); (4) fresh yolk + slow re-feed rescues a rate-broken batch but not a capacity-broken one without extra yolk."""
A=10.0
def run(total_oil,r,C,L,yolk_add=None):
    coated=0.0; lost=0.0; fed=0.0; free=0.0
    t=0
    while fed<total_oil:
        add=min(r,total_oil-fed); fed+=add
        area=add*A+free; free=0.0
        can=min(C,L-coated,area)
        coated+=can; leftover=area-can
        lost+=leftover/A            # uncoated droplets merge: that oil is lost
        t+=1
    return lost/total_oil
def rescue(total_oil,r,C,L,extra_yolk):
    first=run(total_oil,r,C,L)
    lost_oil=first*total_oil
    # re-feed the lost oil slowly into a fresh yolk; fresh yolk adds capacity L2 and the same coating rate
    second=run(lost_oil,0.5*C/A,C,extra_yolk) if lost_oil>0 else 0.0
    return first,second
C=20.0; L=2000.0; total=100.0         # capacity covers 200 oil units at A=10
safe=C/A                               # 2 oil/tick
s1=run(total,0.5*safe,C,L); s2=run(total,safe,C,L); s3=run(total,4*safe,C,L)
cap=run(300.0,0.5*safe,C,L)            # slow, but 300 oil needs 3000 area > L=2000: BREAK by capacity
f1,f2=rescue(total,4*safe,C,L,2000.0)  # rate-broken, rescued with fresh yolk
g1,g2=rescue(300.0,0.5*safe,C,L,0.0)   # capacity-broken, no new yolk
g1b,g2b=rescue(300.0,0.5*safe,C,L,1500.0)
print(f"slow half-rate lost={s1:.2f}  at-limit={s2:.2f}  dump 4x={s3:.2f}  slow-but-over-capacity={cap:.2f}")
print(f"rate-broken: first lost={f1:.2f}, after fresh yolk re-feed lost={f2:.2f}")
print(f"capacity-broken: no extra yolk re-feed lost={g2:.2f}; with extra yolk lost={g2b:.2f}")
ok = s1==0 and s2==0 and s3>0.5 and 0.2<cap<0.5 and f2==0 and g2>0.9 and g2b<0.05
print("RESULT: %s slow=%.2f dump4x=%.2f over_capacity=%.2f rate_rescue=%.2f capacity_no_yolk=%.2f capacity_extra_yolk=%.2f"%("PASS" if ok else "FAIL",s1,s3,cap,f2,g2,g2b))
