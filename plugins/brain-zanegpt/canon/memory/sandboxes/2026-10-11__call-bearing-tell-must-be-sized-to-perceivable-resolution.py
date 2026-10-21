"""Sandbox (composed): seven E23's learnable tell (two night calls from a
consistent bearing = probably a real missing member) meets mirage E19 (size a
tell against the resolution of what SHOWS it, not the internal quantity) and
missing-laughter E1 (silence is only evidence against an established baseline).

Part 1: the bearing is computed on 24 sectors, but the player hears direction at
a coarser resolution R (8 compass points, or 4 quadrants). Consistency =
same or adjacent perceived point. Exact enumeration, no RNG:
real calls: true bearing then a second bearing offset by d sectors, d weighted by
a fixed discrete kernel; false calls: two independent uniform bearings.
Part 2: silence as evidence of abandonment. After the camp moves, a missing
member in-window calls with c per night; outside the window never. Posterior
P(out of window | k silent nights) from a 0.5 prior, for c=0.9 and c=0.3.
"""
from fractions import Fraction as Fr

S = 24
# offset kernel for the second real call (sectors): mostly near, some spread
KERNEL = {0: Fr(4, 16), 1: Fr(3, 16), -1: Fr(3, 16), 2: Fr(2, 16), -2: Fr(2, 16),
          3: Fr(1, 16), -3: Fr(1, 16)}


def perceive(sector, r):
    return (sector * r) // S


def consistent(p1, p2, r):
    d = abs(p1 - p2) % r
    return min(d, r - d) <= (0 if r <= 4 else 1)


def rates(r):
    real = Fr(0)
    for b in range(S):
        for off, w in KERNEL.items():
            real += Fr(1, S) * w * consistent(perceive(b, r), perceive((b + off) % S, r), r)
    false = Fr(0)
    for a in range(S):
        for b in range(S):
            false += Fr(1, S * S) * consistent(perceive(a, r), perceive(b, r), r)
    return real, false


def silence_posterior(c, k):
    p_in = Fr(1, 2) * (1 - c) ** k
    p_out = Fr(1, 2)
    return p_out / (p_in + p_out)


def main():
    res = {}
    for r in (24, 8, 4):
        real, false = rates(r)
        res[r] = (real, false, real / false)
        print(f"resolution {r:2d}: consistent real {float(real):.3f} false {float(false):.3f} "
              f"likelihood ratio {float(real / false):.2f}")
    sil = {}
    for c in (Fr(9, 10), Fr(3, 10)):
        sil[c] = [silence_posterior(c, k) for k in (1, 2, 3)]
        print(f"call rate {float(c):.1f}: P(abandoned | 1,2,3 silent nights) = "
              + ", ".join(f"{float(x):.3f}" for x in sil[c]))
    checks = [
        ("LR falls when the 24-sector bearing is heard at 8 points",
         res[8][2] < res[24][2]),
        (f"at 8 points false pairs look consistent >= 0.35 (got {float(res[8][1]):.3f})",
         res[8][1] >= Fr(35, 100)),
        (f"at 4 quadrants the tell is near-useless, LR < 1.5 (got {float(res[4][2]):.2f})",
         res[4][2] < Fr(3, 2)),
        (f"strong call (0.9): one silent night >= 0.85 sure (got {float(sil[Fr(9,10)][0]):.3f})",
         sil[Fr(9, 10)][0] >= Fr(85, 100)),
        (f"weak/floored call (0.3): three silent nights still < 0.80 (got {float(sil[Fr(3,10)][2]):.3f})",
         sil[Fr(3, 10)][2] < Fr(8, 10)),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"LR 24={float(res[24][2]):.2f} 8={float(res[8][2]):.2f} 4={float(res[4][2]):.2f}; "
          f"silence c0.9 k1={float(sil[Fr(9,10)][0]):.3f}, c0.3 k3={float(sil[Fr(3,10)][2]):.3f}")


if __name__ == "__main__":
    main()
