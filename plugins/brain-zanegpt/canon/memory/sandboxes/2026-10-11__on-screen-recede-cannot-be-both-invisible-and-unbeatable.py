"""Sandbox (train gap, tension T1): a phantom relief (pylon) that recedes.
Poles: OFF-SCREEN ONLY (moves only while the player looks away) vs SLOW
ON-SCREEN RECEDE (creeps away at a fraction f of the player's closing speed,
claimed 'cannot be beaten by discipline').
Exact arithmetic, no RNG. Player speed v = 1, start gap D = 100.
- On-screen recede at fraction f: gap closes at (1 - f) v, so arrival takes
  D / ((1 - f) v). The expansion of the target's image is slower than the
  player's own motion predicts by the ratio f; the recede is NOTICEABLE when f
  exceeds a speed-discrimination threshold j (ASSUMED 0.10, a Weber-fraction
  stand-in; the sandbox sweeps 0.05..0.20).
- Off-screen only: the relief recedes at speed r = 1.5 v while not looked at.
  A player who looks away a share a of the time closes at (1-a) v - a r.
"""
D, V = 100.0, 1.0


def onscreen_time(f):
    return D / ((1 - f) * V)


def offscreen_rate(a, r=1.5):
    return (1 - a) * V - a * r


def main():
    base = D / V
    print(f"no recede: arrive in {base:.1f}")
    rows = {}
    for j in (0.05, 0.10, 0.20):
        t = onscreen_time(j)
        rows[j] = t / base
        print(f"threshold {j:.2f}: the strongest INVISIBLE recede (f = {j:.2f}) delays a disciplined player x{t / base:.3f}")
    f_triple = 1 - 1 / 3
    print(f"to triple the walk an on-screen recede needs f = {f_triple:.3f}, {f_triple / 0.10:.1f}x the 0.10 threshold")
    for a in (0.0, 0.2, 0.4, 0.5):
        rate = offscreen_rate(a)
        status = f"arrives in {D / rate:.1f}" if rate > 0 else "never arrives"
        print(f"off-screen only, looks away {a:.0%} of the time: closing rate {rate:+.2f} -> {status}")
    checks = [
        ("at every assumed threshold an invisible recede adds at most 25% to the walk", all(x <= 1.25 for x in rows.values())),
        ("a recede strong enough to triple the walk is >= 5x over the 0.10 threshold", f_triple / 0.10 >= 5),
        ("off-screen only: a disciplined player (never looks away) arrives in the base time", offscreen_rate(0.0) == V),
        ("break case: off-screen only stops a player who looks away 40% or more", offscreen_rate(0.4) <= 0),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; invisible recede delay "
          + "/".join(f"x{rows[j]:.3f}" for j in rows) + f"; tripling needs f={f_triple:.3f}; off-screen stops at look-away >= 0.4")


if __name__ == "__main__":
    main()
