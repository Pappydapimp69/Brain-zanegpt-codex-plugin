"""Sandbox T1: does a remaster/reissue underperform its original, and how big is take-to-take variance?

Data: the owner's public Suno catalog read 2026-10-02 (title, plays, created date). Rates are plays per
day of age at 2026-10-02 so old and new clips compare fairly. Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 later re-issues (remaster / remix / re-gen of an earlier title) earn fewer plays per day than the
     original in >= 2 of 3 dated pairs
  P2 same-day duplicate takes of one song differ by >= 2x in plays in >= 2 of 3 pairs
  P3 break: across all 3 dated pairs, the later version's plays/day is never above the original's
"""
from datetime import date

TODAY = date(2026, 10, 2)
DATED = [  # (song, original (plays, date), later version (plays, date))
    ("Elevator music", (117, date(2025, 4, 28)), (8, date(2026, 8, 4))),
    ("Shadow waltz", (23, date(2025, 11, 2)), (40, date(2026, 7, 23))),
    ("Yeah ...", (40, date(2025, 7, 2)), (40, date(2025, 7, 8))),
]
SAME_DAY = [("void.loop.6", 85, 16), ("Echoes", 86, 56), ("White lies in velvet", 56, 20)]


def per_day(p, d):
    return p / max(1, (TODAY - d).days)


lower = 0
rows = []
for name, (op, od), (lp, ld) in DATED:
    o, l = per_day(op, od), per_day(lp, ld)
    lower += l < o
    rows.append(f"{name}: original {o:.3f}/day, later {l:.3f}/day ({'lower' if l < o else 'higher' if l > o else 'equal'})")
ratios = [max(a, b) / min(a, b) for _, a, b in SAME_DAY]
big = sum(r >= 2 for r in ratios)
never_higher = all(per_day(lp, ld) <= per_day(op, od) for _, (op, od), (lp, ld) in DATED)
for r in rows:
    print(r)
print("same-day take ratios:", ", ".join(f"{n} {r:.1f}x" for (n, _, _), r in zip(SAME_DAY, ratios)))
res = [("P1 later lower in >=2/3", lower >= 2, f"{lower}/3"), ("P2 takes differ >=2x in >=2/3", big >= 2, f"{big}/3"),
       ("P3 break: later never higher", never_higher, str(never_higher))]
for n, ok, d in res:
    print(f"{n}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 3 else "RESULT: FAIL ") + f"{k}/3; later-lower {lower}/3; take ratios " +
      ", ".join(f"{r:.1f}x" for r in ratios) + f"; median take ratio {sorted(ratios)[1]:.1f}x")
