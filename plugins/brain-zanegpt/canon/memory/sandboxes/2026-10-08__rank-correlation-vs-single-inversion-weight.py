"""Rebuild of suno#E5 claim with my own synthetic boards (no real Suno data).
Prediction (written before first run): for boards of 25 rows ranked by
score = 0.35*z(likes) + 0.15*z(plays) + 0.5*z(comments) (plays weight NONZERO),
(1) >= 90% of 20 boards contain at least one plays-inverted adjacent pair
(so one inversion would wrongly 'prove' plays ignored), (2) mean Spearman(rank, plays)
is <= -0.30 while |rho| for likes is larger, (3) with plays weight EXACTLY 0 but plays
correlated with likes, rho(plays) is still <= -0.20, so correlation alone cannot
prove weight>0 either (boundary of the rule)."""
M = 2 ** 31
def lcg(s):
    while True:
        s = (s * 1103515245 + 12345) % M
        yield s / M
def z(v):
    m = sum(v) / len(v); sd = (sum((x - m) ** 2 for x in v) / len(v)) ** .5 or 1
    return [(x - m) / sd for x in v]
def ranks(v):  # 1 = highest
    order = sorted(range(len(v)), key=lambda i: -v[i]); r = [0] * len(v)
    for k, i in enumerate(order): r[i] = k + 1
    return r
def spearman(a, b):
    ra, rb = ranks(a), ranks(b); n = len(a)
    return 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))
def board(seed, wp, n=25, plays_like_corr=0.6):
    g = lcg(seed); likes, plays, comm = [], [], []
    for _ in range(n):
        l = next(g); likes.append(l)
        plays.append(plays_like_corr * l + (1 - plays_like_corr) * next(g))
        comm.append(0.5 * l + 0.5 * next(g))
    score = [.35 * a + wp * b + .5 * c for a, b, c in zip(z(likes), z(plays), z(comm))]
    order = sorted(range(n), key=lambda i: -score[i])
    pos = [0] * n
    for k, i in enumerate(order): pos[i] = -(k + 1)  # more negative = lower rank; use rank directly below
    rank_score = [-(k) for k in range(n)]
    sc = [0] * n
    for k, i in enumerate(order): sc[i] = n - k   # high = top of chart
    inv = any(plays[order[k]] < plays[order[k + 1]] for k in range(n - 1))
    pos = [n + 1 - x for x in sc]  # chart position, 1 = top (matches the prediction sign)
    return likes, plays, comm, pos, inv
def run(wp):
    rp, rl, rc, inv = [], [], [], 0
    for s in range(1, 21):
        l, p, c, sc, i = board(s * 7919, wp)
        rp.append(spearman(sc, p)); rl.append(spearman(sc, l)); rc.append(spearman(sc, c)); inv += i
    m = lambda v: sum(v) / len(v)
    return inv / 20, m(rp), m(rl), m(rc)
w = run(0.15); z0 = run(0.0)
print("plays weight 0.15: inverted-pair boards %.2f, mean rho plays %.2f likes %.2f comments %.2f" % w)
print("plays weight 0.00: inverted-pair boards %.2f, mean rho plays %.2f likes %.2f comments %.2f" % z0)
# BREAK scenario: plays independent of likes, weight 0 -> rho should vanish
b = []
for s in range(1, 21):
    l, p, c, sc, i = board(s * 104729, 0.0, plays_like_corr=0.0); b.append(spearman(sc, p))
bm = sum(b) / len(b); print("plays weight 0, plays independent: mean rho plays %.2f" % bm)
c1 = w[0] >= .9; c2 = w[1] <= -.30 and abs(w[2]) > abs(w[1]); c3 = z0[1] <= -.20; c4 = abs(bm) < .2
print("c1 inversion everywhere:", c1, "| c2 rho nonzero & likes>plays:", c2, "| c3 zero-weight still correlates:", c3, "| c4 independent->~0:", c4)
print("RESULT: %s inversion in %.0f%% of weighted boards yet rho plays %.2f; zero-weight correlated plays rho %.2f; independent plays rho %.2f"
      % ("PASS" if c1 and c2 and c3 and c4 else "FAIL", w[0] * 100, w[1], z0[1], bm))
