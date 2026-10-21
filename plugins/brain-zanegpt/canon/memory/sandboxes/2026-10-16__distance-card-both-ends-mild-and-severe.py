# Sandbox: harm-distance rule: mild harm (s<=2) is benign only when CLOSE (d<=3); severe harm (s>=3) only when
# DISTANT enough (d>=s). Funny points = s for a benign violation (s>=2), 0 otherwise; harm beat = not benign.
def benign(s, d): return (d <= 3) if s <= 2 else (d >= s)
def score(beats):
    funny = sum(s for s, d in beats if s >= 2 and benign(s, d)); harm = sum(1 for s, d in beats if not benign(s, d))
    return funny, harm
sched = {"go-big": [2, 3, 4, 5, 5], "mild-open-severe-close": [2, 2, 5, 5, 2], "severe-first": [5, 4, 3, 2, 2]}
cards = {"const-d2": lambda s: 2, "const-d5": lambda s: 5, "matched-up": lambda s: max(2, s) if s >= 3 else 2}
res = {}
for sn, sev in sched.items():
    for cn, f in cards.items():
        res[sn, cn] = score([(s, f(s)) for s in sev]); print(f"{sn:22s} {cn:10s} funny/harm {res[sn, cn]}")
tot = {cn: (sum(res[s, cn][0] for s in sched), sum(res[s, cn][1] for s in sched)) for cn in cards}
print("totals funny/harm", tot)
ok = (tot["matched-up"][1] == 0 and tot["const-d2"][1] > 0 and tot["const-d5"][1] > 0
      and tot["matched-up"][0] > tot["const-d2"][0] and tot["matched-up"][0] > tot["const-d5"][0])
print("RESULT: %s matched-up card %s funny/harm vs const-d2 %s and const-d5 %s over 3 schedules; const-d5 harms mild beats (too distant), const-d2 harms severe beats" %
      ("PASS" if ok else "FAIL", tot["matched-up"], tot["const-d2"], tot["const-d5"]))
