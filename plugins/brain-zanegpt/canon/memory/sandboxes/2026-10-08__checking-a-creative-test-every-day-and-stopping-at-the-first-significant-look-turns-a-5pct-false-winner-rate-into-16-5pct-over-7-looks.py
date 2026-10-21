#!/usr/bin/env python3
"""Sandbox: how much does checking a creative test early and often inflate false winners? Deterministic numerical integration, stdlib only.
Model: a test with K equally spaced looks; the z statistic at look j is Z_j = S_j / sqrt(j), S_j = sum of j independent N(0,1) increments (the standard large-sample
result for a two-arm proportion test). Under no true difference, 'stop at the first |Z_j| > 1.96' has false-positive rate P(max_j |Z_j| > 1.96).
Computed by dynamic programming on a fine grid of S (no random numbers). Pocock constants: the common critical z that keeps the K-look rate at 5%, found by bisection.
PREDICTION (written before first run; values are the classic Armitage-McPherson-Rowe repeated-testing numbers):
  P1 false-positive rate with K looks at z=1.96: K=2 -> 8.3% (7.9..8.7), K=3 -> 10.7% (10.2..11.2), K=5 -> 14.2% (13.6..14.8), K=10 -> 19.3% (18.5..20.1).
  P2 K=7 (a daily check on a one-week test) is between 16% and 18%.
  P3 the Pocock critical z for K=5 is about 2.41 (2.38..2.44), for K=10 about 2.56 (2.52..2.60).
  P4 (built to break 'one extra peek is harmless') a single early extra look (K=2) already raises the false-winner rate by at least 60% relative to 5%.
"""
import math
def phi(x): return math.exp(-0.5*x*x)/math.sqrt(2*math.pi)
H=0.02; LIM=9.0
GRID=[i*H for i in range(-int(LIM/H),int(LIM/H)+1)]
def fp_rate(K,z):
    # S_0=0; track the probability mass of paths that have NOT yet crossed; after each look remove mass where |S_j|/sqrt(j) > z.
    n=len(GRID); mid=n//2
    mass=[0.0]*n; mass[mid]=1.0
    alive=1.0
    # kernel width: increments N(0,1) truncated at +-6
    w=int(6/H); ker=[phi(k*H)*H for k in range(-w,w+1)]
    for j in range(1,K+1):
        new=[0.0]*n
        for i,m in enumerate(mass):
            if m<1e-14: continue
            lo=max(0,i-w); hi=min(n-1,i+w)
            for t in range(lo,hi+1): new[t]+=m*ker[t-i+w]
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
r={K:fp_rate(K,1.96) for K in (1,2,3,5,7,10)}
print({K:round(v,4) for K,v in r.items()})
z5=pocock(5); z10=pocock(10)
print(f"Pocock z K=5 {z5:.3f}, K=10 {z10:.3f}")
p1=(0.079<=r[2]<=0.087 and 0.102<=r[3]<=0.112 and 0.136<=r[5]<=0.148 and 0.185<=r[10]<=0.201)
p2=0.16<=r[7]<=0.18; p3=2.38<=z5<=2.44 and 2.52<=z10<=2.60; p4=r[2]/0.05-1>=0.60
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"false-winner rate when stopping at the first significant look: K=2 {r[2]:.1%}, K=5 {r[5]:.1%}, K=7 {r[7]:.1%}, K=10 {r[10]:.1%}; Pocock z K=5 {z5:.2f}, K=10 {z10:.2f}")
