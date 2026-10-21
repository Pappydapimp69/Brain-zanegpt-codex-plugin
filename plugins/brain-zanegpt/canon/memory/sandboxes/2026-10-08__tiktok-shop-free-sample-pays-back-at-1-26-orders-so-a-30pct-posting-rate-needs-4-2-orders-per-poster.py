#!/usr/bin/env python3
"""Sandbox: how many affiliate orders must one free sample bring back? Deterministic, stdlib only.
Seller pays product, shipping and tax for a creator sample (Seller University, read live 2026-10-08); tax set to 0 (ASSUMED, param).
Per-order contribution reuses the break-even model: price 29.99, cogs 7.00, ship 4.50, 6% referral fee, commission c,
refund rate r (half the cogs lost on a refund, no commission paid on refunded orders, admin fee 20% of referral fee capped $5).
Affiliate orders carry no ad spend, so break-even orders per sample = sample_cost / contribution.

PREDICTION (written before first run):
  P1 no refunds, c=15%: break-even orders per sample = 11.50 / 12.19 = 0.94 (0.93..0.95).
  P2 refund rate 15%: 1.26 (1.24..1.28).
  P3 if 30% of sampled creators post, a posting creator must sell 4.2 orders (4.1..4.3) for the programme to break even at r=15%.
  P4 raising commission to 25% (r=15%) raises break-even orders per sample by at least 35%.
  P5 (built to break 'samples pay back easily') if only 10% of sampled creators post, a poster must sell more than 10 orders.
"""
def contrib(price,cogs,ship,fee,comm,r=0.0,u=0.5):
    kept = price - cogs - ship - fee*price - comm*price
    adm = min(0.20*fee*price, 5.00)
    return (1-r)*kept + r*(-(ship + u*cogs + adm))
P=dict(price=29.99,cogs=7.0,ship=4.5,fee=0.06)
sample = P['cogs']+P['ship']+0.0
c0=contrib(**P,comm=0.15); c1=contrib(**P,comm=0.15,r=0.15); c2=contrib(**P,comm=0.25,r=0.15)
b0,b1,b2=sample/c0,sample/c1,sample/c2
print(f"sample cost {sample:.2f}; contribution r=0 {c0:.2f}, r=15% {c1:.2f}, r=15% c=25% {c2:.2f}")
print(f"break-even orders per sample: {b0:.3f} | r=15% {b1:.3f} | r=15% c=25% {b2:.3f} ({(b2/b1-1)*100:+.0f}%)")
for q in (0.5,0.3,0.2,0.1):
    print(f"  post rate {q:.0%}: orders per posting creator needed {b1/q:.1f}")
p1=0.93<=b0<=0.95; p2=1.24<=b1<=1.28; p3=4.1<=b1/0.3<=4.3; p4=b2/b1-1>=0.35; p5=b1/0.10>10
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+
      f"break-even orders/sample {b0:.2f} (no refunds), {b1:.2f} (15% refunds), {b2:.2f} (25% commission); poster needs {b1/0.3:.1f} orders at 30% post rate, {b1/0.1:.1f} at 10%")
