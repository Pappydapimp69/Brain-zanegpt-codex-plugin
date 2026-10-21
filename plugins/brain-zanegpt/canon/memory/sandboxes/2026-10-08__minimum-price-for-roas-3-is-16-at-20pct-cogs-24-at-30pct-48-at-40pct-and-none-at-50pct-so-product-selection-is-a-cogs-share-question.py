#!/usr/bin/env python3
"""Sandbox: the minimum list price a product needs, by COGS share, before an ad ROAS target is reachable. Deterministic, stdlib only.
Per-order shipping is fixed at 4.50; cogs = share * price; referral fee 6% and refunds 15% (half cogs lost, admin fee 20% of fee capped $5); no commission (paid-ad orders).
Question: what is the cheapest price at which break-even ROAS <= 3.0 (a common 'workable' target; hypothetical)?
PREDICTION (written before first run):
  P1 at cogs share 20% the minimum price for break-even ROAS <= 3 is about 19 (17..21).
  P2 at 30% it is about 28 (25..31); at 40% about 44 (40..48).
  P3 at a 50% cogs share no price works near 3.0 only above about 100 (90..130) - or none below 60.
  P4 (built to break 'margin share is all that matters') at the same 30% cogs share a 10-dollar item (fixed shipping 4.5) cannot reach ROAS 3 at all (price < the 28 floor), though a 30-dollar item can.
"""
SHIP,FEE,R,U,TARGET=4.5,0.06,0.15,0.5,3.0
def be(price,share):
    cogs=share*price; kept=price-cogs-SHIP-FEE*price; adm=min(0.2*FEE*price,5.0)
    c=(1-R)*kept+R*-(SHIP+U*cogs+adm)
    return price/c if c>0 else float('inf')
def floor(share):
    p=1.0
    while p<500:
        if be(p,share)<=TARGET: return p
        p+=0.01
    return None
f={s:floor(s/100) for s in (20,30,40,50)}
print({s:(round(v,2) if v else None) for s,v in f.items()}); print("30% share: price 10 ->",round(be(10,.30),2),"; price 30 ->",round(be(30,.30),2))
p1=17<=f[20]<=21; p2=25<=f[30]<=31 and 40<=f[40]<=48; p3=(f[50] is None) or 90<=f[50]<=130; p4=be(10,.30)>TARGET and be(30,.30)<=TARGET
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"minimum price for break-even ROAS <=3 by cogs share 20/30/40/50%: "+"/".join(f"{f[s]:.1f}" if f[s] else "none" for s in (20,30,40,50)))
