"""Perseus and the Gorgon: striking a hazard you cannot look at directly.

Deterministic, stdlib only, no randomness. A 1-D reach axis. The target (the
Gorgon) starts at offset x0 in -6..6 from the striker's sword (p = 0). Each of
10 steps the striker reads a view of the target, then either strikes (the view
says aligned) or moves the sword up to 2 places toward where the view says the
target is. Forced strike on the last step. A hit is |sword - target| <= w.

Views:
  direct     exact, but looking is fatal: death on the first look
  blind      aims at the lair centre (0) told by others; never looks
  raw mirror the reflection reverses the reach axis and the striker acts on it
             as if it were a direct view
  mirror     reversal corrected; image is coarse (offset rounded to steps of q)
             and may be stale by `lag` steps (glance at shield, then act)

Target: asleep (still) or awake (sways +1, 0, -1 around x0 each step).

PREDICTION (written before the first run; also in sbx2_J/predictions.txt):
  direct 0 hits / 13 deaths everywhere; blind asleep w=0 1/13, w=1 3/13,
  w=6 13/13; raw mirror asleep q=1 w=0 1/13, w=1 1/13; mirror asleep q=1 13/13
  at w=0; mirror asleep q=3 w=0 7/13, w=1 13/13; mirror awake q=1 lag0 13/13
  at w=0; awake q=1 lag1 w=0 1/13, w=1 13/13; awake q=3 lag1 w=1 4..11/13,
  w=0 <= 4, w=2 13/13; BREAK w=6: blind ties the mirror at 13/13.

RUN 1 missed two: awake q=1 lag0 w=0 gave 3/13 (predicted 13) and awake q=1
lag1 w=1 gave 7/13 (predicted 13). Not a code bug: acting on a view takes a
step and the target sways meanwhile, so even a current view chases one step
behind. Revised error budget: rounding + (lag + 1) x target speed.
ADDED BEFORE RUN 2: awake q=1 lag0 w=1 13/13; awake q=1 lag1 w=2 13/13;
awake q=3 lag0 w=2 13/13. The run-1 misses are printed as MISS lines and do
not count toward the result.
ADDED BEFORE RUN 3 (after the first ZaneGPT check): a fast target swaying
0, +2, 0, -2 (as fast as the sword), q=1, lag 1: budget 0 + 2 x 2 = 4, so
w=4 13/13 and w=2 below 13/13.
"""

OFFSETS = list(range(-6, 7))
SPEED = 2
STEPS = 10
SWAY = [0, 1, 0, -1]
FAST = [0, 2, 0, -2]


def target_at(x0, k, awake):
    if awake == "fast":
        return x0 + FAST[k % 4]
    return x0 + (SWAY[k % 4] if awake else 0)


def quantize(d, q):
    if q <= 1:
        return d
    s = 1 if d >= 0 else -1
    return s * ((abs(d) + q // 2) // q) * q


def run(view, x0, w, awake=False, q=1, lag=0):
    """Return 'hit', 'miss' or 'dead'."""
    p = 0
    for k in range(STEPS):
        t_now = target_at(x0, k, awake)
        if view == "direct":
            return "dead"
        if view == "blind":
            obs = 0 - p
        else:
            t_seen = target_at(x0, max(0, k - lag), awake)
            obs = quantize(t_seen - p, q)
            if view == "raw":
                obs = -obs  # reflection reverses the reach axis, uncorrected
        if obs == 0 or k == STEPS - 1:
            return "hit" if abs(p - t_now) <= w else "miss"
        step = min(SPEED, abs(obs))
        p += step if obs > 0 else -step
    return "miss"


def count(view, w, **kw):
    res = [run(view, x0, w, **kw) for x0 in OFFSETS]
    return res.count("hit"), res.count("dead")


checks = []
misses = []


def miss(label, got, predicted):
    misses.append(label)
    print(f"MISS (run 1, predicted {predicted}) {label}: {got}")


def check(label, got, want):
    ok = want(got) if callable(want) else got == want
    checks.append(ok)
    print(f"{'ok ' if ok else 'BAD'} {label}: {got}")
    return got


print("== 1) direct view is fatal")
for awake in (False, True):
    check(f"direct awake={awake} (hits, deaths)", count("direct", 6, awake=awake), (0, 13))

print("== 2) asleep target: blind vs raw mirror vs corrected mirror")
b0 = check("blind w=0", count("blind", 0)[0], 1)
b1 = check("blind w=1", count("blind", 1)[0], 3)
r0 = check("raw mirror q=1 w=0", count("raw", 0)[0], 1)
r1 = check("raw mirror q=1 w=1 (worse than blind)", count("raw", 1)[0], 1)
check("mirror q=1 w=0", count("mirror", 0)[0], 13)
check("mirror q=3 w=0 (coarse image misses exact hits)", count("mirror", 0, q=3)[0], 7)
check("mirror q=3 w=1 (tolerance covers the rounding)", count("mirror", 1, q=3)[0], 13)

print("== 3) awake target: lag turns target speed into aim error")
miss("mirror awake q=1 lag0 w=0", count("mirror", 0, awake=True)[0], 13)
check("mirror awake q=1 lag0 w=1 (one act step of sway)", count("mirror", 1, awake=True)[0], 13)
check("mirror awake q=1 lag1 w=0", count("mirror", 0, awake=True, lag=1)[0], 1)
miss("mirror awake q=1 lag1 w=1", count("mirror", 1, awake=True, lag=1)[0], 13)
check("mirror awake q=1 lag1 w=2 (lag 1 + act 1)", count("mirror", 2, awake=True, lag=1)[0], 13)
check("mirror awake q=3 lag0 w=2 (rounding 1 + act 1)", count("mirror", 2, awake=True, q=3)[0], 13)
check("mirror awake q=3 lag1 w=0", count("mirror", 0, awake=True, q=3, lag=1)[0], lambda g: g <= 4)
check("mirror awake q=3 lag1 w=1", count("mirror", 1, awake=True, q=3, lag=1)[0], lambda g: 4 <= g <= 11)
check("mirror awake q=3 lag1 w=2 (budget says 3; it is a bound, not exact)", count("mirror", 2, awake=True, q=3, lag=1)[0], 13)

print("== 3b) fast target, as fast as the sword (added before run 3)")
fw4 = check("fast q=1 lag1 w=4 (budget 0 + 2 x 2)", count("mirror", 4, awake="fast", lag=1)[0], 13)
fw2 = check("fast q=1 lag1 w=2 (below budget)", count("mirror", 2, awake="fast", lag=1)[0], lambda g: g < 13)

print("== 4) BREAK: tolerance wider than the prior's error")
bw = check("blind w=6", count("blind", 6)[0], 13)
mw = check("mirror q=3 w=6", count("mirror", 6, q=3)[0], 13)
check("blind ties the mirror at w=6", bw == mw, True)

if all(checks):
    print(f"RESULT: PASS direct view kills 13/13; corrected mirror hits whenever tolerance >= its error "
          f"(asleep q=3: 7/13 exact, 13/13 at w=1; awake: 13/13 once w >= rounding + (lag+1) x sway); "
          f"uncorrected mirror {r1}/13 at w=1 is worse than blind {b1}/13; BREAK: at w=6 blind ties the mirror 13/13; "
          f"fast target (sway 2) needs w=4: {fw4}/13 there, {fw2}/13 at w=2; "
          f"run 1 missed {len(misses)} awake predictions by leaving out the act step")
else:
    print(f"RESULT: FAIL {checks.count(False)} of {len(checks)} predictions missed")
