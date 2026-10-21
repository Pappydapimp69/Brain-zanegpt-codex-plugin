"""Sandbox: seven E29's fix (keep a pylon fallback after a missed rescue window
so the doppelganger is not held to the horizon) priced against the area pylon
budget (blueprint 0.35: area 1 has 3 pylons, later areas 2-4; a lit pylon
shields depth for its area). Exact fractions, no RNG.
Rescue-narrows as in E29: search 0.6 per night over a 2-night window, the
1-of-2 pick costs 1 or 2 pylons (accuracy 0.633). Missed window: without
fallback the fake stays to night 6; with fallback, one pylon test per night
from night 3 at 1-of-4 then 1-of-3 accuracy (0.45, 0.55), up to K tests.
"""
from fractions import Fraction as Fr

S, Q, HORIZON = Fr(6, 10), Fr(633, 1000), 6


def run(k):
    found1, found2, miss = S, (1 - S) * S, (1 - S) ** 2
    held = found1 * 1 + found2 * 2
    pyl = (found1 + found2) * (Q + (1 - Q) * 2)
    # missed: fallback tests on nights 3.. with accuracies
    accs = [Fr(45, 100), Fr(55, 100), Fr(1)][:k]
    p_alive, h, used = Fr(1), Fr(0), Fr(0)
    night = 3
    for a in accs:
        used += p_alive
        h += p_alive * a * night
        p_alive *= (1 - a)
        night += 1
    h += p_alive * HORIZON
    held += miss * h
    pyl += miss * used
    return held, pyl, miss * used


def main():
    res = {k: run(k) for k in (0, 1, 2, 3)}
    for k, (h, p, f) in res.items():
        print(f"fallback tests {k}: fake held {float(h):.3f} nights, pylons {float(p):.3f} (fallback share {float(f):.3f})")
    cut = 1 - res[2][0] / res[0][0]
    checks = [
        (f"two fallback tests cut fake-held nights by >= 0.25 (got {float(cut):.3f})", cut >= Fr(1, 4)),
        (f"fallback costs < 0.25 extra pylons per disappearance (got {float(res[2][2]):.3f})", res[2][2] < Fr(1, 4)),
        (f"total pylons per disappearance with fallback stay under 1.5 (got {float(res[2][1]):.3f})", res[2][1] < Fr(3, 2)),
        ("break case: a third fallback test still lowers held nights", res[3][0] < res[2][0]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"held 0/2/3 tests {float(res[0][0]):.3f}/{float(res[2][0]):.3f}/{float(res[3][0]):.3f}; "
          f"pylons {float(res[0][1]):.3f}/{float(res[2][1]):.3f}; cut {float(cut):.3f}")


if __name__ == "__main__":
    main()
