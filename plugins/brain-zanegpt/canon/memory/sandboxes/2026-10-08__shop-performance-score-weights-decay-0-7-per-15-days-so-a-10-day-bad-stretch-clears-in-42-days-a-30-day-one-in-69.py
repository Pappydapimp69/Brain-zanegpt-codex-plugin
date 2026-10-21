#!/usr/bin/env python3
"""Sandbox: how fast does Shop Performance Score weighting forgive a bad stretch? Deterministic, stdlib only.
Source (Seller University SPS guide, read live 2026-10-08): older orders decay by factor 0.7 per 15 days (0-15 d full, 16-30 d 70%, 31-45 d 49%, 46-60 d 34%); SPS needs 30 delivered
non-sample orders in 90 days; 3.5 unlocks affiliate/campaigns and 5-day settlement, 4.0 1-day settlement, below 3.0 benefits pause.
ASSUMED: the decay continues in 15-day buckets out to 90 days; constant daily order volume; the model tracks a RETURN RATE, not the real SPS (its formula is not public); 5% is a hypothetical alarm level.
Scenario A: 3% daily return rate, except a 10-day bad stretch at 25%; scenario B: the bad stretch lasts 30 days. t = days after the stretch ends.
PREDICTION (written before first run):
  P1 immediately after the 10-day stretch the decay-weighted return rate peaks near 7.9% (7.5..8.3).
  P2 the weighted rate falls back below 5% between 31 and 50 days after the stretch ends.
  P3 a flat (unweighted) 90-day window stays above 5.0% for 80 days (until the stretch leaves the window), so weighting recovers at least 30 days faster than the flat window.
  P4 (built to break 'a month of problems is forgiven in a month') a 30-day stretch peaks above 12% and needs at least 50 days after it ends to get below 5%.
"""
RATE_OK,RATE_BAD=0.03,0.25
def weight(age): return 0.7**(age//15)
def series(bad_len,horizon=140,window=90):
    # day index d = 0 is the last day of the stretch; stretch occupies days -(bad_len-1)..0; t>0 are later days at normal rate
    def rate(day): return RATE_BAD if -(bad_len-1)<=day<=0 else RATE_OK
    out=[]
    for t in range(0,horizon):
        num=den=0.0; flat_num=flat_den=0.0
        for age in range(0,window):
            day=t-age; r=rate(day); w=weight(age)
            num+=w*r; den+=w; flat_num+=r; flat_den+=1
        out.append((t,num/den,flat_num/flat_den))
    return out
A=series(10); B=series(30)
peakA=A[0][1]; below=lambda S:next((t for t,w,f in S if w<0.05),None)
flat_above=max((t for t,w,f in A if f>0.05),default=None)
print(f"A: peak weighted {peakA:.3%}; back under 5% at t={below(A)}; flat window above 5% until t={flat_above}")
print(f"B: peak weighted {B[0][1]:.3%}; back under 5% at t={below(B)}")
p1=0.075<=peakA<=0.083; p2=31<=below(A)<=50; p3=flat_above>=79 and (flat_above+1-below(A))>=30; p4=B[0][1]>0.12 and below(B)>=50
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"10-day 25% return stretch: weighted peak {peakA:.1%}, under 5% after {below(A)} d (flat window {flat_above+1} d); 30-day stretch: peak {B[0][1]:.1%}, under 5% after {below(B)} d")
