"""Sandbox: does Suno's Trending 'Now' board rank on likes gained in the last hour?

Two first-hand reads of the Now board (Global) one hour apart on 2026-09-30, plus each song's clip
JSON at both times. Row per song present on the board at read 2:
  (pos_read2, likes_read1, likes_read2, plays_read1, plays_read2, comments_read1, comments_read2)
Songs new to the board at read 2 have read-1 counts fetched at read 1 when they were on it, else
from the clip JSON at read 1 time is unavailable -> such rows use None and are excluded where noted.
Deterministic, stdlib only.

PREDICTION (written before read 2 was taken):
  S1 rho(pos2, delta likes) <= -0.60
  S2 |rho(pos2, delta likes)| > |rho(pos2, total likes at read 2)|   (short-window beats totals)
  S3 break: rho(pos2, delta plays) is weaker than delta likes (plays-velocity is not the driver)
  S4 delta likes + delta comments does not do worse than delta likes alone
"""
import math

# Read 1 2026-09-30T08:05:55Z, read 2 2026-09-30T09:06:35Z; all 28 songs on both boards, 0 of 28
# positions changed (board order identical; also identical to the session's first read earlier that morning).
POSITIONS_CHANGED = 0
DATA = [(1,354,355,1233,1258,126,126),(2,321,325,4527,4621,136,136),(3,56,56,50,50,0,0),(4,222,224,1822,1855,51,52),
        (5,224,230,414,423,94,95),(6,37,38,184,184,6,6),(7,297,300,1110,1117,141,141),(8,147,150,285,285,73,74),
        (9,121,121,231,231,24,24),(10,140,144,497,511,12,12),(11,105,106,243,243,35,35),(12,121,124,1762,1796,16,16),
        (13,88,89,175,175,9,9),(14,44,47,92,92,10,10),(15,135,140,262,270,46,46),(16,115,118,274,281,18,18),
        (17,97,98,216,224,32,32),(18,103,106,2526,2526,46,47),(19,103,106,279,279,29,29),(20,134,139,437,437,53,53),
        (21,103,105,193,193,45,45),(22,70,71,173,180,20,20),(23,83,85,225,225,12,12),(24,85,87,200,200,24,24),
        (25,245,249,973,973,61,62),(26,116,118,195,195,56,57),(27,93,96,286,286,16,17),(28,75,77,133,151,17,19)]

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
    va = math.sqrt(sum((x - ma) ** 2 for x in ra))
    vb = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return cov / (va * vb) if va and vb else 0.0


rows = [r for r in DATA if r[1] is not None]
pos = [r[0] for r in rows]
dl = [r[2] - r[1] for r in rows]
tl = [r[2] for r in rows]
dp = [r[4] - r[3] for r in rows]
dlc = [(r[2] - r[1]) + (r[6] - r[5]) for r in rows]
r_dl, r_tl, r_dp, r_dlc = rho(pos, dl), rho(pos, tl), rho(pos, dp), rho(pos, dlc)
res = [("S1 delta likes <= -0.60", r_dl <= -0.60, f"{r_dl:+.3f}"),
       ("S2 delta beats totals", abs(r_dl) > abs(r_tl), f"delta {r_dl:+.3f} vs total {r_tl:+.3f}"),
       ("S3 break: delta plays weaker", abs(r_dp) < abs(r_dl), f"delta plays {r_dp:+.3f}"),
       ("S4 comments do not hurt", r_dlc <= r_dl + 0.05, f"delta likes+comments {r_dlc:+.3f}")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
print(f"(observed, not predicted) board positions changed over the hour: {POSITIONS_CHANGED}/{len(DATA)}; "
      f"total likes gained {sum(dl)}, songs gaining 0 likes {sum(1 for x in dl if x == 0)}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; n {len(rows)} of {len(DATA)}; rho delta likes {r_dl:+.2f}, total likes {r_tl:+.2f}, "
      f"delta plays {r_dp:+.2f}, delta likes+comments {r_dlc:+.2f}; median delta likes {sorted(dl)[len(dl)//2]}")
