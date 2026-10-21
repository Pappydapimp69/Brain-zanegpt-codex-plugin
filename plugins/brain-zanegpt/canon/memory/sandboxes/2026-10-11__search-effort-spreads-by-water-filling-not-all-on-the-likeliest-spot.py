"""Sandbox (train gap, SEARCH-THEORY): how to spread a fixed search effort over
areas when detection is imperfect. Koopman's exponential detection law: an area
searched with effort e detects a present target with 1 - exp(-w e). The optimal
split (found greedily, unit by unit, by largest marginal gain p_i * gain) gives
effort only to areas above a cut-off, levelling p_i exp(-w e_i): 'water-filling'.
Applied to SEVEN's night search: prior over 24 sectors from the call bearing
(seven E31's noise values), effort = search hours in 0.25 h units.
Exact, no RNG. Compared: CONCENTRATE (all hours on the likeliest sector), UNIFORM
over the H nearest sectors (seven E31's block search), OPTIMAL (greedy marginal).
"""
import math

S, UNIT, W = 24, 0.25, 1.2


def prior(sigma):
    def cdf(x):
        return 0.5 * (1 + math.erf(x / (sigma * math.sqrt(2))))
    p = {}
    for k in range(-12, 12):
        p[k % S] = p.get(k % S, 0) + cdf(k + 0.5) - cdf(k - 0.5)
    t = sum(p.values())
    return {k: v / t for k, v in p.items()}


def pfind(p, eff):
    return sum(p[i] * (1 - math.exp(-W * eff.get(i, 0.0))) for i in p)


def sdist(a, b):
    d = abs(a - b) % S
    return min(d, S - d)


def concentrate(p, hours):
    top = max(p, key=lambda i: (p[i], -sdist(i, 0)))
    return {top: hours}


def uniform(p, hours, h=4):
    block = sorted(p, key=lambda i: (sdist(i, 0), i))[:h]
    return {i: hours / h for i in block}


def optimal(p, hours):
    eff = {i: 0.0 for i in p}
    for _ in range(int(round(hours / UNIT))):
        best = max(p, key=lambda i: (p[i] * math.exp(-W * eff[i]) * (1 - math.exp(-W * UNIT)), -i))
        eff[best] += UNIT
    return eff


def main():
    rows = {}
    for sigma in (0.6, 1.5, 3.25):
        for hours in (1.0, 4.0, 8.0):
            p = prior(sigma)
            o = optimal(p, hours)
            r = (pfind(p, concentrate(p, hours)), pfind(p, uniform(p, hours)), pfind(p, o),
                 sum(1 for v in o.values() if v > 0))
            rows[(sigma, hours)] = r
            print(f"sigma {sigma:4.2f} hours {hours:3.1f}: concentrate {r[0]:.3f} uniform-4 {r[1]:.3f} "
                  f"optimal {r[2]:.3f} (spread over {r[3]} sectors)")
    checks = [
        ("optimal is never beaten by either simple split",
         all(r[2] >= max(r[0], r[1]) - 1e-12 for r in rows.values())),
        ("more hours -> optimal spreads over more sectors (sigma 1.5)",
         rows[(1.5, 1.0)][3] < rows[(1.5, 4.0)][3] < rows[(1.5, 8.0)][3]),
        ("concentrating everything loses >= 0.15 to optimal with 8 hours at sigma 1.5",
         rows[(1.5, 8.0)][2] - rows[(1.5, 8.0)][0] >= 0.15),
        ("break case: with a very sharp prior and 1 hour, concentrating is within 0.01 of optimal",
         rows[(0.6, 1.0)][2] - rows[(0.6, 1.0)][0] <= 0.01),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"s{sg}/h{hr}: c {r[0]:.3f} u {r[1]:.3f} o {r[2]:.3f} n{r[3]}" for (sg, hr), r in rows.items()))


if __name__ == "__main__":
    main()
