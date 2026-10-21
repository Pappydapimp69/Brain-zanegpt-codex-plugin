#!/usr/bin/env python3
"""Sandbox: what does the style x product test matrix cost once you correct for many comparisons? Deterministic, stdlib only.
4 styles compared pairwise (6 comparisons) within each of 3 products; CTR 1.0% vs 1.5% (50% lift), alpha 0.05, power 0.80.
Bonferroni: alpha_per_test = 0.05 / 6. Exact binomial power/size computed by summing pmfs (no RNG).

PREDICTION (written before first run):
  P1 unadjusted family-wise false-positive rate over 6 pairwise tests = 1-0.95^6 = 0.265 (0.26..0.27).
  P2 Bonferroni sample size per style = about 11,950 impressions (11,500..12,400), i.e. 1.54x the single-test 7,750.
  P3 matrix total = 4 styles x 3 products x n = about 143,000 impressions (140,000..148,000).
  P4 exact power at that n with the adjusted alpha is within 0.77..0.83.
  P5 (built to break 'more styles is free') adding a 5th style (10 comparisons) raises the per-style n by at least 1.15x.
"""
import math
def Phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def ppf(p):
    lo,hi=-12.0,12.0
    for _ in range(200):
        mid=(lo+hi)/2
        if Phi(mid)<p: lo=mid
        else: hi=mid
    return (lo+hi)/2
ZB=ppf(0.80)
def n_arm(p1,p2,alpha):
    za=ppf(1-alpha/2); pb=(p1+p2)/2
    return math.ceil((za*math.sqrt(2*pb*(1-pb))+ZB*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2/(p2-p1)**2), za
def window(n,p,k=7):
    mu=n*p; sd=math.sqrt(n*p*(1-p)); lo=max(0,int(mu-k*sd)); hi=min(n,int(mu+k*sd)+1)
    return {x:math.exp(math.lgamma(n+1)-math.lgamma(x+1)-math.lgamma(n-x+1)+x*math.log(p)+(n-x)*math.log(1-p)) for x in range(lo,hi+1)}
def prob_reject(n,p1,p2,za):
    a=window(n,p1); b=window(n,p2); t=0.0
    for x1,pa in a.items():
        for x2,pb_ in b.items():
            pb=(x1+x2)/(2*n)
            if 0<pb<1 and abs(x2-x1)/n/math.sqrt(pb*(1-pb)*2/n)>za: t+=pa*pb_
    return t
n1,_=n_arm(.010,.015,.05); n6,z6=n_arm(.010,.015,.05/6); n10,_=n_arm(.010,.015,.05/10)
fw=1-0.95**6; pw=prob_reject(n6,.010,.015,z6); sz=prob_reject(n6,.010,.010,z6)
tot=4*3*n6
print(f"single-test n {n1}; Bonferroni(6) n {n6} ({n6/n1:.2f}x, z {z6:.3f}); Bonferroni(10) n {n10} ({n10/n6:.2f}x vs 6)")
print(f"family-wise FP unadjusted {fw:.3f}; exact power at n6 {pw:.3f}; exact size per test {sz:.4f}; matrix total {tot:,}")
p1=0.26<=fw<=0.27; p2=11500<=n6<=12400; p3=140000<=tot<=148000; p4=0.77<=pw<=0.83; p5=n10/n6>=1.15
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+f"6 comparisons: FWER {fw:.2f} unadjusted; Bonferroni n/style {n6:,} ({n6/n1:.2f}x), exact power {pw:.2f}; 4x3 matrix {tot:,} impressions; 5th style x{n10/n6:.2f}")
