#!/usr/bin/env python3
"""Sandbox: is Commission Saving via GMV Max worth it, and when does it fail? Deterministic, stdlib only.
Source (Seller University 'Commission Saving via GMV Max', read live 2026-10-08): eligible GMV Max campaigns get a reduction of the platform commission fee (page example: -3%),
the campaign ROI target must be at or below a personalized requirement refreshed daily (page example: requirement 9 -> target 9 or lower), locked 14 days, budget must meet the
recommended value. ASSUMED: the fee is the 6% referral fee and the reduction is 3 points; refunds 15% as in the break-even lessons; SKU price 29.99, cost 7, shipping 4.5.
PREDICTION (written before first run):
  P1 paid-order break-even ROAS falls from 2.32 to 2.18 (2.15..2.21) with a 3-point fee reduction.
  P2 the saving is 0.90 per placed order (0.88..0.92) before refunds.
  P3 with the page's example requirement (target <= 9) every ROI target from the break-even 2.18 up to 9 is eligible (band width 6.8, 6.5..7.0).
  P4 (built to break 'if it saves fees it is always worth it') if the shop's personalized requirement were 2.0 (below break-even 2.18), the eligible campaign loses money at its best allowed target: net per order < 0 at target 2.0.
"""
P,C,SHIP,R,U=29.99,7.0,4.5,0.15,0.5
def contrib(fee,comm=0.0):
    kept=P-C-SHIP-fee*P-comm*P; adm=min(0.2*fee*P,5.0)
    return (1-R)*kept+R*-(SHIP+U*C+adm)
c6,c3=contrib(0.06),contrib(0.03)
b6,b3=P/c6,P/c3
sav=P*0.03
band=9-b3
net_at_2=c3-P/2.0
print(f"BE-ROAS fee6% {b6:.2f} fee3% {b3:.2f}; saving per order {sav:.2f}; eligible target band {b3:.2f}..9 width {band:.2f}; net per order at target 2.0 {net_at_2:+.2f}")
p1=2.15<=b3<=2.21 and abs(b6-2.32)<0.01; p2=0.88<=sav<=0.92; p3=6.5<=band<=7.0; p4=net_at_2<0
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"3-point commission saving: paid BE-ROAS {b6:.2f}->{b3:.2f}, saves {sav:.2f}/order; requirement 9 leaves a {band:.1f}-wide eligible band, requirement 2.0 would force {net_at_2:+.2f}/order")
