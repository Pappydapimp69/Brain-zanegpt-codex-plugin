"""Blind rebuild of seven E69 (own fixture). Claim: a hallucinated-voice budget
is a readout of masking width and talk share, not a constant.
Different model: masking falls off SMOOTHLY with angle instead of an on/off
cone. A masker at angular distance a talks with probability d and, when
talking, blocks the target with probability exp(-a/sigma). Voices spread evenly
around 360 degrees. A word lands with prob prod over maskers of (1 - d*exp(-a/sigma)).
Budget = most voices (1..16) with landing >= 0.5. Exact, no RNG.
PREDICTION (written before running): across sigma 15..90 degrees the spread
budget changes by at least a factor 3; at fixed sigma 45 it changes with talk
share d 0.2..0.6 by at least a factor 2; one place (all a = 0) gives the same
budget at every sigma.
"""
import math


def landing(n, d, sigma, spread=True):
    p = 1.0
    for k in range(1, n):
        a = min(k * 360 / n, 360 - k * 360 / n) if spread else 0.0
        p *= 1 - d * math.exp(-a / sigma)
    return p


def budget(d, sigma, spread=True):
    ok = [n for n in range(1, 17) if landing(n, d, sigma, spread) >= 0.5]
    return max(ok)


def main():
    by_sigma = {s: budget(0.4, s) for s in (15, 30, 45, 60, 90)}
    by_d = {d: budget(d, 45) for d in (0.2, 0.4, 0.6)}
    one_place = {s: budget(0.4, s, False) for s in (15, 45, 90)}
    print("spread budget by sigma (d 0.4): " + ", ".join(f"{s}: {b}" for s, b in by_sigma.items()))
    print("spread budget by talk share (sigma 45): " + ", ".join(f"{d}: {b}" for d, b in by_d.items()))
    print("one-place budget by sigma: " + ", ".join(f"{s}: {b}" for s, b in one_place.items()))
    checks = [
        ("budget varies >= x3 across sigma", max(by_sigma.values()) >= 3 * min(by_sigma.values())),
        ("budget varies >= x2 across talk share", max(by_d.values()) >= 2 * min(by_d.values())),
        ("one place is the same at every sigma", len(set(one_place.values())) == 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; sigma budgets "
          + "/".join(str(b) for b in by_sigma.values()) + "; talk-share budgets " + "/".join(str(b) for b in by_d.values())
          + f"; one place {list(one_place.values())[0]}")


if __name__ == "__main__":
    main()
