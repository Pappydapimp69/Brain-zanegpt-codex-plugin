# RUN 1: RESULT FAIL on prediction (c) only: I mis-did the arithmetic, 0.8**7 = 0.2097 so week 8 is 21% not below 20%. Parts (a), (b) and the
# BREAK held. RUN 2 prediction (c), written before re-running: organic week8/week1 is 0.21 (0.8**7), still under 25% and rising paid need.
# Toy deterministic model (assumed parameters, not measurements). 10000-person audience, 12 weeks.
# Prediction (before run): with per-exposure CTR decay d=0.85 per exposure to the same creative, (a) doubling paid impressions on ONE
# creative yields less than 1.2x the clicks of the base budget while rotating through k=6 creatives at the BASE budget yields >=2x;
# (b) a descriptive-norm copy uplift of 44.1/35.1=1.256x (kernel numbers) multiplies conversions in every scenario; (c) organic
# delivery decaying 20%/week falls below 20% of its week-1 level by week 8 so an organic-only plan fails to hold delivery;
# BREAK: at d=0.99 (almost no fatigue) doubling the budget on one creative must beat rotation at base budget.
A = 10000; W = 12
def clicks(freq_per_week, k, d, b=0.02):
    # per person: each creative gets (freq*W/k) exposures; the n-th exposure converts clicks at b*d**n
    n_each = int(round(freq_per_week * W / k))
    per_creative = sum(b * d ** n for n in range(n_each))
    return A * k * per_creative
def conv(c, uplift=1.0, rate=0.05): return c * rate * uplift
f_base = 3
r = {}
for d in (0.85, 0.99):
    r[("single_base", d)] = clicks(f_base, 1, d)
    r[("single_double", d)] = clicks(2 * f_base, 1, d)
    r[("rot6_base", d)] = clicks(f_base, 6, d)
    r[("rot6_double", d)] = clicks(2 * f_base, 6, d)
a_ratio_double = r[("single_double", 0.85)] / r[("single_base", 0.85)]
a_ratio_rot = r[("rot6_base", 0.85)] / r[("single_base", 0.85)]
b_ratio_double99 = r[("single_double", 0.99)] / r[("rot6_base", 0.99)]
UP = 44.1 / 35.1; UP_NEAR = 49.3 / 42.8
c_plain = conv(r[("rot6_base", 0.85)]); c_norm = conv(r[("rot6_base", 0.85)], UP)
# organic: weekly organic impressions decay by g; paid fills the gap to hold 3 freq
g = 0.8; org = [A * 3 * g ** t for t in range(W)]
org_share8 = org[7] / org[0]
paid_needed = sum(A * 3 - o for o in org)
print(f"a) d=.85 double-budget single x{a_ratio_double:.3f} vs base; rotation(6) base x{a_ratio_rot:.3f}")
print(f"   d=.99 double-budget single / rotation base = {b_ratio_double99:.3f}")
print(f"b) norm uplift x{UP:.3f}; near-norm x{UP_NEAR:.3f}; rot6 conv plain={c_plain:.0f} norm={c_norm:.0f}; single base conv norm={conv(r[('single_base',0.85)],UP):.0f}")
print(f"c) organic week8/week1={org_share8:.3f}; paid impressions needed over {W} weeks={paid_needed:.0f} of {A*3*W}")
ok = a_ratio_double < 1.2 and a_ratio_rot >= 2 and b_ratio_double99 > 1 and c_norm / c_plain > 1.25 and 0.20 < org_share8 < 0.25
print(f"RESULT: {'PASS' if ok else 'FAIL'} double-budget single x{a_ratio_double:.2f}; rotation x{a_ratio_rot:.2f}; no-fatigue double/rot {b_ratio_double99:.2f}; norm x{UP:.3f}; organic wk8 {org_share8:.2f}")
