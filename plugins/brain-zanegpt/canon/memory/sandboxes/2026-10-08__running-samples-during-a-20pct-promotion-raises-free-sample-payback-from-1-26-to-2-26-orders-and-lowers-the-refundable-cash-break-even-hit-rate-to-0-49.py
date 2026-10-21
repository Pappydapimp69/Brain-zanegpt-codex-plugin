#!/usr/bin/env python3
"""Sandbox (edge): what does a promotion do to sample payback? Deterministic, stdlib only.
Composes tiktok-shop lessons E6 (free sample 11.50 pays back after 1.26 orders; 4.2 per poster at 30% posting), E15 (refundable sample: cash break-even hit rate m* = 1 - S/(P(1-fee)) = 0.59) and E21 (20% off needs 1.79x volume; per-order contribution 5.09 at 23.99).
Question: if the sampled creator's orders happen during a 20% promotion (price 23.99), how do the payback numbers move? Same SKU (29.99, cogs 7, ship 4.5, fee 6%, commission 15%, 15% refunds); sample cost 11.50 unchanged.
PREDICTION (written before first run):
  P1 free-sample payback rises from 1.26 to 2.26 orders (2.20..2.32).
  P2 at a 30% posting rate each poster must sell 7.5 orders (7.3..7.7), up from 4.2.
  P3 the refundable-sample cash break-even hit rate falls from 0.59 to 0.49 (0.48..0.50) because the creator pays less.
  P4 (built to break 'a promotion only changes the order side') the sample cost side is also affected for refundable samples: net price P(1-fee) drops from 28.19 to 22.55 (22.4..22.7).
  P5 at a 40% discount free-sample payback exceeds 10 orders (price 17.99, contribution 1.08).
"""
def contrib(p,comm=0.15,fee=0.06,r=0.15,cogs=7.0,ship=4.5,u=0.5):
    kept=p-cogs-ship-fee*p-comm*p; adm=min(0.2*fee*p,5.0)
    return (1-r)*kept+r*-(ship+u*cogs+adm)
S=11.5
c_full=contrib(29.99); c20=contrib(29.99*0.8); c40=contrib(29.99*0.6)
pay_full=S/c_full; pay20=S/c20; pay40=S/c40
m_full=1-S/(29.99*0.94); m20=1-S/(29.99*0.8*0.94)
net20=29.99*0.8*0.94
print(f"contribution full {c_full:.2f}, 20% off {c20:.2f}, 40% off {c40:.2f}")
print(f"free payback orders: full {pay_full:.2f}, 20% off {pay20:.2f}, 40% off {pay40:.2f}; per poster at 30% posting: full {pay_full/0.3:.1f}, 20% off {pay20/0.3:.1f}")
print(f"refundable cash break-even hit rate: full {m_full:.3f}, 20% off {m20:.3f}; net price at 20% off {net20:.2f}")
p1=2.20<=pay20<=2.32; p2=7.3<=pay20/0.3<=7.7; p3=0.48<=m20<=0.50; p4=22.4<=net20<=22.7; p5=pay40>10
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+f"20% promo: free sample payback {pay_full:.2f}->{pay20:.2f} orders ({pay20/0.3:.1f} per poster at 30%), refundable break-even hit rate {m_full:.2f}->{m20:.2f}; 40% off needs {pay40:.1f} orders")
