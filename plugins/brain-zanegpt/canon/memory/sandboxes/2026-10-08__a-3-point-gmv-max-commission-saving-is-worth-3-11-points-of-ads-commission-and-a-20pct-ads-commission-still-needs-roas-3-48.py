#!/usr/bin/env python3
"""Sandbox (edge): is a GMV Max commission saving worth the same as an equal cut in the Shop Ads commission? Deterministic, stdlib only.
Composes tiktok-shop lessons E18 (3-point fee saving: paid break-even ROAS 2.32 -> 2.19) and E16 (ads commission 0/5/10/15/20% -> 2.32/2.57/2.89/3.29/3.83).
Both are percentages of the price paid, so they should trade roughly 1:1; the refund administration fee (20% of the referral fee) is the only asymmetry.
PREDICTION (written before first run):
  P1 break-even ROAS with ads commission a and referral fee f depends on a+f almost only: BE(a=10%, f=3%) is within 0.02 of BE(a=7%, f=6%) (about 2.65).
  P2 the 3-point saving is worth 2.9 to 3.0 points of ads commission (the admin-fee term makes it slightly less than 3).
  P3 with the saving active, ads commissions of 5%, 10%, 15%, 20% give break-even 2.43, 2.73, 3.10, 3.60 (each within 0.04).
  P4 (built to break 'the saving makes a high ads commission safe') at a 20% ads commission, even with the saving, the paid break-even stays above 3.5.
"""
P,C,SHIP,R,U=29.99,7.0,4.5,0.15,0.5
def be(a,f):
    kept=P-C-SHIP-f*P-a*P; adm=min(0.2*f*P,5.0)
    c=(1-R)*kept+R*-(SHIP+U*C+adm); return P/c
def equiv_points(target_be,f):
    lo,hi=0.0,0.5
    for _ in range(80):
        mid=(lo+hi)/2
        if be(mid,f)<target_be: lo=mid
        else: hi=mid
    return (lo+hi)/2
print({a:(round(be(a/100,0.06),2),round(be(a/100,0.03),2)) for a in (0,5,10,15,20)})
d=abs(be(0.10,0.03)-be(0.07,0.06))
# points of ads commission that a 3-point fee saving is worth, measured at a=10%
pts=(0.10-equiv_points(be(0.10,0.03),0.06))*100
print(f"|BE(10%,3%)-BE(7%,6%)| = {d:.4f}; 3-pt saving ~ {pts:.2f} points of ads commission")
p1=d<=0.02; p2=2.9<=pts<=3.0
exp={5:2.43,10:2.73,15:3.10,20:3.60}; p3=all(abs(be(a/100,0.03)-v)<=0.04 for a,v in exp.items())
p4=be(0.20,0.03)>3.5
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"a 3-point commission saving equals {pts:.2f} points of ads commission; with the saving, break-even by ads commission 5/10/15/20% = "+"/".join(f"{be(a/100,0.03):.2f}" for a in (5,10,15,20)))
