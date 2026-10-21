"""Loop 4 sandbox: a sanity meter that PUNISHES (low sanity makes the player
worse at the game) versus one that only changes PERCEPTION. Exact Markov chain,
no RNG. Sanity 0..5, start 5. Each encounter: fail with probability f(s); a fail
drops sanity by 1, a success recovers +1 with probability 0.3 (capped at 5).
Sanity 0 = collapse (absorbing). 12 encounters.
  PERCEPTION  f(s) = 0.30 at every level (low sanity only changes what is shown)
  PUNISH      f(s) = 0.30 + 0.10 * (5 - s)  (low sanity also hurts aim/controls)
"""


def collapse(fail, enc=12, rec=0.3):
    dist = {s: 0.0 for s in range(6)}
    dist[5] = 1.0
    for _ in range(enc):
        nd = {s: 0.0 for s in range(6)}
        nd[0] += dist[0]
        for s in range(1, 6):
            f = fail(s)
            nd[s - 1] += dist[s] * f
            up = min(s + 1, 5)
            nd[up] += dist[s] * (1 - f) * rec
            nd[s] += dist[s] * (1 - f) * (1 - rec)
        dist = nd
    return dist[0], sum(s * p for s, p in dist.items())


def main():
    res = {}
    for name, fn in (("perception", lambda s: 0.30), ("punish", lambda s: 0.30 + 0.10 * (5 - s))):
        res[name] = collapse(fn)
        print(f"{name:10s}: collapse within 12 encounters {res[name][0]:.3f}, mean sanity at end {res[name][1]:.2f}")
    soft = collapse(lambda s: 0.30 + 0.03 * (5 - s))
    print(f"mild punish (0.03 per level): collapse {soft[0]:.3f}")
    ratio = res["punish"][0] / res["perception"][0]
    checks = [
        (f"a punishing meter collapses >= 2x as often (x{ratio:.2f})", ratio >= 2),
        ("the perception-only meter still lets some players collapse (> 0)", res["perception"][0] > 0),
        ("break case: a mild punishment (0.03 per level) stays within 1.3x of perception-only",
         soft[0] / res["perception"][0] <= 1.3),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; collapse perception "
          f"{res['perception'][0]:.3f} punish {res['punish'][0]:.3f} (x{ratio:.2f}); mild {soft[0]:.3f}")


if __name__ == "__main__":
    main()
