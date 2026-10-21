#!/usr/bin/env python3
"""Sandbox: how much traffic does a TikTok creative A/B test need? Deterministic, stdlib only.

Two-sided pooled two-proportion z-test, alpha 0.05, one equal-size arm per creative.
n_per_arm (normal approx) = (z_a*sqrt(2*pbar*(1-pbar)) + z_b*sqrt(p1*(1-p1)+p2*(1-p2)))^2 / (p2-p1)^2
Exact power/size are computed by summing the binomial pmfs over the whole rejection region (no RNG).

PREDICTION (written before first run):
  P1 CTR 1.0% vs 1.5% at 80% power needs about 7,700 impressions per arm (7,000..8,500).
  P2 the exact binomial power at that n is within 0.77..0.83 (normal approx is trustworthy here).
  P3 the exact size (false-positive rate when both arms are 1.0%) is within 0.03..0.065.
  P4 a common 'judge after 1,000 impressions per creative' habit has power below 0.15 for 1.0% vs 1.5%.
  P5 (built to break P1's scaling) CTR 0.5% vs 0.75% (same relative lift) needs at least 1.8x the impressions of P1.
  P6 conversion rate per click 2% vs 3% needs about 3,800 clicks per arm (3,400..4,200), i.e. over 300,000
     impressions per arm at a 1% CTR: impression-level tests can rank hooks/CTR but cannot rank CVR.
"""
import math
def Phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def ppf(p):                      # inverse normal CDF by bisection (deterministic)
    lo,hi=-10.0,10.0
    for _ in range(200):
        mid=(lo+hi)/2
        if Phi(mid)<p: lo=mid
        else: hi=mid
    return (lo+hi)/2
ZA=ppf(0.975); ZB=ppf(0.80)

def n_arm(p1,p2):
    pb=(p1+p2)/2
    return math.ceil((ZA*math.sqrt(2*pb*(1-pb))+ZB*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2/(p2-p1)**2)

def pmf_window(n,p,k=7):
    mu=n*p; sd=math.sqrt(n*p*(1-p)); lo=max(0,int(mu-k*sd)); hi=min(n,int(mu+k*sd)+1)
    # log-space pmf to avoid underflow
    out={}
    for x in range(lo,hi+1):
        lg=math.lgamma(n+1)-math.lgamma(x+1)-math.lgamma(n-x+1)+x*math.log(p)+(n-x)*math.log(1-p)
        out[x]=math.exp(lg)
    return out

def reject(x1,x2,n):
    pb=(x1+x2)/(2*n)
    if pb in (0,1): return False
    se=math.sqrt(pb*(1-pb)*2/n)
    return se>0 and abs(x2-x1)/n/se>ZA

def prob_reject(n,p1,p2):
    a=pmf_window(n,p1); b=pmf_window(n,p2)
    return sum(pa*pb for x1,pa in a.items() for x2,pb in b.items() if reject(x1,x2,n))

n1=n_arm(.010,.015); pw=prob_reject(n1,.010,.015); size=prob_reject(n1,.010,.010)
pw1k=prob_reject(1000,.010,.015)
n2=n_arm(.005,.0075)
nc=n_arm(.02,.03)
imp_for_cvr=nc/0.01
print(f"z_alpha {ZA:.3f} z_beta {ZB:.3f}")
print(f"CTR 1.0% vs 1.5%: n/arm {n1}  exact power {pw:.3f}  exact size {size:.3f}  power at 1,000 imp {pw1k:.3f}")
print(f"CTR 0.5% vs 0.75%: n/arm {n2}  ratio to first {n2/n1:.2f}")
print(f"CVR 2% vs 3% per click: clicks/arm {nc}; impressions/arm at 1% CTR {imp_for_cvr:,.0f}")
p1_=7000<=n1<=8500; p2_=0.77<=pw<=0.83; p3_=0.03<=size<=0.065; p4_=pw1k<0.15; p5_=n2/n1>=1.8; p6_=3400<=nc<=4200 and imp_for_cvr>300000
print(f"P1 {p1_} P2 {p2_} P3 {p3_} P4 {p4_} P5 {p5_} P6 {p6_}")
print(("RESULT: PASS " if all((p1_,p2_,p3_,p4_,p5_,p6_)) else "RESULT: FAIL ")+
      f"CTR1.0v1.5 n/arm {n1} power {pw:.2f} size {size:.3f}; 1k-imp power {pw1k:.2f}; 0.5v0.75 n/arm {n2} ({n2/n1:.2f}x); CVR2v3 clicks/arm {nc} = {imp_for_cvr:,.0f} imp at 1% CTR")
