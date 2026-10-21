"""Newsvendor: critical fractile vs brute force vs 'order the mean'.

Source: Wikipedia "Newsvendor model" — E[profit] = E[p min(q,D)] - c q,
optimal q = F^-1((p-c)/p) with F^-1 the GENERALIZED inverse CDF
(smallest q with F(q) >= CR); normal case q = mu + sigma * Z^-1(CR).

Claim: (i) on discrete (Poisson) demand the generalized-inverse quantile is
exactly the brute-force argmax of expected profit; (ii) the normal
approximation mu + z*sqrt(mu), rounded to nearest, stays within 1% of
optimal expected profit even at small mu; (iii) 'order the mean' is near
optimal only when CR ~ 0.5 and loses >5% when CR is extreme at small mu.

PREDICTION (written before the first run):
 S1 mu=50 CR=0.3 : opt q ~46, normal q 46, normal loss <0.1%, mean loss ~1%
 S2 mu=50 CR=0.9 : opt q ~59, normal q 59, normal loss <0.1%, mean loss ~4%
 S3 mu=2  CR=0.95 (BREAK for order-the-mean): opt q 5, normal q 4,
                   normal loss ~0.15%, mean loss ~22%
 S4 mu=3  CR=0.5 : opt q 3, normal q 3, both losses ~0
 (i) holds 4/4; (ii) holds 4/4; (iii) mean loss >5% only in S3 (and maybe S2).

Exact: Poisson pmf summed to a tail < 1e-15. No RNG, stdlib only.
"""
import math
from statistics import NormalDist


def pois(mu, n):
    pmf = [math.exp(-mu)]
    for k in range(1, n + 1):
        pmf.append(pmf[-1] * mu / k)
    return pmf


def exp_profit(q, p, c, pmf):
    emin = sum(min(q, d) * w for d, w in enumerate(pmf))
    return p * emin - c * q


def run(name, mu, p, c):
    cr = (p - c) / p
    n = int(mu + 40 * math.sqrt(mu) + 60)
    pmf = pois(mu, n)
    prof = [exp_profit(q, p, c, pmf) for q in range(n)]
    q_brute = max(range(n), key=lambda q: (prof[q], -q))
    cdf, q_frac = 0.0, None
    for k, w in enumerate(pmf):
        cdf += w
        if cdf >= cr:
            q_frac = k
            break
    z = NormalDist().inv_cdf(cr)
    q_norm = max(0, round(mu + z * math.sqrt(mu)))
    q_mean = round(mu)
    best = prof[q_brute]
    loss_n = (best - prof[q_norm]) / best * 100
    loss_m = (best - prof[q_mean]) / best * 100
    print(f"{name}: mu={mu} CR={cr:.2f} q_brute={q_brute} q_fractile={q_frac} "
          f"q_normal={q_norm} q_mean={q_mean} best={best:.3f} "
          f"normal_loss={loss_n:.3f}% mean_loss={loss_m:.2f}%")
    return q_brute == q_frac, loss_n, loss_m


cases = [("S1", 50, 10, 7), ("S2", 50, 10, 1),
         ("S3-break", 2, 20, 1), ("S4", 3, 10, 5)]
res = [run(*c) for c in cases]
frac_ok = sum(r[0] for r in res)
norm_ok = sum(r[1] <= 1.0 for r in res)
mean_bad = [c[0] for c, r in zip(cases, res) if r[2] > 5.0]
ok = frac_ok == 4 and norm_ok == 4 and "S3-break" in mean_bad and "S4" not in mean_bad
print(f"RESULT: {'PASS' if ok else 'FAIL'} fractile==brute {frac_ok}/4; "
      f"normal-approx within 1% {norm_ok}/4; order-the-mean >5% loss in {mean_bad}")
