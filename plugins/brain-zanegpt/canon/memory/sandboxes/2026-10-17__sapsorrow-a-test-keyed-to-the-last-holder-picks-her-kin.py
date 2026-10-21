"""Sandbox: The StoryTeller, "Sapsorrow" (1988) -- the dead queen's ring decides the next queen.

Claim under test: a selection test keyed to the previous holder (her ring) favours her
nearest kin, and favours them more the more distinctive she was; with no inheritance
the pull vanishes, and only an exclusion clause removes kin from the pick.

Toy numbers: finger size in the kingdom ~ Normal(50, 4). Ring fits if |size - Q| <= 1
where Q is the dead queen's size. A daughter's expected size regresses toward the mean:
50 + h*(Q - 50), with spread 4*sqrt(1 - h^2) (single-parent regression, h = 0.5).
1000 unrelated eligible women and 3 daughters. Deterministic (closed-form normal CDF).

Prediction written before the first run:
  Q=50 enrichment ~1.1-1.2; Q=58 ~4; Q=62 larger (~10); BREAK h=0 exactly 1.0;
  exclusion clause gives daughters' share 0.
Round 2 prediction (after the ZaneGPT check, before rerun): looser ring 5-20; 2% caste
  near her size below 5; h=0.8 above the 3 sd value; daughters-first about 0.32 vs about
  0.013 in random order.
"""
from math import sqrt
from statistics import NormalDist

MEAN, SD, TOL, STRANGERS, DAUGHTERS = 50.0, 4.0, 1.0, 1000, 3


def fit_prob(mu, sd, q, tol=TOL):
    d = NormalDist(mu, sd)
    return d.cdf(q + tol) - d.cdf(q - tol)


def run(name, q, h, exclude_household=False, tol=TOL, caste=0.0):
    # caste: share of strangers drawn from a tight cluster N(q, 1) around the queen's size
    p_s = (1 - caste) * fit_prob(MEAN, SD, q, tol) + caste * fit_prob(q, 1.0, q, tol)
    kin_sd = SD * sqrt(1 - h * h)
    p_d = fit_prob(MEAN + h * (q - MEAN), kin_sd, q, tol)
    enrich = p_d / p_s
    exp_d = 0.0 if exclude_household else DAUGHTERS * p_d
    exp_s = STRANGERS * p_s
    share = exp_d / (exp_d + exp_s)
    # chance at least one daughter fits (the trap can spring at all)
    p_any_d = 0.0 if exclude_household else 1 - (1 - p_d) ** DAUGHTERS
    print(f"{name}: Q={q:.0f} h={h} tol={tol} caste={caste} stranger fit={p_s:.4f} daughter fit={p_d:.4f} "
          f"enrichment={enrich:.2f} daughters' share of fitters={share:.4f} "
          f"P(some daughter fits)={p_any_d:.3f}")
    return enrich, share, p_any_d


e1, _, _ = run("S1 typical queen", 50, 0.5)
e2, s2, a2 = run("S2 distinctive queen (2 sd)", 58, 0.5)
e3, s3, _ = run("S3 very distinctive queen (3 sd)", 62, 0.5)
e4, _, _ = run("S4 BREAK no inheritance", 58, 0.0)
_, s5, _ = run("S5 control: law bars the king's household", 58, 0.5, exclude_household=True)
# round 2 (added after the ZaneGPT check; predictions written before this rerun)
e6, _, _ = run("S6 3 sd queen, looser ring (tolerance 2)", 62, 0.5, tol=2.0)
e7, s7, _ = run("S7 BREAK2 3 sd queen, 2% of strangers from a caste near her size", 62, 0.5, caste=0.02)
e9, _, _ = run("S9 3 sd queen, stronger inheritance (h=0.8)", 62, 0.8)
# S8 crowd test: in a random trying order the first fitter is a daughter with chance = share;
# if the 3 daughters try first, the trap springs with chance P(some daughter fits).
print(f"S8 crowd test at 2 sd: random order -> daughter picked {s2:.4f}; daughters try first -> {a2:.3f} "
      f"({a2 / s2:.0f}x)")

ok = (1.05 <= e1 <= 1.25 and 3.0 <= e2 <= 5.5 and e3 > e2 and abs(e4 - 1.0) < 1e-9
      and s5 == 0.0 and s3 > s2 and 5 <= e6 <= 20 and e7 < 5 and e9 > e3 and a2 > 10 * s2)
summary = (f"kin enrichment {e1:.2f} (typical queen) -> {e2:.2f} (2 sd) -> {e3:.2f} (3 sd); "
           f"no inheritance {e4:.2f}; exclusion clause share {s5:.0f}; looser ring {e6:.2f}; "
           f"2% caste {e7:.2f}; h=0.8 {e9:.2f}; daughters-first {a2:.3f} vs random order {s2:.4f}")
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + summary)
