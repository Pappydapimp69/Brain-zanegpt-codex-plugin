#!/usr/bin/env python3
"""Sandbox (edge): how deep can a promotion go before paid ads stop clearing a workable ROAS? Deterministic, stdlib only.
Composes tiktok-shop lessons E21 (discount needs 1.79x volume at 20% off; contribution linear in price), E22 (price floor for ROAS 3 by cost share) and E10 (paid-only break-even ROAS 2.32 at list).
SKU: list 29.99, cogs 7.00 (fixed in dollars, so cost share rises as the price falls), shipping 4.50, fee 6%, refunds 15%; paid orders pay no commission. 'Workable' target ROAS 3.0 (hypothetical).
PREDICTION (written before first run):
  P1 the deepest discount at which paid break-even ROAS stays at or under 3.0 is about 21% (20.5..21.7), i.e. a price floor of about 23.7 (23.5..23.9).
  P2 at list price break-even is 2.32, at 10% off about 2.54 (2.50..2.58), at 20% off about 2.99 (2.95..3.03).
  P3 at 30% off (price 20.99) break-even exceeds 4.0 (cost share has risen to 33%).
  P4 (built to break 'if the list price clears, the sale price clears') the same SKU that clears the ROAS-3 floor at list fails it at 25% off.
"""
SHIP,FEE,R,U,COGS,LIST,TARGET=4.5,0.06,0.15,0.5,7.0,29.99,3.0
def be(price):
    kept=price-COGS-SHIP-FEE*price; adm=min(0.2*FEE*price,5.0)
    c=(1-R)*kept+R*-(SHIP+U*COGS+adm)
    return price/c if c>0 else float('inf')
def best_discount():
    d=0.0
    while d<60:
        if be(LIST*(1-d/100))>TARGET: return d-0.01
        d+=0.01
    return d
dmax=best_discount(); pfloor=LIST*(1-dmax/100)
print(f"BE list {be(LIST):.2f}; 10% off {be(LIST*.9):.2f}; 20% off {be(LIST*.8):.2f}; 25% off {be(LIST*.75):.2f}; 30% off {be(LIST*.7):.2f}")
print(f"max discount for ROAS<=3: {dmax:.2f}% (price {pfloor:.2f})")
p1=20.5<=dmax<=21.7 and 23.5<=pfloor<=23.9; p2=abs(be(LIST)-2.32)<0.01 and 2.50<=be(LIST*.9)<=2.58 and 2.95<=be(LIST*.8)<=3.03
p3=be(LIST*.7)>4.0; p4=be(LIST)<=TARGET and be(LIST*.75)>TARGET
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"paid break-even ROAS: list {be(LIST):.2f}, 10% off {be(LIST*.9):.2f}, 20% off {be(LIST*.8):.2f}, 30% off {be(LIST*.7):.2f}; the deepest discount that keeps ROAS<=3 is {dmax:.1f}% (price {pfloor:.2f})")
