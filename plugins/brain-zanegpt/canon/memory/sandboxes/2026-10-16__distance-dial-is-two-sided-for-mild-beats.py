# Sandbox: kernel says severe harm needs distance AND mild harm needs closeness.
# The earlier rule-card sandbox only modelled "severity <= distance". Here a beat is
# funny iff the gag passes the rule card AND the framing distance sits in a band
# around what the severity needs: need(sev)=sev, funny iff need-1 <= distance <= need+1
# (too close for severe = distressing; too distant for mild = no stakes, no laugh).
import random

def gags(seed, n=360):
    r = random.Random(seed)
    return [{"harm": r.choice(["humiliate", "injure"]), "victim_wins": r.random() < 0.3}
            for _ in range(n)]

def card_ok(g):
    return g["harm"] == "humiliate" and not g["victim_wins"]

def run(sched, dist, seed=11):
    pool = gags(seed); funny = shown = 0
    for i, sev in enumerate(sched):
        d = dist(i)
        for g in pool[i * 60:(i + 1) * 60]:
            if not card_ok(g):
                continue
            shown += 1
            if sev - 1 <= d <= sev + 1:
                funny += 1
    return funny, shown

go_big = [1, 2, 3, 4, 5, 5]
mild = [1, 1, 1, 2, 2, 2]
matched = lambda i: [1, 2, 3, 4, 5, 5][i]
grounded = lambda i: 2
max_dist = lambda i: 5          # "just frame everything as surreal": the one-sided shortcut
R = {
 "bigsched_matched": run(go_big, matched),
 "bigsched_grounded": run(go_big, grounded),
 "bigsched_maxdist": run(go_big, max_dist),
 "mildsched_maxdist": run(mild, max_dist),   # breaker: shortcut applied to mild beats
 "mildsched_grounded": run(mild, grounded),
}
for k, (f, s) in R.items():
    print("%-20s funny=%3d of shown=%3d" % (k, f, s))
# Prediction (before run): matched dial wins everywhere; max distance helps the severe
# beats but kills mild ones: mildsched_maxdist funny == 0 while mildsched_grounded >= 80%
# of shown; bigsched_maxdist < bigsched_matched.
ok = (R["mildsched_maxdist"][0] == 0
      and R["mildsched_grounded"][0] >= 0.8 * R["mildsched_grounded"][1]
      and R["bigsched_maxdist"][0] < R["bigsched_matched"][0]
      and R["bigsched_matched"][0] > R["bigsched_grounded"][0])
print("RESULT: %s matched=%d grounded=%d maxdist=%d mild-maxdist=%d mild-grounded=%d/%d"
      % ("PASS" if ok else "FAIL", R["bigsched_matched"][0], R["bigsched_grounded"][0],
         R["bigsched_maxdist"][0], R["mildsched_maxdist"][0], *R["mildsched_grounded"]))
