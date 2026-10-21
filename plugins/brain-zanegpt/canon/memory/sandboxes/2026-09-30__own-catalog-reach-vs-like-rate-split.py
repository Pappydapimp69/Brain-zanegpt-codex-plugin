"""Sandbox: does the reach-vs-like-rate split (suno E3, corrected) hold inside ONE small creator's
catalog, an independent population from the Trending boards?

Data: the owner's 53 Suno songs (plays, likes, comments), public profile JSON, 2026-09-30.
Deterministic, stdlib only.

PREDICTION (written before the first run):
  S1 songs with >= 20 plays: Spearman rho(log plays, like rate) <= -0.30
  S2 all 53 songs: rho(log plays, like rate) <= -0.30
  S3 break: drop the one breakout song (19,675 plays); S1 must still hold, else the split is one
     outlier, not a pattern.
  S4 the breakout's like rate is below the catalog median like rate (songs >= 20 plays).
"""
import math

CAT = [[12,1,0],[19,1,0],[12,1,0],[15,1,0],[7,0,0],[40,1,1],[14,1,0],[10,1,0],[18,1,0],[23,0,0],[23,1,0],[7,1,0],
       [8,1,0],[16,1,0],[20,0,0],[26,1,0],[45,0,0],[20,2,0],[32,1,0],[40,2,0],[56,2,0],[20,1,0],[40,2,0],[29,1,0],
       [40,1,0],[23,1,0],[56,1,0],[20,0,0],[16,1,0],[56,2,0],[62,3,0],[29,2,0],[69,4,0],[19675,524,33],[85,2,0],
       [16,1,0],[50,2,0],[26,0,0],[69,1,0],[40,1,0],[78,2,0],[117,4,0],[221,1,0],[127,6,0],[56,1,0],[86,4,0],
       [288,5,0],[195,6,0],[32,0,0],[50,1,1],[50,0,0],[40,2,0],[56,1,0]]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def rho(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return cov / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


def split(rows):
    return rho([math.log(p) for p, l, c in rows], [l / p for p, l, c in rows])


ge20 = [r for r in CAT if r[0] >= 20]
s1 = split(ge20)
s2 = split(CAT)
no_hit = [r for r in ge20 if r[0] < 10000]
s3 = split(no_hit)
rates = sorted(l / p for p, l, c in ge20)
median = rates[len(rates) // 2]
hit_rate = 524 / 19675

res = [("S1 >=20 plays", s1 <= -0.30, f"rho {s1:+.3f} n {len(ge20)}"),
       ("S2 all songs", s2 <= -0.30, f"rho {s2:+.3f} n {len(CAT)}"),
       ("S3 break: without the breakout", s3 <= -0.30, f"rho {s3:+.3f} n {len(no_hit)}"),
       ("S4 breakout below median rate", hit_rate < median, f"hit {hit_rate:.3f} vs median {median:.3f}")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; rho >=20 {s1:+.2f}, all {s2:+.2f}, without breakout {s3:+.2f}; breakout rate {hit_rate:.3f} vs median {median:.3f}")
