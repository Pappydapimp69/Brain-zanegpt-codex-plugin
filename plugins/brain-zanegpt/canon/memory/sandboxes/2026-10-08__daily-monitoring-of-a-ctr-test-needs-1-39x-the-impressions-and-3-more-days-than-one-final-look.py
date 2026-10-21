#!/usr/bin/env python3
"""Sandbox: what does it cost in days to check a creative test every day without inflating false winners? Deterministic, stdlib only.
Uses the Pocock critical z from the peeking sandbox (K=2:2.18? computed here by the same numerical integration) to size a CTR 1.0% vs 1.5% test (alpha 0.05 overall, power 0.80 at the final look).
Daily impressions per creative is a parameter (1,500 here); looks are once per day.
PREDICTION (written before first run):
  P1 fixed-sample size 7,750 impressions per creative takes 5.2 days at 1,500 per day (5.1..5.3).
  P2 with K=6 equally spaced daily looks the Pocock z is about 2.45 (2.42..2.49) and the final-look sample size rises to about 1.5x (1.43..1.57), i.e. about 11,700 impressions.
  P3 that moves the end of the test from day 6 to day 8 at 1,500 per day (6 looks need 7.8 days, so the 8th day) (days = 8).
  P4 (built to break 'monitoring is free') the expected savings never offset the cost: the final-look n for K=6 exceeds the fixed-sample n by at least 3,500 impressions.
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
def pocock(K):
    lo,hi=1.9,3.2
    for _ in range(30):
        mid=(lo+hi)/2
        if fp_rate(K,mid)>0.05: lo=mid
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
def n_final(p1,p2,za):
    pb=(p1+p2)/2
    return math.ceil((za*math.sqrt(2*pb*(1-pb))+ZB*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2/(p2-p1)**2)
PER_DAY=1500
n0=n_final(.010,.015,1.959964); z6=pocock(6); n6=n_final(.010,.015,z6)
d0=n0/PER_DAY; d6=math.ceil(n6/PER_DAY)
print(f"fixed n {n0:,} = {d0:.2f} days; Pocock K=6 z {z6:.3f}, n {n6:,} ({n6/n0:.2f}x) -> {d6} days; extra impressions {n6-n0:,}")
p1=5.1<=d0<=5.3; p2=2.42<=z6<=2.49 and 1.43<=n6/n0<=1.57; p3=d6==8; p4=(n6-n0)>=3500
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"daily looks (K=6): Pocock z {z6:.2f}, {n6/n0:.2f}x the fixed sample ({n0:,} -> {n6:,} impressions), {d0:.1f} -> {d6} days at {PER_DAY:,}/day")
