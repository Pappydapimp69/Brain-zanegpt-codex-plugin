"""Prediction (before run): (1) SEC bulletin figure reproduces: $100k, 4% growth, 20 y, fee 1.00% vs 0.25% -> gap close to
$30k (within $2.5k). (2) Texas SSB figure reproduces: $200/mo from 25 vs $400/mo from 45 at 6% to 65 -> 400,290 vs 185,740
within 1% under monthly compounding. (3) For a 60k earner contributing 8% of income for 30 y at 4% growth, the kernel's
2.6-3.2 point savings-rate suppression costs more final wealth than a 0.75 point fee difference on the same contributions,
in at least 2 of 3 income levels, and the two effects cross when the saver contributes >= ~24% of income (fee drag grows
with the balance, savings suppression with income). Deterministic closed-form/iterative arithmetic, no RNG."""
def fv_lump(p, r, n): return p * (1 + r) ** n
def fv_monthly(pmt, annual, years):
    r = annual / 12; n = years * 12
    return pmt * (((1 + r) ** n - 1) / r)
s1 = fv_lump(100000, .04 - .0025, 20) - fv_lump(100000, .04 - .0100, 20)
print("s1 SEC gap", round(s1))
a, b = fv_monthly(200, .06, 40), fv_monthly(400, .06, 20)
print("s2 Texas monthly-compound 200 from 25:", round(a), "400 from 45:", round(b))
def final(income, rate, growth, years, fee=0.0):
    bal = 0.0
    for _ in range(years):
        bal = bal * (1 + growth - fee) + income * rate
    return bal
rows = []
for income in (40000, 60000, 90000):
    base = final(income, .08, .04, 30, fee=.0025)
    supp = final(income, .08 - .029, .04, 30, fee=.0025)     # kernel midpoint 2.9 points less saved
    fee = final(income, .08, .04, 30, fee=.0100)               # 0.75 point higher fee
    rows.append((income, base - supp, base - fee))
    print("s3 income", income, "savings-suppression cost", round(base - supp), "fee cost", round(base - fee))
# crossover: contribution rate where fee cost == savings cost (60k)
cross = None
for k in range(8, 61):
    r = k / 100
    c_sup = final(60000, r, .04, 30, .0025) - final(60000, r - .029, .04, 30, .0025)
    c_fee = final(60000, r, .04, 30, .0025) - final(60000, r, .04, 30, .0100)
    if cross is None and c_fee >= c_sup: cross = k
print("s4 fee cost overtakes suppression at contribution rate", cross, "%")
ok1 = abs(s1 - 30000) <= 2500
ok2 = abs(a - 400290) / 400290 < .01 and abs(b - 185740) / 185740 < .01
ok3 = sum(1 for _, s, f in rows if s > f) >= 2
ok4 = cross is not None and 15 <= cross <= 35
print("RESULT: %s sec_gap=%d texas=%d/%d suppression_beats_fee_at_%d_of_3_incomes crossover_rate=%s%%" % ("PASS" if ok1 and ok2 and ok3 and ok4 else "FAIL", round(s1), round(a), round(b), sum(1 for _, s, f in rows if s > f), cross))
