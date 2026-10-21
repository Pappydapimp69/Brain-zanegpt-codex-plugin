#!/usr/bin/env python3
"""Sandbox: how much extra volume does a discount need before it stops losing money? Deterministic, stdlib only.
SKU list price 29.99, cogs 7, shipping 4.5, referral fee 6% and commission 15% both charged on the PRICE PAID, refunds 15% (half cogs lost, admin fee 20% of referral fee capped $5).
Fixed per-order costs (cogs, shipping) do not shrink with the price; fee and commission do. Contribution is linear in price: c(P) = a*P - b.
(Context: Seller Center promotions such as Flash Deals unlock at a Shop Performance Score of 2.5 - Seller University SPS guide, read live 2026-10-08.)
PREDICTION (written before first run):
  P1 contribution per order at full price 9.11; at 10% off 7.10 (7.05..7.15); at 20% off 5.09 (5.05..5.15).
  P2 required volume multiplier to keep total contribution flat: 1.28x at 10% off (1.26..1.30), 1.79x at 20% (1.75..1.83), 2.96x at 30% (2.85..3.05).
  P3 contribution reaches zero at a discount of about 45.4% (45..46): the price floor is about 16.39 (16.3..16.5).
  P4 (built to break 'a sale just trades margin for volume') at 40% off the multiplier is above 8: a deep discount needs a sales surge that a sample or ad budget will not deliver.
"""
P0,C,SHIP,FEE,COMM,R,U=29.99,7.0,4.5,0.06,0.15,0.15,0.5
def contrib(p):
    kept=p-C-SHIP-FEE*p-COMM*p; adm=min(0.2*FEE*p,5.0)
    return (1-R)*kept+R*-(SHIP+U*C+adm)
c0=contrib(P0)
rows={d:(contrib(P0*(1-d/100)),c0/contrib(P0*(1-d/100)) if contrib(P0*(1-d/100))>0 else float('inf')) for d in (10,20,30,40,45)}
# zero-contribution price by bisection
lo,hi=1.0,P0
for _ in range(100):
    mid=(lo+hi)/2
    if contrib(mid)<0: lo=mid
    else: hi=mid
pfloor=hi; dmax=(1-pfloor/P0)*100
print(f"c(full) {c0:.2f}"); 
for d,(c,m) in rows.items(): print(f"  {d}% off: contribution {c:.2f}, volume multiplier {m:.2f}")
print(f"zero-contribution price {pfloor:.2f} = {dmax:.1f}% off")
p1=abs(c0-9.11)<0.01 and 7.05<=rows[10][0]<=7.15 and 5.05<=rows[20][0]<=5.15
p2=1.26<=rows[10][1]<=1.30 and 1.75<=rows[20][1]<=1.83 and 2.85<=rows[30][1]<=3.05
p3=45<=dmax<=46 and 16.3<=pfloor<=16.5; p4=rows[40][1]>8
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"volume needed to hold total contribution: 10% off {rows[10][1]:.2f}x, 20% {rows[20][1]:.2f}x, 30% {rows[30][1]:.2f}x, 40% {rows[40][1]:.1f}x; contribution hits zero at {dmax:.1f}% off (price {pfloor:.2f})")
