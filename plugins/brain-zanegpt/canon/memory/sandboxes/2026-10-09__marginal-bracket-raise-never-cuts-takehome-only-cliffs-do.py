"""Sandbox: does a raise that crosses a progressive tax bracket ever cut take-home pay?

NOT TAX OR FINANCIAL ADVICE. Toy arithmetic on a published table, no standard
deduction, no state tax, no payroll tax, no credits.

SOURCE EXCERPT (fetched this run from irs.gov "Federal income tax rates and
brackets", 2025 single filer; page text: "You pay tax as a percentage of your
income in layers called tax brackets ... When your income jumps to a higher tax
bracket, you don't pay the higher rate on your entire income. You pay the higher
rate only on the part that's in the new tax bracket."):
  10% $0 - $11,925 | 12% $11,926 - $48,475 | 22% $48,476 - $103,350
  24% $103,351 - $197,300 | 32% $197,301 - $250,525 | 35% $250,526 - $626,350
  37% $626,351 and up

PREDICTIONS (written before the first run):
 P1 layered model: 0 decreases of take-home over taxable income 0..700,000 in $1 steps;
    the smallest one-dollar gain is 0.63 (37% top rate).
 P2 BREAK attempt, naive whole-income-at-one-rate model: exactly 6 decreases (one per threshold).
 P3 hypothetical cliff (a $2,000 benefit lost entirely above $60,000): exactly 1 decrease,
    and the $1,000 raise from 60,000 to 61,000 loses money (22% of 1,000 is 220 tax, 780 kept, minus 2,000).
 P4 tax on 100,000 = 16,914.00 exactly (hand sum 1192.5 + 4386 + 11335.5), average 16.914% < 22% marginal.
 P5 kernel checks: 401k at 80,000 salary, 6% pre-tax with 50% match of first 6%: out-of-pocket 3,744
    for 7,200 into the account; Texas compounding example lands within 1% of 400,290 / 185,740;
    22.15% card interest avoided beats 10.47% taxed at 22% (8.17%).
"""
from fractions import Fraction as F

BR = [(0, F(10, 100)), (11925, F(12, 100)), (48475, F(22, 100)), (103350, F(24, 100)),
      (197300, F(32, 100)), (250525, F(35, 100)), (626350, F(37, 100))]


def layered(x):
    t = F(0)
    for i, (lo, r) in enumerate(BR):
        hi = BR[i + 1][0] if i + 1 < len(BR) else None
        if x <= lo:
            break
        top = x if hi is None else min(x, hi)
        t += (top - lo) * r
    return t


def naive(x):  # the misreading: whole income taxed at the top rate it reaches
    r = BR[0][1]
    for lo, rr in BR:
        if x > lo:
            r = rr
    return x * r


def cliff(x):  # hypothetical benefit rule, NOT any real program
    return layered(x) + (2000 if x > 60000 else 0)


def decreases(f, hi=700000):
    prev = x0 = None
    n = 0
    mingain = None
    for x in range(0, hi + 1):
        net = x - f(x)
        if prev is not None:
            if net < prev:
                n += 1
            g = net - prev
            if mingain is None or g < mingain:
                mingain = g
        prev = net
    return n, mingain


ok = True
n1, g1 = decreases(layered)
print("layered: decreases=%d min one-dollar gain=%s" % (n1, float(g1)))
ok &= (n1 == 0 and g1 == F(63, 100))
n2, _ = decreases(naive)
print("naive whole-income: decreases=%d" % n2)
ok &= (n2 == 6)
n3, _ = decreases(cliff)
d = (61000 - cliff(61000)) - (60000 - cliff(60000))
print("cliff: decreases=%d; 60,000 -> 61,000 raise changes take-home by %s" % (n3, float(d)))
ok &= (n3 == 1 and d < 0)
# $1 across the 12%->22% edge
print("one dollar across 48,475 -> 48,476 raises take-home by %s" % float((48476 - layered(48476)) - (48475 - layered(48475))))
t = layered(100000)
print("tax on 100,000 = %s ; average %.3f%% vs marginal 22%%" % (float(t), float(t / 1000)))
ok &= (t == 16914)
# average rate below marginal everywhere above 0
ok &= all(layered(x) / x <= max(r for lo, r in BR if x > lo) for x in range(1, 700001, 997))
ok &= all(layered(x) / x < max(r for lo, r in BR if x > lo) for x in range(11926, 700001, 997))

# kernel exercise 1: 401k match (ideas PERSONAL-FINANCE/retirement/401k-match)
sal = 80000
contrib = sal * F(6, 100)
match = contrib * F(1, 2)
saved = layered(sal) - layered(sal - contrib)
oop = contrib - saved
print("401k: contrib %s match %s tax saved %s out-of-pocket %s for %s in account (%.2fx)" % (
    float(contrib), float(match), float(saved), float(oop), float(contrib + match), float((contrib + match) / oop)))
ok &= (oop == 3744 and contrib + match == 7200)

# kernel exercise 2: compound interest (ideas PERSONAL-FINANCE/investing/compound-interest)
def fv(pmt, months, ann=0.06):
    r = ann / 12
    return pmt * ((1 + r) ** months - 1) / r
a, b = fv(200, 480), fv(400, 240)
print("compound: early %.0f (source 400,290) late %.0f (source 185,740)" % (a, b))
ok &= abs(a / 400290 - 1) < 0.01 and abs(b / 185740 - 1) < 0.01

# kernel exercise 3: debt payoff vs investing (ideas PERSONAL-FINANCE/debt/payoff-vs-investing)
card, mkt_after = 22.15, 10.47 * (1 - 0.22)
print("payoff vs invest: avoided card interest %.2f%% vs taxed market %.2f%%" % (card, mkt_after))
ok &= card > mkt_after

print("RESULT: %s layered=0 decreases, naive=%d, cliff=%d, tax(100k)=16914, 401k oop=3744" % ("PASS" if ok else "FAIL", n2, n3))
