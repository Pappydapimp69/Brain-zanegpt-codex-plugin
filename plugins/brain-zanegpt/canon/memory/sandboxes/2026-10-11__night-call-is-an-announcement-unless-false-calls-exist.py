"""Sandbox: can a night call from a missing member guide a search without
announcing the disappearance (and without naming who calls)?

Toy model, assumed constants. Per night: m = prior that someone is currently
missing. A missing member calls with C = 0.9. The woods also produce FALSE
calls (hallucination) at rate F, regardless. A call names nobody.
1) Posterior P(missing | call) vs F -- with F = 0 a call IS the announcement.
2) Cost: wasted search nights per real one = F(1-m) / (C m).
3) Skill path: real calls come from a stable bearing (sigma 2 of 24 sectors,
   person drifts slowly); false calls come from a uniform bearing. Two calls on
   consecutive nights within 3 sectors = "consistent". Measure the posterior
   after a consistent pair by simulation.
"""
import math
import random

SECTORS, C, M, TRIALS = 24, 0.9, 0.15, 60000


def post(f, m=M):
    return C * m / (C * m + f * (1 - m))


def sdist(a, b):
    d = abs(a - b) % SECTORS
    return min(d, SECTORS - d)


def consistent_rate(real, rng):
    hits = 0
    for _ in range(TRIALS):
        if real:
            pos = rng.randrange(SECTORS)
            b1 = round(pos + rng.gauss(0, 2))
            pos2 = pos + round(rng.gauss(0, 1))
            b2 = round(pos2 + rng.gauss(0, 2))
        else:
            b1, b2 = rng.randrange(SECTORS), rng.randrange(SECTORS)
        hits += sdist(b1 % SECTORS, b2 % SECTORS) <= 3
    return hits / TRIALS


def main():
    rng = random.Random(7)
    for f in (0.0, 0.05, 0.10, 0.15, 0.25):
        waste = f * (1 - M) / (C * M)
        print(f"F={f:.2f}: P(missing|call)={post(f):.3f}  wasted searches per real={waste:.2f}")
    pr, pf = consistent_rate(True, rng), consistent_rate(False, rng)
    f = 0.15
    # two calls on consecutive nights, then consistency
    prior_pair_real = (C * M) ** 2
    prior_pair_false = (f * (1 - M)) ** 2
    post_pair = prior_pair_real / (prior_pair_real + prior_pair_false)
    post_cons = prior_pair_real * pr / (prior_pair_real * pr + prior_pair_false * pf)
    print(f"consistent-pair rate: real {pr:.3f} false {pf:.3f}")
    print(f"F=0.15 one call {post(f):.3f} -> two calls {post_pair:.3f} -> two consistent {post_cons:.3f}")
    f_for_06 = C * M * (1 - 0.6) / (0.6 * (1 - M))
    checks = [
        ("F=0 makes a call certain proof (posterior 1.0)", post(0.0) == 1.0),
        (f"F needed for posterior <= 0.6 is >= 0.10 (got {f_for_06:.3f})", f_for_06 >= 0.10),
        ("at that F, wasted searches per real >= 0.6", f_for_06 * (1 - M) / (C * M) >= 0.6),
        (f"consistency raises one-call posterior at F=0.15 to >= 0.85 (got {post_cons:.3f})", post_cons >= 0.85),
        (f"false pairs look consistent < 0.35 of the time (got {pf:.3f})", pf < 0.35),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"F for 0.6 = {f_for_06:.3f}; one call {post(0.15):.3f}, consistent pair {post_cons:.3f}")


if __name__ == "__main__":
    main()
