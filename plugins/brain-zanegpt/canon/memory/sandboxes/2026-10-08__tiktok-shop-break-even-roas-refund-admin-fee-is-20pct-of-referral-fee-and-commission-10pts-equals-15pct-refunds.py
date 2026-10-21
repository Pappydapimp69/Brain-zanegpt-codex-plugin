#!/usr/bin/env python3
"""Sandbox: break-even ROAS for a TikTok Shop SKU. Deterministic, stdlib only.

Model (per order PLACED; ROAS = placed revenue / ad spend, break-even ad spend per order = contribution):
  kept (1-r):   price - cogs - ship_out - fee*price - commission*price
  refunded (r): -(ship_out + u*cogs + min(0.20*fee*price, 5.00))   # referral fee refunded minus a refund
                admin fee of 20% OF THE REFERRAL FEE capped $5/SKU (Seller University, read 2026-10-08);
                u = share of COGS not recoverable; ASSUMED: no commission paid on refunded orders.
  break_even_ROAS = price / contribution.

PREDICTION (written before first run), base SKU price 29.99, cogs 7.00, ship_out 4.50, fee 6%, commission 15%, r=0:
  P1 contribution 12.19, break-even ROAS 2.46.
  P2 r=15%, u=0.5 raises break-even ROAS to 3.25..3.35 (about +34%).
  P3 commission 15%->25% (+10 pts) raises break-even ROAS MORE than the r=15% refund rate does (>= 3.6).
  P4 the $5 refund-admin cap binds only when 0.2*fee*price > 5, i.e. price > 416.67; at 29.99 the refund admin fee is 0.36.
  P5 (built to break) at price 500 the cap binds (fee charged exactly 5.00, not 6.00).
"""
def contrib(price,cogs,ship,fee,comm,r=0.0,u=0.5):
    kept = price - cogs - ship - fee*price - comm*price
    adm = min(0.20*fee*price, 5.00)
    refd = -(ship + u*cogs + adm)
    return (1-r)*kept + r*refd, adm
def be(price,*a,**k):
    c,_ = contrib(price,*a,**k); return price/c, c
B = dict(price=29.99,cogs=7.0,ship=4.5,fee=0.06,comm=0.15)
r0,c0 = be(B['price'],B['cogs'],B['ship'],B['fee'],B['comm'])
r1,c1 = be(B['price'],B['cogs'],B['ship'],B['fee'],B['comm'],r=0.15)
r2,c2 = be(B['price'],B['cogs'],B['ship'],B['fee'],0.25)
_,adm30 = contrib(29.99,7,4.5,0.06,0.15)
_,adm500 = contrib(500,100,8,0.06,0.15)
cap_price = 5.00/(0.20*0.06)
print(f"base: contribution {c0:.2f} BE-ROAS {r0:.2f}")
print(f"refund 15% (u=0.5): contribution {c1:.2f} BE-ROAS {r1:.2f} ({(r1/r0-1)*100:+.0f}%)")
print(f"commission 25%: contribution {c2:.2f} BE-ROAS {r2:.2f} ({(r2/r0-1)*100:+.0f}%)")
print(f"refund admin fee at 29.99: {adm30:.2f}; cap binds above price {cap_price:.2f}; at 500: {adm500:.2f}")
p1 = abs(c0-12.19)<0.01 and abs(r0-2.46)<0.01
p2 = 3.25<=r1<=3.35
p3 = r2>r1 and r2>=3.6
p4 = abs(adm30-0.36)<0.01 and abs(cap_price-416.67)<0.01
p5 = adm500==5.00 and 0.2*0.06*500==6.0
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+
      f"base BE-ROAS {r0:.2f}; refund15% {r1:.2f}; commission25% {r2:.2f}; admin cap binds above ${cap_price:.0f}")
