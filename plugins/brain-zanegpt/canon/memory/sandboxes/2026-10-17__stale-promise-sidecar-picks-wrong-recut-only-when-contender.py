"""Sandbox: six cold-open recuts, each with a true promise level p (read from the real cut) and a hand-kept
sidecar copy of p (collective-reference E1: a hand-synced sidecar drifts silently; derive it instead).
Ranking is IPM x D1 with D1 penalising promise above delivery 0.5 (cold-open-promise-matches-delivery,
rank-ipm-times-d1-needs-fidelity-retention-link). A recut changes the true p by -0.3 or +0.3; a stale
sidecar still holds the old p.
Prediction (written before first run): deriving p from the cut gives 0 wrong picks over all 2^6 stale
subsets x 2^6 recut directions (4096 cases); a hand sidecar gives wrong picks in some but far fewer than half
of the cases (<25 percent) because staleness only matters when a stale entry is or becomes the argmax.
Assumption: promise is the only drifting field. BREAK: all six stale with all recuts upward, where I expect
the sidecar to keep the old winner."""
import itertools
BASE = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
DELIVERY = 0.5
def score(p):
    p = max(0.0, min(1.0, p))
    return 10 * (0.5 + p) * 0.40 * (1 - 1.5 * max(0.0, p - DELIVERY))
def pick(ps): return max(range(6), key=lambda i: (round(score(ps[i]), 12), -i))
wrong_sidecar = wrong_derived = total = 0
for stale in itertools.product((0, 1), repeat=6):
    for dirs in itertools.product((-0.3, 0.3), repeat=6):
        true = [b + d for b, d in zip(BASE, dirs)]
        side = [b if s else t for b, t, s in zip(BASE, true, stale)]
        best = pick(true)
        total += 1
        wrong_derived += pick(true) != best
        wrong_sidecar += score(true[pick(side)]) < score(true[best]) - 1e-12
print("cases:", total, "wrong with derived promise:", wrong_derived, "wrong with hand sidecar:", wrong_sidecar,
      f"({100*wrong_sidecar/total:.1f} percent)")
one_stale = n1 = 0
for j in range(6):
    stale = [0]*6; stale[j] = 1
    for dirs in itertools.product((-0.3, 0.3), repeat=6):
        true = [b + d for b, d in zip(BASE, dirs)]
        side = [BASE[i] if stale[i] else true[i] for i in range(6)]
        n1 += 1; one_stale += score(true[pick(side)]) < score(true[pick(true)]) - 1e-12
print(f"exactly one stale entry: wrong in {one_stale} of {n1} ({100*one_stale/n1:.1f} percent)")
up = [b + 0.3 for b in BASE]
print("BREAK all six stale, all recuts up: sidecar picks", pick(BASE), "true pick", pick(up),
      "regret", round(score(up[pick(up)]) - score(up[pick(BASE)]), 3))
ok = wrong_derived == 0 and 0 < wrong_sidecar < total * 0.25
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" derived 0/{total} wrong, hand sidecar {wrong_sidecar}/{total} wrong ({100*wrong_sidecar/total:.1f} percent), one stale entry {one_stale}/{n1}")
