# Bike drivetrain arithmetic (exact, no RNG): usable distinct gear ratios of a 2x12 setup, and cross-chain avoidance.
from fractions import Fraction as F
CHAINRINGS=(50,34)                                  # compact double
CASSETTE=(11,12,13,14,15,17,19,21,24,27,30,34)      # a 12-speed 11-34 layout
combos=[(c,s) for c in CHAINRINGS for s in CASSETTE]
ratio=lambda c,s: F(c,s)
print("nominal gears:",len(combos))
def distinct(rs,tol):                                # count ratios once a step under tol (relative) is merged
    rs=sorted(set(rs)); out=[rs[0]]
    for r in rs[1:]:
        if (r-out[-1])/out[-1] >= tol: out.append(r)
    return len(out)
allr=[ratio(c,s) for c,s in combos]
d_exact=len(set(allr)); d3=distinct(allr,F(3,100)); d5=distinct(allr,F(5,100))
print("distinct exact:",d_exact,"| steps >=3%:",d3,"| steps >=5%:",d5)
# cross-chain: big ring on the 3 biggest cogs, small ring on the 3 smallest cogs are avoided
def ok(c,s): return not (c==50 and s in CASSETTE[-3:]) and not (c==34 and s in CASSETTE[:3])
usable=[(c,s) for c,s in combos if ok(c,s)]
dU3=distinct([ratio(c,s) for c,s in usable],F(3,100))
print("usable after cross-chain rule:",len(usable),"| distinct steps >=3% among usable:",dU3)
# overlap region: ratios the two rings both reach within 3%
small=[ratio(34,s) for s in CASSETTE]; big=[ratio(50,s) for s in CASSETTE]
overlap=sum(1 for b in big if any(abs(b-x)/x<F(3,100) for x in small))
print("big-ring gears matched by a small-ring gear within 3%:",overlap)
gearinch=lambda c,s: float(F(c,s))*27.0   # 700c wheel ~27 in
print("gear inches range:",round(gearinch(34,34),1),"-",round(gearinch(50,11),1))
okr = len(combos)==24 and len(usable)==18 and d3<=len(combos) and overlap>=3 and dU3<=18
print(("RESULT: PASS" if okr else "RESULT: FAIL"),f"24 nominal gears -> {len(usable)} cross-chain-safe -> {dU3} distinct at 3% steps; {overlap} big-ring gears duplicated by the small ring; {round(gearinch(34,34),1)}-{round(gearinch(50,11),1)} gear inches")
