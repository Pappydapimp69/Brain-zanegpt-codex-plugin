"""Sandbox: does Suno Trending 'Now' rank on engagement velocity, and do creator
followers matter (TikTok kernel: follower count is not a ranking factor)?

Data: read first-hand 2026-09-30 from suno.com/trending (Global) + public clip and
profile JSON. Row = (position, plays, likes, comments, age_hours, creator_followers).
Deterministic, stdlib only.

PREDICTION (written before the first run):
  S1 Now:    rho(pos, likes/hour) <= -0.60   (stronger than total likes, -0.42 last pass)
  S2 Now:    rho(pos, (likes+comments)/hour) <= rho(pos, likes/hour)  (comments add signal)
  S3 Weekly: |rho(pos, total likes)| > |rho(pos, likes/hour)|  (weekly is a totals board)
  S4 Both:   |rho(pos, followers)| < 0.30  (follower count not a ranking factor)
  S5 Break:  a followers-only ranker beats the best engagement ranker on either board
             -> claim broken. PASS means engagement tau > follower tau on both boards.
  S6 Now:    |rho(pos, age_hours)| < 0.30  (not a pure recency sort)
"""
import math

NOW = [
    (1, 1233, 354, 126, 49.8, 33036), (2, 4518, 320, 135, 50.5, 3254), (3, 50, 56, 0, 49.9, 1252),
    (4, 1822, 219, 50, 55.0, 1079), (5, 407, 223, 94, 26.2, 2661), (6, 184, 36, 6, 35.7, 841),
    (7, 1099, 297, 141, 68.7, 2959), (8, 285, 147, 73, 52.8, 4039), (9, 231, 121, 24, 63.2, 4208),
    (10, 497, 140, 12, 44.4, 11403), (11, 243, 105, 35, 54.9, 446), (12, 1762, 121, 16, 39.1, 4954),
    (13, 175, 88, 9, 76.0, 3482), (14, 92, 44, 10, 33.3, 321), (15, 262, 134, 46, 35.2, 7745),
    (16, 274, 115, 17, 42.0, 7059), (17, 216, 97, 32, 68.3, 2672), (18, 2526, 102, 46, 72.1, 222),
    (19, 279, 102, 29, 49.3, 3556), (20, 437, 132, 53, 72.9, 2536), (21, 193, 102, 45, 23.5, 654),
    (22, 158, 69, 19, 39.6, 2186), (23, 225, 82, 12, 54.3, 2272), (24, 200, 84, 23, 78.1, 1804),
    (25, 973, 243, 61, 62.4, 4742), (26, 195, 116, 56, 38.0, 13751), (27, 286, 93, 16, 47.0, 5907),
    (28, 133, 74, 17, 24.3, 387),
]
WEEKLY = [
    (1, 18847, 637, 358, 113.7, 528), (2, 97272, 1620, 153, 202.8, 20625), (3, 1461, 480, 121, 145.4, 2370),
    (4, 2837, 561, 206, 194.0, 33036), (5, 3926, 469, 238, 98.3, 4800), (6, 2456, 658, 198, 112.4, 5799),
    (7, 411, 356, 68, 124.3, 4583), (8, 3783, 196, 78, 86.5, 2389), (9, 4415, 260, 18, 204.8, 1801),
    (10, 15222, 795, 276, 206.1, 627), (11, 1257, 318, 40, 150.9, 2356), (12, 679, 281, 34, 180.2, 2771),
    (13, 948, 134, 21, 110.5, 572), (14, 1854, 389, 160, 117.8, 4439), (15, 930, 335, 123, 150.2, 3801),
    (16, 4369, 201, 24, 134.8, 4954), (17, 566, 181, 81, 223.7, 650), (18, 2483, 197, 25, 136.7, 23006),
    (19, 745, 220, 68, 222.5, 2536), (20, 376, 213, 35, 196.4, 446), (21, 27017, 555, 50, 209.8, 209),
    (22, 523, 176, 18, 124.5, 44), (23, 584, 175, 28, 200.9, 8293), (24, 2295, 196, 106, 190.9, 2655),
    (25, 351, 189, 20, 189.9, 4300), (26, 1369, 137, 28, 111.9, 1175),
]


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


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def rho(a, b):
    return pearson(ranks(a), ranks(b))


def tau_rank(signal, pos):
    n, s = len(pos), 0
    for i in range(n):
        for j in range(i + 1, n):
            d = (-signal[i] + signal[j]) * (pos[i] - pos[j])
            s += (d > 0) - (d < 0)
    return s / (n * (n - 1) / 2)


def signals(rows):
    pos = [r[0] for r in rows]
    likes = [r[2] for r in rows]
    vel = [r[2] / r[4] for r in rows]
    vel_lc = [(r[2] + r[3]) / r[4] for r in rows]
    fol = [r[5] for r in rows]
    age = [r[4] for r in rows]
    return pos, likes, vel, vel_lc, fol, age


out = []
p, lk, v, vlc, f, age = signals(NOW)
wp, wlk, wv, wvlc, wf, wage = signals(WEEKLY)

r_now = dict(likes=rho(p, lk), vel=rho(p, v), vel_lc=rho(p, vlc), followers=rho(p, f), age=rho(p, age))
r_wk = dict(likes=rho(wp, wlk), vel=rho(wp, wv), vel_lc=rho(wp, wvlc), followers=rho(wp, wf), age=rho(wp, wage))

out.append(("S1 now velocity <= -0.60", r_now["vel"] <= -0.60, f"vel {r_now['vel']:+.3f} vs total likes {r_now['likes']:+.3f}"))
out.append(("S2 now comments add", r_now["vel_lc"] <= r_now["vel"], f"vel_lc {r_now['vel_lc']:+.3f} vs vel {r_now['vel']:+.3f}"))
out.append(("S3 weekly totals beat velocity", abs(r_wk["likes"]) > abs(r_wk["vel"]), f"likes {r_wk['likes']:+.3f} vs vel {r_wk['vel']:+.3f}"))
out.append(("S4 followers |rho|<0.30 both", abs(r_now["followers"]) < 0.30 and abs(r_wk["followers"]) < 0.30,
            f"now {r_now['followers']:+.3f} weekly {r_wk['followers']:+.3f}"))
best_now = max(tau_rank(lk, p), tau_rank(v, p), tau_rank(vlc, p))
best_wk = max(tau_rank(wlk, wp), tau_rank(wv, wp), tau_rank(wvlc, wp))
tf_now, tf_wk = tau_rank(f, p), tau_rank(wf, wp)
out.append(("S5 break: followers ranker loses both", best_now > tf_now and best_wk > tf_wk,
            f"tau engagement/followers now {best_now:+.3f}/{tf_now:+.3f} weekly {best_wk:+.3f}/{tf_wk:+.3f}"))
out.append(("S6 now not pure recency", abs(r_now["age"]) < 0.30, f"age {r_now['age']:+.3f}"))

for name, ok, detail in out:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {detail}")
n = sum(ok for _, ok, _ in out)
print(("RESULT: PASS " if n == len(out) else "RESULT: FAIL ") +
      f"{n}/{len(out)}; now rho vel {r_now['vel']:+.2f} likes {r_now['likes']:+.2f} vel_lc {r_now['vel_lc']:+.2f} age {r_now['age']:+.2f} "
      f"followers {r_now['followers']:+.2f}; weekly rho likes {r_wk['likes']:+.2f} vel {r_wk['vel']:+.2f} followers {r_wk['followers']:+.2f}; "
      f"tau eng/fol now {best_now:+.2f}/{tf_now:+.2f} weekly {best_wk:+.2f}/{tf_wk:+.2f}")
