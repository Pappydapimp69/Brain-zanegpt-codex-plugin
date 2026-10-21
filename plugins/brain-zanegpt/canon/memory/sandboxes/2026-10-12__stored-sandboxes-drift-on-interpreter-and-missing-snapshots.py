"""Gap: do Brain's stored sandboxes still reproduce, and what breaks them?
This sandbox demonstrates the interpreter-version cause found when all 1,349
stored sandboxes were re-run on 2026-10-12: since Python 3.12 the built-in
sum() of floats uses compensated summation, so 'reversed order gives a
different float sum' no longer shows with sum(), while a plain accumulation
loop still shows it. Deterministic values, no RNG.
PREDICTION (written before running): on this interpreter (3.13) sum() in two
orders is equal; a plain loop in two orders differs; math.fsum in two orders is
equal. So a sandbox using sum() to demonstrate order dependence passes on 3.11
and fails on 3.12+.
"""
import math
import sys

VALS = [((i * 0.37) % 1) * 10 ** (i % 7 - 3) for i in range(5000)]


def loop(xs):
    a = 0.0
    for v in xs:
        a += v
    return a


def main():
    s_eq = sum(VALS) == sum(reversed(VALS))
    l_eq = loop(VALS) == loop(list(reversed(VALS)))
    f_eq = math.fsum(VALS) == math.fsum(reversed(VALS))
    print(f"python {sys.version.split()[0]}: sum() order-equal {s_eq}; plain loop order-equal {l_eq}; fsum order-equal {f_eq}")
    new = sys.version_info >= (3, 12)
    checks = [
        ("sum() is order-independent on 3.12+ (compensated)", s_eq == new),
        ("a plain accumulation loop is order-dependent", not l_eq),
        ("math.fsum is order-independent", f_eq),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; sum equal {s_eq} loop equal {l_eq} "
          f"fsum equal {f_eq} on {sys.version.split()[0]}")


if __name__ == "__main__":
    main()
