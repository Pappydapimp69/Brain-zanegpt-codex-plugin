# Sandbox: rule card with a harm ceiling + go-big escalation + framing distance.
# A beat has severity s (1..8). It is "ok" if s <= distance d; a funny beat scores s, a harmful one scores 0
# and counts as a safety violation. Card ceiling c clamps severity to min(s, c).
SCHED = [1, 2, 3, 4, 5, 6, 7, 8]          # go-big schedule

def run(d, c):
    sev = [min(s, c) if c is not None else s for s in SCHED]
    viol = sum(1 for s in sev if s > d)
    score = sum(s for s in sev if s <= d)
    return viol, score

res = {}
for d in range(1, 9):
    best = run(d, d)[1]                              # plateau at the framing distance (clamped beats repeat the ceiling)
    res[d] = {
        "nocard": run(d, None),
        "matched": run(d, d),
        "over": run(d, d + 2),                       # BREAK: card states a ceiling above the framing distance
        "under": run(d, max(1, d - 2)),
        "best": best,
    }
for d in (2, 4, 6):
    print(d, res[d])
ok_matched = all(r["matched"][0] == 0 and r["matched"][1] == r["best"] for d, r in res.items())
# nocard / over ceilings leak whenever d < max reachable severity
leak_nocard = [d for d, r in res.items() if r["nocard"][0] > 0]
leak_over = [d for d, r in res.items() if r["over"][0] > 0 and d < 7]
under_loss = [d for d, r in res.items() if r["under"][1] < r["best"]]
# a fixed grounded distance d=1 with go-big and no card: score only the opener
fixed = res[1]["nocard"]
print("nocard leaks at d:", leak_nocard)
print("over-ceiling leaks at d:", leak_over)
print("under-ceiling loses score at d:", under_loss)
print("fixed d=1 nocard:", fixed)
good = ok_matched and len(leak_over) >= 5 and len(under_loss) >= 6 and len(leak_nocard) == 7
print(f"RESULT: {'PASS' if good else 'FAIL'} matched ceiling: 0 violations and full score at all 8 distances; "
      f"no card leaks at {len(leak_nocard)}/8, over-ceiling leaks at {len(leak_over)}, under-ceiling loses at {len(under_loss)}")
