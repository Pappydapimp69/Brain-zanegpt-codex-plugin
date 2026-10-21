# Stair stringer layout: total rise R (inches) in 1/8" steps, 30..140. Riser limit 7.75", max variation between risers 3/8".
# PREDICTION (before run): fixed 7.5" riser with the remainder in the last riser breaks the 3/8" variation rule for >85% of heights;
# equal division R/N never does; marking each step at round(i*R/N, 1/16) keeps variation <=1/16" while repeating one rounded riser
# drifts and breaks the 3/8" rule for some tall heights.
from fractions import Fraction as F
heights=[F(h,8) for h in range(30*8,140*8+1)]
def q(x,den): return F(round(x*den),den)
def variation(rises): return max(rises)-min(rises)
naive_bad=eq_bad=cum_max=0; drift_bad=0; drift_worst=F(0); nover=0; n_tot=len(heights)
for R in heights:
    # fixed 7.5 riser, remainder on the last
    n=int(R//F(15,2)); rem=R-n*F(15,2)
    rises=[F(15,2)]*n+([rem] if rem>0 else [])
    if variation(rises)>F(3,8): naive_bad+=1
    # equal division: smallest N with R/N <= 7.75
    N=1
    while R/N>F(31,4): N+=1
    if variation([R/N]*N)>0: eq_bad+=1
    # marking each step cumulatively rounded to 1/16
    marks=[q(R*i/N,16) for i in range(N+1)]
    rs=[marks[i+1]-marks[i] for i in range(N)]
    cum_max=max(cum_max,variation(rs))
    # repeating one rounded riser (tape-measure habit): last step absorbs the error
    r=q(R/N,16); rs2=[r]*(N-1)+[R-r*(N-1)]
    v=variation(rs2); drift_worst=max(drift_worst,v)
    if v>F(3,8): drift_bad+=1
    if R/N>F(31,4): nover+=1
print("heights",n_tot,"fixed-7.5 breaks 3/8 rule",naive_bad,"(%.1f%%)"%(100*naive_bad/n_tot))
print("equal-division variation>0:",eq_bad,"riser over 7.75:",nover)
print("cumulative marking worst variation",float(cum_max),"in")
print("repeat-rounded-riser worst variation",float(drift_worst),"in, breaks 3/8 on",drift_bad)
ok=naive_bad/n_tot>0.85 and eq_bad==0 and cum_max<=F(1,16) and drift_bad>0
print("RESULT: %s fixed-7.5 breaks rule on %.1f%% of %d heights; equal division 0 breaks; cumulative marks worst %.4f in; repeat-rounded riser breaks on %d, worst %.3f in"%("PASS" if ok else "FAIL",100*naive_bad/n_tot,n_tot,float(cum_max),drift_bad,float(drift_worst)))
