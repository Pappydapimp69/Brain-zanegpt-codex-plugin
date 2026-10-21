"""Sandbox: with the owner's decision that a missing member's call fades to
silence (lost after night 6, seven E27 decision), and the sleep/camp rescue
window (seven E30: lost when the lead sleeps two areas ahead), which limit
abandons first? And does allowing sleeping out keep abandonment deliberate?
Exact enumeration, no RNG, over all 8-day plans (4^8 = 65536) of stay, scout1,
scout2, move (camp +1). Variant adds sleepout2 (sleep two areas ahead without a
camp, a dusk choice) -> 5^8 plans. Unfound member assumed throughout.
"""
from itertools import product

TIME_LIMIT = 6  # lost at the start of day 6 if still missing


def outcome(plan):
    camp = 0
    for day, a in enumerate(plan):
        if day >= TIME_LIMIT:
            return "time", a
        if a == "move":
            camp += 1
        sleep = camp + 2 if a == "sleepout2" else camp
        if sleep >= 2:
            return "space", a
    return "time", None


def tally(acts):
    n = space = time = acc = 0
    for plan in product(acts, repeat=8):
        n += 1
        kind, a = outcome(plan)
        if kind == "space":
            space += 1
            acc += a not in ("move", "sleepout2")
        else:
            time += 1
    return n, space, time, acc


def main():
    base = tally(("stay", "scout1", "scout2", "move"))
    out = tally(("stay", "scout1", "scout2", "move", "sleepout2"))
    for name, (n, s, t, a) in (("base", base), ("sleepout", out)):
        print(f"{name:8s}: plans {n}  space-first {s/n:.3f}  time-first {t/n:.3f}  accidental {a}")
    checks = [
        (f"time limit abandons first in >= 0.40 of base plans (got {base[2]/base[0]:.3f})", base[2] / base[0] >= 0.40),
        ("no accidental abandonment in base plans", base[3] == 0),
        ("break case: allowing sleeping out keeps accidental abandonment at 0", out[3] == 0),
        (f"sleeping out makes space-first the majority (got {out[1]/out[0]:.3f})", out[1] / out[0] > 0.5),
    ]
    held = sum(ok for _, ok in checks)
    for n_, ok in checks:
        print(("held   " if ok else "MISSED ") + n_)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"base time-first {base[2]/base[0]:.3f}; sleepout space-first {out[1]/out[0]:.3f}; accidental {base[3]}/{out[3]}")


if __name__ == "__main__":
    main()
