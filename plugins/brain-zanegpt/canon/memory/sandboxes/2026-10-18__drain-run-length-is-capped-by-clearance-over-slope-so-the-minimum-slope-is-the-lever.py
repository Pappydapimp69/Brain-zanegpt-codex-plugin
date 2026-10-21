# Drain run: the pipe must fall `slope` inches per foot of run, so fall = slope * length and
# the longest run that fits a vertical clearance D is D / slope. Model the run foot by foot
# (no closed form used to produce the answer), then compare with the closed form.
# PREDICTION (before run): clearance 3.5 in: at 1/4 in per ft the longest run is 14 ft, at
# 1/8 in per ft it is 28 ft (exactly double); clearance 6 in gives 24 ft and 48 ft; a 1/16 in
# per ft run (below the 1/8 minimum) would fit 56 ft but is not allowed; a run built at 1/4
# when 1/8 would pass wastes exactly half the clearance (fall 2x for every length 4..40 ft);
# and the percent form of 1/4 in per ft is 2.083 percent, so 2 percent (0.24 in per ft) fails
# the 1/4 minimum.
from fractions import Fraction as F
def longest_run(clearance, slope):
    elev, feet = F(clearance), 0
    while elev - slope >= 0:
        elev -= slope; feet += 1
    return feet
cases = [(F(7, 2), F(1, 4)), (F(7, 2), F(1, 8)), (F(6), F(1, 4)), (F(6), F(1, 8))]
got = [longest_run(c, s) for c, s in cases]
closed = [int(c / s) for c, s in cases]
print("longest runs", got, "closed form", closed)
double = all(longest_run(c, F(1, 8)) == 2 * longest_run(c, F(1, 4)) for c in (F(7, 2), F(6), F(9)))
waste = all(L * F(1, 4) == 2 * L * F(1, 8) for L in range(4, 41))
pct = F(1, 4) / 12 * 100
two_pct_ok = F(2, 100) * 12 >= F(1, 4)      # 2 percent = 0.24 in per ft
print("1/4 in per ft = %.3f percent; 2 percent meets 1/4 minimum: %s" % (float(pct), two_pct_ok))
print("below-min 1/16 would fit", longest_run(F(7, 2), F(1, 16)), "ft (not allowed)")
ok = got == [14, 28, 24, 48] == closed and double and waste and abs(float(pct) - 2.083) < 0.001 and not two_pct_ok
print("RESULT: %s longest runs %s ft at clearances 3.5/6 in for 1/4 and 1/8 per ft, 1/8 doubles 1/4 at 3 clearances, 1/4 wastes 2x fall over lengths 4..40, 1/4 in per ft = %.3f%% so 2%% fails the minimum"
      % ("PASS" if ok else "FAIL", got, float(pct)))
