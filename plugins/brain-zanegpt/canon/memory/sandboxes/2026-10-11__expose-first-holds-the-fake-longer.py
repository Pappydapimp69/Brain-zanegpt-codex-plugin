"""Sandbox: expose-first vs rescue-narrows, scored on how long a doppelganger
stays at the fire. Seven's rule: holding a fake raises the chance of losing
another. Exact expected values, no RNG.
Per disappearance, a 2-night window. Horizon 6 nights; a fake not resolved in
the window is held to the horizon.
A expose-first: one pylon test per night (2 pylons), deduction 0.45 then 0.55
(1-of-3 after one wrong); exposure ends the fake's stay.
B rescue-narrows (duplicate at fire): a search per night finds with 0.6; on a
find the 1-of-2 pick is made that day (accuracy 0.633 from seven E26; a wrong
first pick is fixed by the second pylon the same day) so the fake leaves.
Knock-on: each fake-held night adds BASE*H extra chance of another loss.
"""
from fractions import Fraction as Fr

HORIZON, BASE, H = 6, Fr(10, 100), Fr(1)


def held_a():
    p1, p2 = Fr(45, 100), Fr(55, 100)
    e = p1 * 1 + (1 - p1) * p2 * 2 + (1 - p1) * (1 - p2) * HORIZON
    pylons = p1 * 1 + (1 - p1) * 2
    return e, pylons


def held_b():
    s = Fr(6, 10)
    q = Fr(633, 1000)
    e = s * 1 + (1 - s) * s * 2 + (1 - s) ** 2 * HORIZON
    found = 1 - (1 - s) ** 2
    pylons = found * (q * 1 + (1 - q) * 2)
    return e, pylons


def main():
    (ea, pa), (eb, pb) = held_a(), held_b()
    xa, xb = ea * BASE * H, eb * BASE * H
    print(f"A expose-first : fake held {float(ea):.3f} nights, pylons {float(pa):.3f}, extra losses {float(xa):.3f}")
    print(f"B rescue-narrows: fake held {float(eb):.3f} nights, pylons {float(pb):.3f}, extra losses {float(xb):.3f}")
    ratio = ea / eb
    checks = [
        (f"A holds the fake >= 1.3x longer than B (got {float(ratio):.3f})", ratio >= Fr(13, 10)),
        ("A causes more knock-on losses than B", xa > xb),
        (f"B spends fewer pylons than A (B {float(pb):.3f} vs A {float(pa):.3f})", pb < pa),
        ("break case: B still holds a fake > 1.5 nights on average", eb > Fr(3, 2)),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"held A {float(ea):.3f} B {float(eb):.3f} ratio {float(ratio):.3f}; pylons A {float(pa):.3f} B {float(pb):.3f}")


if __name__ == "__main__":
    main()
