# Sandbox: does "docs 84% vs Stack Overflow 80%" (multi-select survey) support "docs are where most learning happens"?
import math

def z_diff(p1, p2, n, rho):
    # paired (same respondents) difference of two proportions; rho = correlation of the two yes/no answers
    var = (p1*(1-p1) + p2*(1-p2) - 2*rho*math.sqrt(p1*(1-p1)*p2*(1-p2))) / n
    return (p1 - p2) / math.sqrt(var)

# Scenario 1: n=65000, lead 84 vs 80, across correlations -0.5..0.9
z1 = [z_diff(.84, .80, 65000, r) for r in (-0.5, 0, 0.5, 0.9)]
print("S1 n=65000 z by rho:", [round(z, 1) for z in z1])
s1 = min(z1) > 1.96

# Scenario 2 (BREAK): same lead, n=1000, independent answers
z2 = z_diff(.84, .80, 1000, 0)
print("S2 n=1000 rho=0 z:", round(z2, 2))
s2 = z2 < 1.96 + 1  # lead stops being clearly significant (z about 2.1)
s2_nonrobust = z_diff(.84, .80, 400, 0) < 1.96

# Scenario 3 (BREAK): reach vs time share. 100 devs; 84 touch docs, 80 touch SO.
# Diataxis split of docs sessions: type -> (share of docs visits, minutes/visit, prose fraction of page)
docs_types = {"tutorial": (.2, 20, .5), "howto": (.3, 5, .3), "reference": (.4, 2, .6), "explanation": (.1, 10, .9)}
SO_MIN = 4  # minutes per SO visit, example-heavy answers
visits_docs, visits_so = 3, 6   # per touching developer in the period
def docs_minutes(skip_prose):
    m = 0
    for share, mins, prose in docs_types.values():
        eff = mins * (1 - prose*skip_prose)   # copy-first readers skip prose (examples-over-prose)
        m += share * eff
    return 84 * visits_docs * m
so_minutes = 80 * visits_so * SO_MIN
d0, d1 = docs_minutes(0.0), docs_minutes(0.8)
print("S3 minutes docs(read all)=%.0f docs(copy-first)=%.0f SO=%.0f" % (d0, d1, so_minutes))
reach_docs_first = 84 > 80
# break-even SO minutes per visit at which time share ties docs, per reader model
be0 = d0 / (80 * visits_so)
be1 = d1 / (80 * visits_so)
print("S3 break-even SO min/visit: read-all=%.2f copy-first=%.2f (SO assumed %d)" % (be0, be1, SO_MIN))
# docs wins reach at 84>80 regardless; wins time only if SO visits are shorter than the break-even
ok = s1 and s2 and reach_docs_first and be1 < be0 and (be0 - be1) / be0 > 0.3 and not (d1 > so_minutes)
print("RESULT: %s docs lead is significant at n=65000 for every rho (min z %.1f) but marginal at n=1000 (z %.2f); reach says docs first yet time share has SO first (%.0f vs %.0f min) and copy-first reading cuts docs break-even from %.2f to %.2f min/visit"
      % ("PASS" if ok else "FAIL", min(z1), z2, d1, so_minutes, be0, be1))
