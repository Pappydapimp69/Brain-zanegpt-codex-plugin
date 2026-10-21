from fractions import Fraction as F
# Two equal-distance legs at 30 and 60 mpg; also unequal splits; average economy = total distance / total fuel
def avg(legs):  # legs: [(miles, mpg)]
    return sum(F(m) for m,_ in legs)/sum(F(m)/F(g) for m,g in legs)
eq=avg([(100,30),(100,60)]); arith=F(30+60,2)
print(f"equal 100+100 miles at 30 and 60 mpg: true {float(eq):.2f} mpg, arithmetic mean {float(arith):.2f} (overstates {float(arith/eq-1):.1%})")
# equal fuel instead of equal distance: arithmetic mean is then correct
fuel=[(F(5)*30,30),(F(5)*60,60)]
ef=avg(fuel); print(f"equal 5 gal each leg: true {float(ef):.2f} mpg (arithmetic correct)")
# sweep: share of miles at the better economy
worst=0
for pct in range(0,101,10):
    legs=[(100-pct,30),(pct,60)]
    t=avg([l for l in legs if l[0]>0]); naive=F(30)*(100-pct)/100+F(60)*pct/100
    worst=max(worst,float(naive/t-1)); print(f"{pct:3d}% of miles at 60 mpg: true {float(t):.2f}, mile-weighted arithmetic {float(naive):.2f}")
ok = eq==40 and ef==45 and arith==45 and abs(worst-0.125)<1e-9
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"equal distance gives 40.00 mpg not 45 (arithmetic 12.5% high); equal fuel gives 45.00 = arithmetic; mile-weighted arithmetic overstates at every mix, peaking at {worst:.1%} at 50% of miles")
