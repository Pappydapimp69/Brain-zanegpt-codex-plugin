"""Sandbox: is it worth going out after a night call, given false calls exist
(seven E23) and the owner's decision that the real call fades to silence
(0.9 x 0.6 per night missing, no floor; seven E27)?
Exact arithmetic, no RNG. Value of answering = P(real | call) * FIND - RISK,
in member-equivalents, where RISK is the chance the night out costs someone.
Prior someone missing M=0.15, false-call rate F=0.106 (posterior 0.6 on night 0),
FIND = 0.9 (shallow, same-night skilled search, seven E22).
"""
M, F, FIND = 0.15, 0.106, 0.9


def post(n):
    c = 0.9 * 0.6 ** n
    return c * M / (c * M + F * (1 - M))


def main():
    rows = []
    for n in range(7):
        p = post(n)
        rows.append(p)
        print(f"night {n}: P(real | call) {p:.3f}  value at risk 0.15: {p * FIND - 0.15:+.3f}  "
              f"at risk 0.30: {p * FIND - 0.30:+.3f}")
    last_pos_15 = max(n for n in range(7) if rows[n] * FIND - 0.15 > 0)
    last_pos_30 = max((n for n in range(7) if rows[n] * FIND - 0.30 > 0), default=-1)
    checks = [
        (f"night 0 call is worth answering at risk 0.30 (value {rows[0]*FIND-0.30:+.3f})", rows[0] * FIND > 0.30),
        (f"at risk 0.15 answering stays worth it through night 2 (last positive {last_pos_15})", last_pos_15 >= 2),
        (f"at risk 0.15 answering stops paying by night 4 (last positive {last_pos_15})", last_pos_15 < 4),
        (f"posterior falls below 0.25 by night 4 (got {rows[4]:.3f})", rows[4] < 0.25),
    ]
    held = sum(ok for _, ok in checks)
    for n_, ok in checks:
        print(("held   " if ok else "MISSED ") + n_)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"posterior n0 {rows[0]:.3f} n2 {rows[2]:.3f} n4 {rows[4]:.3f}; last worth answering at risk 0.15: night {last_pos_15}, at 0.30: night {last_pos_30}")


if __name__ == "__main__":
    main()
