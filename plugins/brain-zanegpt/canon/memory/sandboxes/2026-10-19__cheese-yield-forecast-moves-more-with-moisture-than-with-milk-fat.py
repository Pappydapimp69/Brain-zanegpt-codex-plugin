"""Van Slyke-style yield (kg cheese per 100 kg milk): Y = (0.93*F + C - 0.1) * 1.09 / (1 - M)
F milk fat %, C casein %, M cheese moisture fraction. Real scenario: 100 kg of 3.5% fat, 2.5% casein milk -> cheddar at 37% moisture.
Prediction (before run): baseline Y ~ 9.2 kg (+-0.3); +1 point of moisture raises yield ~1.6% relative, and
that equals the effect of ~0.25 points of milk fat (hidden-parameter parity); BREAK: at fresh-cheese moisture
(75%) one moisture point moves yield ~4% relative, more than twice the cheddar sensitivity."""
def Y(F=3.5,C=2.5,M=0.37): return (0.93*F+C-0.1)*1.09/(1-M)
base=Y()
d_m=Y(M=0.38)/base-1
d_f_per_pt=(Y(F=4.5)/base-1)          # per 1 fat point
fat_equiv=d_m/d_f_per_pt              # fat points equal to 1 moisture point
fresh=Y(M=0.76)/Y(M=0.75)-1
print(f"base {base:.2f} kg; +1pt moisture {d_m:.2%}; 1 fat point {d_f_per_pt:.2%}; moisture point = {fat_equiv:.2f} fat points; fresh cheese +1pt moisture {fresh:.2%}")
ok=abs(base-9.2)<0.3 and 0.014<=d_m<=0.018 and 0.20<=fat_equiv<=0.30 and fresh>2*d_m
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" base {base:.2f} kg/100kg; 1pt moisture {d_m:.2%} = {fat_equiv:.2f} fat points; fresh cheese {fresh:.2%}")
