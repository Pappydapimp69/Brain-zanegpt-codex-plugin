"""Oral transmission of one 'strange' checkable detail (a shoreline that lay
further seaward) across generations.

Model (stdlib, deterministic):
- Each generation N tellers learn the story from the previous generation's
  consensus. Each teller independently rationalises the strange detail away
  with probability eps (Bartlett: the strange part goes first, and the
  rationalised version is stable, so loss is absorbing).
- The generation's consensus keeps the detail if a strict majority kept it.
- A common shock c per generation rationalises it for everyone at once
  (shared schema: the present coastline contradicts the story).
- 25 years per generation.
Target from the kernel: survival to 7250 years (290 generations) at the
youngest dated tradition, against the folklorists' 500-800 year ceiling.
"""
import math
import random

YEARS_PER_GEN = 25
TARGET_YEARS = 7250


def p_keep_majority(n, eps):
    """P(strict majority of n tellers keep the detail)."""
    need = n // 2 + 1
    return sum(math.comb(n, k) * (1 - eps) ** k * eps ** (n - k) for k in range(need, n + 1))


def half_life_gens(n, eps, c=0.0):
    s = p_keep_majority(n, eps) * (1 - c)
    if s >= 1.0:
        return float("inf")
    return math.log(2) / -math.log(s)


def mc_half_life(n, eps, c, runs, seed):
    rng = random.Random(seed)
    lifetimes = []
    for _ in range(runs):
        g = 0
        while True:
            g += 1
            if rng.random() < c:
                break
            kept = sum(1 for _ in range(n) if rng.random() >= eps)
            if kept <= n // 2:
                break
            if g > 200000:
                break
        lifetimes.append(g)
    lifetimes.sort()
    # median lifetime ~ geometric median; compare to analytic median ceil(hl)
    return lifetimes[len(lifetimes) // 2]


def yrs(g):
    return g * YEARS_PER_GEN


def main():
    ok = True
    rows = []
    # 1) single chain calibration: which eps gives the 500-800 yr consensus?
    for eps in (0.02, 0.03, 0.04):
        hl = half_life_gens(1, eps)
        rows.append(("single", 1, eps, 0.0, hl))
    hl_single = half_life_gens(1, 0.03)
    print(f"single chain eps=0.03: half-life {hl_single:.1f} gens = {yrs(hl_single):.0f} yr")
    ok &= 500 <= yrs(hl_single) <= 800

    # 2) majority correction with independent errors
    res = {}
    for n in (3, 5, 7):
        hl = half_life_gens(n, 0.03)
        res[n] = hl
        print(f"majority N={n} eps=0.03: half-life {hl:.0f} gens = {yrs(hl):.0f} yr")
    ok &= yrs(res[3]) < TARGET_YEARS  # predicted: N=3 falls short
    ok &= yrs(res[5]) >= TARGET_YEARS

    # push: largest eps at which N=5 and N=7 still reach 7250 yr
    for n in (3, 5, 7, 9):
        lo, hi = 0.0, 0.5
        for _ in range(60):
            mid = (lo + hi) / 2
            if yrs(half_life_gens(n, mid)) >= TARGET_YEARS:
                lo = mid
            else:
                hi = mid
        print(f"N={n}: max per-teller eps for 7250-yr half-life = {lo:.4f}")
        res[("eps_max", n)] = lo

    # 3) BREAK: correlated (common-shock) rationalisation
    for c in (0.001, 0.0024, 0.005):
        for n in (5, 9):
            hl = half_life_gens(n, 0.03, c)
            res[("c", c, n)] = hl
            print(f"common shock c={c} N={n}: half-life {hl:.0f} gens = {yrs(hl):.0f} yr")
    ok &= yrs(res[("c", 0.005, 9)]) < TARGET_YEARS
    ok &= res[("c", 0.005, 9)] <= 139
    c_max = 1 - 2 ** (-1 / (TARGET_YEARS / YEARS_PER_GEN))
    print(f"common-shock ceiling for 7250 yr even with perfect majority: c <= {c_max:.5f}/gen "
          f"(one shared rationalisation per {1 / c_max:.0f} gens)")

    # 4) Monte Carlo cross-check of the analytic model (N=3)
    hl3 = half_life_gens(3, 0.03)
    med = mc_half_life(3, 0.03, 0.0, 2001, seed=7)
    # median of geometric lifetime = ceil(log 0.5 / log s)
    exp_med = math.ceil(math.log(0.5) / math.log(p_keep_majority(3, 0.03)))
    rel = abs(med - exp_med) / exp_med
    print(f"MC N=3 median lifetime {med} gens vs analytic {exp_med} (rel diff {rel:.3f}); hl {hl3:.1f}")
    ok &= rel < 0.10

    summary = (f"single eps.03 {yrs(hl_single):.0f} yr; majority N3 {yrs(res[3]):.0f} yr, "
               f"N5 {yrs(res[5]):.0f} yr; eps_max N5 {res[('eps_max', 5)]:.3f}; "
               f"common shock .005 caps N9 at {yrs(res[('c', 0.005, 9)]):.0f} yr; "
               f"MC rel diff {rel:.3f}")
    print(("RESULT: PASS " if ok else "RESULT: FAIL ") + summary)


if __name__ == "__main__":
    main()
