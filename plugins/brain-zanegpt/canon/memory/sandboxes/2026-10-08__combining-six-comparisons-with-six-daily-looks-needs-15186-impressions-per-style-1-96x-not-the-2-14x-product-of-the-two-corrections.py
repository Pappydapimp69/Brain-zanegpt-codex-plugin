#!/usr/bin/env python3
"""Sandbox (edge): do the multiple-comparison correction (matrix lesson) and the repeated-look correction (peeking lessons) simply multiply? Deterministic, stdlib only.
Composes tiktok-shop lessons E4 (CTR 1.0 vs 1.5% needs 7,750), E13 (6 comparisons: Bonferroni 11,957 = 1.54x), E23/E24 (6 daily looks: Pocock z 2.46, 10,748 = 1.39x).
Question: with BOTH (6 pairwise comparisons AND 6 daily looks) what is the per-style sample, and is it the product of the two factors?
Method: overall false-positive rate alpha = 0.05/6 across 6 looks via the same numerical integration as the peeking sandbox; size at the final look with power 0.80.
PREDICTION (written before first run):
  P1 the combined critical z is about 3.05 (2.98..3.12).
  P2 the combined per-style sample is about 14,900 impressions (14,000..15,800), i.e. 1.92x the fixed single-test 7,750 (1.80..2.04).
  P3 it is LESS than the naive product of the two factors (1.54 x 1.39 = 2.14x = about 16,590): the corrections overlap, so they do not multiply.
  P4 (built to break 'plan for the sum of the two costs') it is MORE than either factor alone (more than 11,957).
  P5 the 4-style by 3-product matrix then needs about 179,000 impressions (168,000..190,000) and each style-cell finishes in 7 to 9 days at 1,500 impressions per style per day.
"""
import math
def phi(x): return math.exp(-0.5*x*x)/math.sqrt(2*math.pi)
H=0.02; LIM=9.0
GRID=[i*H for i in range(-int(LIM/H),int(LIM/H)+1)]
def fp_rate(K,z):
    n=len(GRID); mid=n//2; mass=[0.0]*n; mass[mid]=1.0; w=int(6/H); ker=[phi(k*H)*H for k in range(-w,w+1)]
    for j in range(1,K+1):
        new=[0.0]*n
        for i,m in enumerate(mass):
            if m<1e-14: continue
            for t in range(max(0,i-w),min(n-1,i+w)+1): new[t]+=m*ker[t-i+w]
        thr=z*math.sqrt(j)
        for t,s in enumerate(GRID):
            if abs(s)>thr: new[t]=0.0
        mass=new
    return 1.0-sum(mass)
def crit(K,alpha):
    lo,hi=1.9,4.2
    for _ in range(30):
        mid=(lo+hi)/2
        if fp_rate(K,mid)>alpha: lo=mid
        else: hi=mid
    return (lo+hi)/2
def Phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def ppf(p):
    lo,hi=-12.0,12.0
    for _ in range(200):
        m=(lo+hi)/2
        if Phi(m)<p: lo=m
        else: hi=m
    return (lo+hi)/2
ZB=ppf(0.80)
def n_final(za):
    p1,p2=.010,.015; pb=(p1+p2)/2
    return math.ceil((za*math.sqrt(2*pb*(1-pb))+ZB*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2/(p2-p1)**2)
n0=n_final(1.959964); nb=n_final(ppf(1-0.05/12)); nk=n_final(crit(6,0.05)); zc=crit(6,0.05/6); nc=n_final(zc)
prod=(nb/n0)*(nk/n0)
tot=4*3*nc; days=math.ceil(nc/1500)
print(f"fixed {n0:,}; Bonferroni {nb:,} ({nb/n0:.2f}x); Pocock {nk:,} ({nk/n0:.2f}x); naive product {prod:.2f}x = {int(n0*prod):,}")
print(f"combined z {zc:.3f}: n {nc:,} ({nc/n0:.2f}x); 4x3 matrix {tot:,} impressions; {days} days at 1,500/day per style")
p1=2.98<=zc<=3.12; p2=14000<=nc<=15800 and 1.80<=nc/n0<=2.04; p3=nc<n0*prod; p4=nc>nb; p5=168000<=tot<=190000 and 7<=days<=9
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+f"6 comparisons + 6 daily looks: z {zc:.2f}, {nc:,} impressions per style ({nc/n0:.2f}x; naive product {prod:.2f}x), 4x3 matrix {tot:,}")
