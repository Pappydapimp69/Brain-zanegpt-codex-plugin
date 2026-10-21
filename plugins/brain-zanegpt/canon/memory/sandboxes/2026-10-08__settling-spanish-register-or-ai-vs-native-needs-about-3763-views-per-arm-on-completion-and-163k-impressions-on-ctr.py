#!/usr/bin/env python3
"""Sandbox: traffic needed to settle the two open tensions (Spanish register; AI vs native video). Deterministic, stdlib only.
Pooled two-proportion z, alpha 0.05 two-sided, power 0.80 (same formula as the CTR sizing sandbox, which matched exact binomial power 0.803).
PREDICTION (written before first run):
  P1 completion rate 30% vs 33% (10% relative lift): about 3,760 views per arm (3,500..4,000).
  P2 6-second view rate 40% vs 44%: about 2,350 per arm (2,200..2,500).
  P3 CTR 1.0% vs 1.1% (10% relative): about 163,000 impressions per arm (150,000..175,000) -> too costly to decide on CTR.
  P4 (built to break 'a small lift is just as cheap') halving the lift to 5% relative on completion (30% vs 31.5%) needs at least 3.8x the traffic of P1.
"""
import math
def Phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def ppf(p):
    lo,hi=-12.0,12.0
    for _ in range(200):
        m=(lo+hi)/2
        if Phi(m)<p: lo=m
        else: hi=m
    return (lo+hi)/2
ZA,ZB=ppf(0.975),ppf(0.80)
def n(p1,p2):
    pb=(p1+p2)/2
    return math.ceil((ZA*math.sqrt(2*pb*(1-pb))+ZB*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2/(p2-p1)**2)
a,b,c,d=n(.30,.33),n(.40,.44),n(.010,.011),n(.30,.315)
print(f"completion 30->33%: {a:,}; 6s view 40->44%: {b:,}; CTR 1.0->1.1%: {c:,}; completion 30->31.5%: {d:,} ({d/a:.2f}x)")
q=(3500<=a<=4000, 2200<=b<=2500, 150000<=c<=175000, d/a>=3.8)
print("P1..P4",q)
print(("RESULT: PASS " if all(q) else "RESULT: FAIL ")+f"views per arm: completion +10% {a:,}, 6s-view +10% {b:,}, CTR +10% {c:,}; halving the lift costs {d/a:.1f}x")
