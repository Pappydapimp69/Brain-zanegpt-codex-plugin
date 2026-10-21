#!/usr/bin/env python3
"""Sandbox: break-even ROAS depends on whether the order came through paid ads or an affiliate. Deterministic, stdlib only.
SKU price 29.99, cogs 7, ship 4.5, fee 6%, refund 15% (half cogs lost, admin fee 20% of referral fee capped $5). Affiliate orders pay 15% commission; paid-ad orders pay none.
PREDICTION (written before first run):
  P1 paid-only break-even ROAS = 2.32 (2.28..2.36).
  P2 affiliate-attributed break-even ROAS = 3.29 (3.27..3.31).
  P3 if 25% of orders are affiliate-attributed the blended break-even ROAS = 2.50 (2.46..2.54), strictly between P1 and P2.
  P4 (built to break 'one ROAS target fits all') a single ROAS target of 2.5 loses money on 100% affiliate orders: contribution at ROAS 2.5 < 0.
"""
P,C,SHIP,FEE,R,U=29.99,7.0,4.5,0.06,0.15,0.5
def contrib(comm):
    kept=P-C-SHIP-FEE*P-comm*P; adm=min(0.2*FEE*P,5.0)
    return (1-R)*kept+R*-(SHIP+U*C+adm)
cp,ca=contrib(0.0),contrib(0.15); bp,ba=P/cp,P/ca
cb=0.75*cp+0.25*ca; bb=P/cb
net_aff_at_25=ca-P/2.5
print(f"contribution paid {cp:.2f} affiliate {ca:.2f}; BE-ROAS paid {bp:.2f} affiliate {ba:.2f} blended(25% aff) {bb:.2f}; affiliate order net at ROAS 2.5: {net_aff_at_25:+.2f}")
p1=2.28<=bp<=2.36; p2=3.27<=ba<=3.31; p3=2.46<=bb<=2.54 and bp<bb<ba; p4=net_aff_at_25<0
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"BE-ROAS paid-only {bp:.2f}, affiliate {ba:.2f}, 25% affiliate blend {bb:.2f}; ROAS target 2.5 loses {abs(net_aff_at_25):.2f} per affiliate order")
