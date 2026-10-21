"""Sandbox: does Suno Trending rank track likes/comments rather than plays?

Data: rows read first-hand from suno.com/trending (Global) on 2026-09-30.
  WEEKLY: position, plays, likes, comments  (clip JSON)
  NOW:    position, plays, likes            (page buttons, K values rounded by the UI)
Deterministic, stdlib only.

PREDICTION (written before the first run):
  S1 weekly: |rho(pos, plays)| < 0.30, rho(pos, likes) <= -0.50, rho(pos, comments) <= -0.40
  S2 now:    |rho(pos, plays)| < 0.35, rho(pos, likes) <= -0.60
  S3 split:  rho(log plays, like rate) <= -0.50 on weekly rows
  S4 break:  a plays-only ranker loses to a likes-only ranker on BOTH boards
             (Kendall tau vs the observed order), built to break the claim if plays win anywhere.
"""
import math

WEEKLY = [  # (pos, plays, likes, comments)
    (1, 18840, 635, 358), (2, 97101, 1617, 153), (3, 1461, 480, 121), (4, 2830, 561, 206),
    (5, 3926, 468, 237), (6, 2456, 657, 198), (7, 411, 356, 68), (8, 3783, 196, 78),
    (9, 4415, 260, 18), (10, 15009, 793, 274), (11, 1250, 318, 40), (12, 670, 281, 34),
    (13, 948, 134, 21), (14, 1853, 389, 160), (15, 930, 335, 123), (16, 4369, 201, 24),
    (17, 566, 181, 81), (18, 2483, 197, 25), (19, 745, 220, 68), (20, 376, 213, 35),
    (21, 26715, 555, 50), (22, 523, 176, 18),
]
NOW = [  # (pos, plays, likes)
    (1, 1200, 354), (2, 4500, 319), (3, 50, 56), (4, 1800, 217), (5, 407, 220), (6, 184, 35),
    (7, 1100, 297), (8, 285, 146), (9, 223, 121), (10, 481, 138), (11, 243, 104), (12, 1700, 120),
    (13, 175, 87), (14, 92, 44), (15, 262, 132), (16, 267, 114), (17, 216, 97), (18, 2500, 102),
    (19, 279, 102), (20, 430, 130), (21, 193, 102), (22, 158, 65), (23, 216, 81), (24, 200, 84),
    (25, 966, 239), (26, 195, 114), (27, 286, 91), (28, 124, 74),
]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = math.sqrt(sum((x - ma) ** 2 for x in a))
    vb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return cov / (va * vb)


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def kendall(a, b):
    n, s = len(a), 0
    for i in range(n):
        for j in range(i + 1, n):
            s += (1 if (a[i] - a[j]) * (b[i] - b[j]) > 0 else -1 if (a[i] - a[j]) * (b[i] - b[j]) < 0 else 0)
    return s / (n * (n - 1) / 2)


def col(rows, k):
    return [r[k] for r in rows]


results = []

# S1 weekly
pos, pl, lk, cm = (col(WEEKLY, k) for k in range(4))
s1 = dict(plays=spearman(pos, pl), likes=spearman(pos, lk), comments=spearman(pos, cm),
          likes_plus_comments=spearman(pos, [a + b for a, b in zip(lk, cm)]))
ok1 = abs(s1["plays"]) < 0.30 and s1["likes"] <= -0.50 and s1["comments"] <= -0.40
results.append(("S1 weekly", ok1, s1))

# S2 now
npos, npl, nlk = (col(NOW, k) for k in range(3))
s2 = dict(plays=spearman(npos, npl), likes=spearman(npos, nlk))
ok2 = abs(s2["plays"]) < 0.35 and s2["likes"] <= -0.60
results.append(("S2 now", ok2, s2))

# S3 broadcast vs community split
rate = [l / p for p, l in zip(pl, lk)]
s3 = dict(logplays_vs_rate=spearman([math.log(p) for p in pl], rate))
ok3 = s3["logplays_vs_rate"] <= -0.50
results.append(("S3 split", ok3, s3))

# S4 break attempt: which single signal best reproduces the observed order?
def tau_for(signal, positions):
    return kendall([-x for x in signal], positions)  # higher signal should mean smaller position
s4 = dict(weekly_plays=tau_for(pl, pos), weekly_likes=tau_for(lk, pos), weekly_comments=tau_for(cm, pos),
          now_plays=tau_for(npl, npos), now_likes=tau_for(nlk, npos))
ok4 = s4["weekly_likes"] > s4["weekly_plays"] and s4["now_likes"] > s4["now_plays"]
results.append(("S4 break: plays vs likes ranker", ok4, s4))

for name, ok, vals in results:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  " + ", ".join(f"{k}={v:+.3f}" for k, v in vals.items()))

passed = sum(ok for _, ok, _ in results)
summary = (f"{passed}/4 scenarios; weekly rho plays {s1['plays']:+.2f} likes {s1['likes']:+.2f} "
           f"comments {s1['comments']:+.2f}; now rho plays {s2['plays']:+.2f} likes {s2['likes']:+.2f}; "
           f"split {s3['logplays_vs_rate']:+.2f}; tau likes/plays weekly {s4['weekly_likes']:+.2f}/{s4['weekly_plays']:+.2f} "
           f"now {s4['now_likes']:+.2f}/{s4['now_plays']:+.2f}")
print(("RESULT: PASS " if passed == 4 else "RESULT: FAIL ") + summary)
