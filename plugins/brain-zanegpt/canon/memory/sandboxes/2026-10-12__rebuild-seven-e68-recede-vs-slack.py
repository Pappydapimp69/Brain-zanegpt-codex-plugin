"""Blind rebuild of seven E68 (own fixture). Claim: a sub-threshold on-screen
recede is harmless only without a deadline; near a deadline an invisible recede
can stop a disciplined player, so size it against slack.
Exact, no RNG. A disciplined walk takes base time T; the deadline (night) leaves
slack s, so the player arrives in time iff T/(1-f) <= T(1+s), i.e. f <= s/(1+s).
Trips have slack spread evenly over 0..0.5 (101 points). Recede f below a
speed-discrimination threshold j (stand-ins 0.05, 0.08, 0.12) is invisible.
PREDICTION (written before running): at j = 0.08 an invisible recede flips at
least 10% of trips from 'arrives' to 'benighted'; with slack >= 0.2 it flips
none; the flipped share grows with j.
"""


def flipped(f, slacks):
    return sum(1 for s in slacks if f > s / (1 + s)) / len(slacks)


def main():
    slacks = [i * 0.005 for i in range(101)]
    rows = {j: flipped(j, slacks) for j in (0.05, 0.08, 0.12)}
    wide = flipped(0.08, [s for s in slacks if s >= 0.2])
    for j, v in rows.items():
        print(f"invisible recede f = {j:.2f}: share of trips flipped to benighted {v:.3f}")
    print(f"trips with slack >= 0.20 flipped at f = 0.08: {wide:.3f}")
    checks = [
        ("at j = 0.08 at least 10% of trips flip", rows[0.08] >= 0.10),
        ("no trip with slack >= 0.2 flips", wide == 0.0),
        ("flipped share grows with the threshold", rows[0.05] < rows[0.08] < rows[0.12]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; flipped "
          + "/".join(f"{v:.3f}" for v in rows.values()) + f" at j 0.05/0.08/0.12; slack>=0.2: {wide:.3f}")


if __name__ == "__main__":
    main()
