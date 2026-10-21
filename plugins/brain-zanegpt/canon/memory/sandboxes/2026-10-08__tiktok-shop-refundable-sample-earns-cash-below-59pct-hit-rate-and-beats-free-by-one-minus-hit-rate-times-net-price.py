#!/usr/bin/env python3
"""Sandbox: free sample vs refundable sample (creator buys at full price, refunded only if OTHER shoppers hit the seller's
sales threshold). Deterministic arithmetic, stdlib only. Terms read live 2026-10-08 (Seller University: How to use refundable
samples; Refundable Samples Terms & Conditions): creator pays full price; seller receives the purchase amount minus platform fees;
refund = full price incl. 100% of platform commission returned; threshold 1-3 sales (default 1), creator's own purchase doesn't count.
ASSUMED: threshold k=1, a creator who misses has 0 qualifying sales, fast-refund cases ignored.
SKU: price 29.99, cogs 7.00, ship 4.50, referral fee 6%, commission 15%, refund rate 15% -> contribution per order c = 9.11, sample cost S = 11.50.

PREDICTION (written before first run):
  P1 cash break-even hit rate before counting generated orders: m* = 1 - S/(P*(1-fee)) = 0.59 (0.58..0.60):
     below it a refundable sample earns cash on the creators who miss more than it refunds to those who hit.
  P2 at hit rate m=0.30 and 2 orders per hit, expected net per purchasing creator = +13.70 (13.5..13.9).
  P3 a free sample at posting rate 0.30 and 4.2 orders per poster nets about 0 (-0.15..+0.15) per sample (consistent with the payback lesson).
  P4 at equal success rate (m = q) and equal orders per success, refundable beats free by exactly (1-m)*P*(1-fee) per creator, for every m in [0,1).
  P5 (built to break 'refundable always wins overall') with take-up tau = 0.25 of the free-sample take-up, refundable generates fewer orders
     per 100 offers than free (at m=q), so it can only win on cash, not on volume.
"""
P,C,SHIP,FEE=29.99,7.0,4.5,0.06
def contrib(comm=0.15,r=0.15,u=0.5):
    kept=P-C-SHIP-FEE*P-comm*P; adm=min(0.2*FEE*P,5.0)
    return (1-r)*kept+r*-(SHIP+u*C+adm)
c=contrib(); S=C+SHIP; Pn=P*(1-FEE)
def net_free(q,o): return -S+q*o*c
def net_ref(m,o): return m*(-S+o*c)+(1-m)*(Pn-S)
mstar=1-S/Pn
print(f"c {c:.2f} S {S:.2f} P(1-fee) {Pn:.2f} m* {mstar:.3f}")
n2=net_ref(0.3,2); f3=net_free(0.3,4.2)
print(f"refundable m=0.30 o=2: {n2:+.2f}; free q=0.30 o=4.2: {f3:+.2f}")
ok4=all(abs((net_ref(m/100,3)-net_free(m/100,3))-(1-m/100)*Pn)<1e-9 for m in range(0,100))
tau=0.25; orders_free=100*0.3*3; orders_ref=100*tau*0.3*3
print(f"P4 identity holds for all m: {ok4}; orders per 100 offers at tau=0.25: free {orders_free:.0f} vs refundable {orders_ref:.1f}")
for m in (0.1,0.3,0.6,0.8,1.0): print(f"  m={m:.1f}: refundable {net_ref(m,2):+7.2f} | free(q=m) {net_free(m,2):+7.2f}")
p1=0.58<=mstar<=0.60; p2=13.5<=n2<=13.9; p3=-0.15<=f3<=0.15; p4=ok4; p5=orders_ref<orders_free
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+
      f"cash break-even hit rate {mstar:.2f}; refundable +{n2:.2f} vs free {f3:+.2f} per creator at m=q=0.30; refundable beats free by (1-m)*{Pn:.2f}; at 25% take-up orders {orders_ref:.0f} vs {orders_free:.0f} per 100 offers")
