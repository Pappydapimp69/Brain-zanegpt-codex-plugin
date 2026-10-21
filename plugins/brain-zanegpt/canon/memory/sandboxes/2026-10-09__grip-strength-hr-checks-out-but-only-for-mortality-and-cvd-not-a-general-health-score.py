"""Sandbox: grip-strength-predicts-mortality kernel, checked against the real source record.

Source snapshot (embedded below): Findings + Interpretation paragraphs of the PubMed/MEDLINE
abstract for Leong et al., Lancet 2015, PMID 25982160, DOI 10.1016/s0140-6736(14)62000-6,
retrieved via the Europe PMC REST API; and the Results numbers of Mandsager et al. 2018
(PMID 30646252, DOI 10.1001/jamanetworkopen.2018.3605) from the same API.
Full text of both papers was NOT accessed; only abstracts.

PREDICTION (written before the first run):
 P1 every number the kernel quotes (5 HRs with CIs and p, n=139,691, 3,379 deaths, 4.0 y) appears
    verbatim in the source abstract: 100% of checks pass.
 P2 CI-implied p (normal approx on log-HR, nominal rounded inputs) agrees with the reported p
    bound for 4 of 5 outcomes; the stroke row (1.09, 1.05-1.15, "p<0.0001") nominally gives
    p ~ 1.2e-4 (a nominal mismatch) yet is reachable under rounding of the printed digits.
 P3 Extrapolating the per-5-kg HR log-linearly, the Mandsager low-vs-elite contrast (HR 5.04)
    corresponds to ~54 kg (+/-1) of grip difference, i.e. beyond any plausible span: the per-5-kg
    figure cannot be stretched across a tier-style contrast.
 P4 Applying the ACSM 2-10 percent load step to a 30 kg baseline needing +5 kg: 2 steps at 10
    percent, 9 steps at 2 percent (arithmetic only; says nothing about causality).
 P5 the abstract's own outcome list limits the claim: it reports NO significant association
    for diabetes, falls, fracture, and the opposite sign for cancer in high-income countries.
"""
import math, re

PURE_FINDINGS = ('Between January, 2003, and December, 2009, a total of 142,861 participants were enrolled in the PURE study, of whom 139,691 with known vital status were included in the analysis. During a median follow-up of 4.0 years (IQR 2.9-5.1), 3379 (2%) of 139,691 participants died. After adjustment, the association between grip strength and each outcome, with the exceptions of cancer and hospital admission due to respiratory illness, was similar across country-income strata. Grip strength was inversely associated with all-cause mortality (hazard ratio per 5 kg reduction in grip strength 1.16, 95% CI 1.13-1.20; p<0.0001), cardiovascular mortality (1.17, 1.11-1.24; p<0.0001), non-cardiovascular mortality (1.17, 1.12-1.21; p<0.0001), myocardial infarction (1.07, 1.02-1.11; p=0.002), and stroke (1.09, 1.05-1.15; p<0.0001). Grip strength was a stronger predictor of all-cause and cardiovascular mortality than systolic blood pressure. We found no significant association between grip strength and incident diabetes, risk of hospital admission for pneumonia or COPD, injury from fall, or fracture. In high-income countries, the risk of cancer and grip strength were positively associated (0.916, 0.880-0.953; p<0.0001), but this association was not found in middle-income and low-income countries.')
PURE_INTERP = ('This study suggests that measurement of grip strength is a simple, inexpensive risk-stratifying method for all-cause death, cardiovascular death, and cardiovascular disease. Further research is needed to identify determinants of muscular strength and to test whether improvement in strength reduces mortality and cardiovascular disease.')
MAND_LOW_ELITE_HR = 5.04      # low vs elite fitness, adjusted HR (abstract)
MAND_BELOW_ABOVE_HR = 1.41    # below-average vs above-average fitness (abstract)
MAND_SMOKING_HR = 1.41        # smoking (abstract)

fails = []
def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))
    if not ok:
        fails.append(name)

# ---- Scenario 1: transcription fidelity of every number in the kernel -------------------
kernel_claims = [
    "139,691", "3379", "4.0 years",
    "1.16, 95% CI 1.13-1.20; p<0.0001",
    "(1.17, 1.11-1.24; p<0.0001)",
    "(1.17, 1.12-1.21; p<0.0001)",
    "(1.07, 1.02-1.11; p=0.002)",
    "(1.09, 1.05-1.15; p<0.0001)",
    "per 5 kg reduction",
    "stronger predictor of all-cause and cardiovascular mortality than systolic blood pressure",
]
for c in kernel_claims:
    check("S1 source contains: " + c, c in PURE_FINDINGS)
n_ok = sum(1 for c in kernel_claims if c in PURE_FINDINGS)

# ---- Scenario 2: do reported CI and p agree? (normal approx on log-HR) -------------------
def p_from_ci(hr, lo, hi):
    se = (math.log(hi) - math.log(lo)) / (2 * 1.959964)
    z = math.log(hr) / se
    p = math.erfc(abs(z) / math.sqrt(2))
    return se, z, p
rows = {  # outcome: (hr_per_5kg, lo, hi, reported_bound_kind, reported_p)
    "all-cause": (1.16, 1.13, 1.20, "<", 1e-4),
    "cv-death": (1.17, 1.11, 1.24, "<", 1e-4),
    "non-cv-death": (1.17, 1.12, 1.21, "<", 1e-4),
    "MI": (1.07, 1.02, 1.11, "=", 0.002),
    "stroke": (1.09, 1.05, 1.15, "<", 1e-4),
}
nominal_agree = 0
for k, (hr, lo, hi, kind, rp) in rows.items():
    se, z, p = p_from_ci(hr, lo, hi)
    if kind == "<":
        ok = p < rp
    else:  # '=' : reported to 1 sig fig, agree if rounds to the same value
        ok = abs(p - rp) < 0.0005
    nominal_agree += ok
    center = math.sqrt(lo * hi)
    print("     %-12s z=%.2f p=%.2e  ci-geo-center=%.3f vs hr=%.2f  nominal-agree=%s" % (k, z, p, center, hr, ok))
check("S2 nominal CI-vs-p agreement is 4 of 5 (stroke is the mismatch)", nominal_agree == 4, "agree=%d" % nominal_agree)

# stroke: is "p<0.0001" reachable if each printed 2-dp digit is rounded (+/-0.005)?
best = 0
steps = [-1, -0.5, 0, 0.5, 1]
for dh in steps:
    for dl in steps:
        for du in steps:
            h, l, u = 1.09 + .005 * dh, 1.05 + .005 * dl, 1.15 + .005 * du
            if l < h < u:
                best = max(best, p_from_ci(h, l, u)[1])
p_best = math.erfc(best / math.sqrt(2))
check("S2b stroke p<0.0001 reachable under rounding of printed digits", p_best < 1e-4, "best z=%.2f p=%.1e" % (best, p_best))

# ---- Scenario 3 (BREAK): stretch per-5-kg HR to a tier-style contrast --------------------
hr5 = 1.16
def kg_for(hr_target):
    return 5 * math.log(hr_target) / math.log(hr5)
kg_elite = kg_for(MAND_LOW_ELITE_HR)
kg_tier = kg_for(MAND_BELOW_ABOVE_HR)
kg_smoke = kg_for(MAND_SMOKING_HR)
print("     log-linear grip gap equal to: below-vs-above fitness %.1f kg, smoking %.1f kg, low-vs-elite fitness %.1f kg"
      % (kg_tier, kg_smoke, kg_elite))
check("S3 low-vs-elite HR needs ~54 kg of grip gap (53..56)", 53 <= kg_elite <= 56, "%.1f kg" % kg_elite)
for span in (20, 30, 40):   # HYPOTHETICAL grip spans for a bottom-vs-top contrast, not data
    print("     hypothetical grip span %d kg -> implied HR %.2f (vs fitness low-vs-elite %.2f)"
          % (span, hr5 ** (span / 5), MAND_LOW_ELITE_HR))
check("S3b a 40 kg span still yields HR well below 5.04", hr5 ** 8 < MAND_LOW_ELITE_HR / 1.5, "%.2f" % (hr5 ** 8))
# smoking-equivalent: ~11.6 kg, a modest, plausible gap -> grip is comparable to a clinical risk factor
check("S3c smoking-sized HR corresponds to ~11-12 kg of grip", 11 <= kg_smoke <= 12.5, "%.1f kg" % kg_smoke)

# ---- Scenario 4: progressive-overload arithmetic (ACSM 2-10 percent step) ----------------
def steps_needed(base, gain, r):
    return math.ceil(round(math.log((base + gain) / base) / math.log(1 + r), 9))
s10, s2 = steps_needed(30, 5, 0.10), steps_needed(30, 5, 0.02)
print("     +5 kg from 30 kg: %d steps at 10%%, %d steps at 2%%" % (s10, s2))
# NOTE: the written prediction P4 said 9 steps at 2 percent; that was an arithmetic slip
# (ln(35/30)/ln(1.02) = 7.78 -> 8). Kept in the docstring on purpose; the check uses the correct value.
check("S4 30 kg +5 kg takes 2 steps at 10% and 8 at 2% (prediction said 9: miss, see note)", (s10, s2) == (2, 8))
check("S4b source itself refuses the causal reading (needs to test whether improving strength reduces mortality)",
      "test whether improvement in strength reduces mortality" in PURE_INTERP)

# ---- Scenario 5 (BREAK): what the kernel's 'overall health risk' wording leaves out -------
nulls = [w for w in ("diabetes", "injury from fall", "fracture") if w in PURE_FINDINGS]
check("S5 abstract lists null outcomes: diabetes, falls, fracture", len(nulls) == 3, ",".join(nulls))
cancer = re.search(r"cancer and grip strength were positively associated \(([0-9.]+),", PURE_FINDINGS)
check("S5b cancer in high-income countries runs the opposite way (HR<1 per 5 kg reduction)", bool(cancer) and float(cancer.group(1)) < 1, cancer.group(1) if cancer else "")
check("S5c abstract gives no SBP hazard ratio, so 'stronger than SBP' is not numerically re-checkable here",
      not re.search(r"systolic blood pressure[^.]*\d\.\d\d", PURE_FINDINGS))

print("     transcription %d/%d ; nominal p agreement %d/5" % (n_ok, len(kernel_claims), nominal_agree))
if fails:
    print("RESULT: FAIL %d check(s) failed: %s" % (len(fails), "; ".join(fails)))
else:
    print("RESULT: PASS numbers match source %d/%d; CI/p agree 4/5 nominal (stroke 5/5 under rounding); per-5kg HR implies %.0f kg for low-vs-elite so it cannot stretch to tier contrasts; abstract limits claim to mortality/CVD (diabetes, falls, fracture null; cancer reversed)" % (n_ok, len(kernel_claims), kg_elite))
