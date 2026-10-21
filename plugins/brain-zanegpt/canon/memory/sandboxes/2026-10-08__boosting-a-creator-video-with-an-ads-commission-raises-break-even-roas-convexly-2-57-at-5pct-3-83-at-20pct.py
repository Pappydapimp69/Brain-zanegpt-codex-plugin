#!/usr/bin/env python3
"""Sandbox: break-even ROAS when a creator video is boosted with Shop Ads and an ADS commission applies. Deterministic, stdlib only.
Source (Seller University 'Shop Ads Commission in Partner Campaigns', read live 2026-10-08): the Shop Ads commission is optional, applies only to orders generated through ads,
is an integer 1-80%, and must not be below the Open Collaboration ads rate. ASSUMED: on ads-attributed orders the ads commission REPLACES the affiliate commission (the page does not say);
same SKU as the break-even lessons (29.99, cost 7, shipping 4.5, 6% fee, 15% refunds).
PREDICTION (written before first run):
  P1 break-even ROAS by ads commission: 0% 2.32, 5% 2.57 (2.55..2.60), 10% 2.89 (2.86..2.92), 15% 3.29 (3.27..3.31), 20% 3.83 (3.78..3.88).
  P2 the increments are strictly increasing (convex): each extra 5 points costs more ROAS than the last.
  P3 contribution reaches zero near 51% ads commission: break-even ROAS above 100 at 50%.
  P4 (built to break 'ads commission is a small tweak') going from 10% to 20% raises the ROAS floor by at least 0.9.
"""
P,C,SHIP,FEE,R,U=29.99,7.0,4.5,0.06,0.15,0.5
def contrib(comm):
    kept=P-C-SHIP-FEE*P-comm*P; adm=min(0.2*FEE*P,5.0)
    return (1-R)*kept+R*-(SHIP+U*C+adm)
be={a:P/contrib(a/100) for a in (0,5,10,15,20,50)}
inc=[be[b]-be[a] for a,b in ((0,5),(5,10),(10,15),(15,20))]
print({a:round(v,2) for a,v in be.items()}); print("increments",[round(x,2) for x in inc])
p1=(abs(be[0]-2.32)<0.01 and 2.55<=be[5]<=2.60 and 2.86<=be[10]<=2.92 and 3.27<=be[15]<=3.31 and 3.78<=be[20]<=3.88)
p2=all(x<y for x,y in zip(inc,inc[1:])); p3=be[50]>100; p4=be[20]-be[10]>=0.9
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"break-even ROAS by ads commission 0/5/10/15/20/50%: "+"/".join(f"{be[a]:.2f}" for a in (0,5,10,15,20,50))+f"; 10->20% adds {be[20]-be[10]:.2f}")
