"""Loop 2 sandbox: fourth-wall 'sanity effects' (Eternal Darkness style: fake
save deletion, fake controller unplug) lose their power on repeat. How should a
game schedule a finite authored pool?
Exact expected values, no RNG. Pool of N authored effects; a playthrough fires M
triggers. An effect's scare value on its k-th showing (k = 0 first) is
r**k (habituation, r = 0.35 assumed). A trigger is a DUD if its value < 0.2.
Policies:
  RANDOM      each trigger picks uniformly from the pool (with repeats)
  SHUFFLE     no repeat until the pool is exhausted, then reshuffle
  VARIANTS    shuffle bag, but each showing is a derived variant whose
              similarity to earlier showings of the same effect is s (0..1);
              value = r**(s*k)   (derived, not authored: the derived-tells kernel)
"""
from fractions import Fraction
import math

R = 0.35


def expected_random(n, m):
    # E[value] of trigger t = sum_k P(this effect seen k times before) r^k
    tot = dud = 0.0
    for t in range(m):
        for k in range(t + 1):
            pk = math.comb(t, k) * (1 / n) ** k * (1 - 1 / n) ** (t - k)
            v = R ** k
            tot += pk * v
            dud += pk * (v < 0.2)
    return tot, dud / m


def shuffle(n, m, s=1.0):
    tot = dud = 0.0
    for t in range(m):
        k = t // n
        v = R ** (s * k)
        tot += v
        dud += v < 0.2
    return tot, dud / m


def main():
    rows = {}
    for n, m in ((8, 8), (8, 16), (8, 24)):
        rows[(n, m)] = (expected_random(n, m), shuffle(n, m), shuffle(n, m, s=0.4))
        (ra, rd), (sa, sd), (va, vd) = rows[(n, m)]
        print(f"pool {n}, triggers {m}: total scare random {ra:.2f} (duds {rd:.2f}) | shuffle {sa:.2f} "
              f"(duds {sd:.2f}) | variants s=0.4 {va:.2f} (duds {vd:.2f})")
    (ra, _), (sa, _), _ = rows[(8, 8)]
    _, (sa16, sd16), (va16, vd16) = rows[(8, 16)]
    _, (sa24, sd24), (va24, vd24) = rows[(8, 24)]
    checks = [
        (f"shuffle bag beats random by >= 25% when triggers = pool (x{sa / ra:.2f})", sa / ra >= 1.25),
        (f"once triggers exceed the pool, shuffle duds jump (16: {sd16:.2f}, 24: {sd24:.2f})", sd24 >= 0.5),
        (f"derived variants keep duds at 0 through 3x the pool (got {vd24:.2f})", vd24 == 0),
        ("break case: with M = N, variants add nothing over shuffle", abs(rows[(8, 8)][2][0] - sa) < 1e-12),
    ]
    held = sum(ok for _, ok in checks)
    for n_, ok in checks:
        print(("held   " if ok else "MISSED ") + n_)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; M=N random {ra:.2f} shuffle {sa:.2f}; "
          f"M=3N shuffle {sa24:.2f} duds {sd24:.2f} vs variants {va24:.2f} duds {vd24:.2f}")


if __name__ == "__main__":
    main()
