# Kernels: DISTRIBUTION/reddit-containment (9:1 participation:promo, promo only in dedicated weekly threads),
# where-to-post (jam -> itch -> dedicated subs -> Show HN last), show-hn-survival (playable link, no marketing words).
# Memory: launch-plan-checker.../E1 (allowed promo = participation // 9).
# Model: day 0 = Monday. Subreddit g (gamedev-style) allows promo posts only on its thread day (Fri=4) and needs
# participation_in_that_sub >= 9 * (promo_in_that_sub + 1). Subreddit w (playmygame-style): promo any day, no ratio.
# Account makes C comments/day, spread by a policy. Plan: itch day>=0, g promo, w promo, then Show HN after both.
def earliest_g(C, per_sub):
    """days until first valid promo post in g; per_sub=True counts only comments made in g, False counts any sub."""
    part_g = 0; part_any = 0
    for day in range(0, 200):
        gc = C if per_sub else C // 2          # per_sub: all comments go to g; pooled: half go to g, half elsewhere
        part_g += gc; part_any += C
        have = part_g if per_sub else part_any
        if day % 7 == 4 and have >= 9: return day
    return None
# Scenario 1: 3 comments/day all into g -> need 9 -> day 3, but promo allowed only Friday (day 4)
d1 = earliest_g(3, True)
# Scenario 2: BREAK: comments spread, but ratio is per-subreddit: half the comments go elsewhere, so 9 in g takes longer
d2 = earliest_g(3, False) if False else None
def earliest_g_split(C, share_g):
    part = 0
    for day in range(200):
        part += C * share_g
        if day % 7 == 4 and part >= 9: return day
    return None
d2 = earliest_g_split(3, 0.5)           # 1.5/day -> 9 needs day 5 -> first Friday after is day 11
# Scenario 3: standalone post attempted on day 1 (Tue) with 9 comments done: invalid
standalone_ok = lambda day: day % 7 == 4
bad = not standalone_ok(1)
# Scenario 4: full plan wall-clock with 3 comments/day: itch day 0, w day 0 (no ratio), g at d1, Show HN day after g
plan_done = d1 + 1
# Scenario 5: two thread-gated subs each needing own 9: 18 comments at 3/day = day 5 -> Friday day 4 can post only one, other next Friday
def two_subs(C):
    part = 0; posted = []
    for day in range(200):
        part += C
        if day % 7 == 4:
            while part >= 9 and len(posted) < 2: part -= 9; posted.append(day)
        if len(posted) == 2: return posted
p = two_subs(3)
# Scenario 6: launch-plan-checker/E1 identity: allowed promo posts = participation // 9
allowed = lambda p: p // 9
ident = [allowed(n) for n in (8, 9, 18, 27)] == [0, 1, 2, 3]
print("S1 first g promo day", d1, "(comments ready day 2, Friday is day 4)")
print("S2 half the comments elsewhere ->", d2)
print("S3 Tuesday standalone invalid:", bad)
print("S4 whole plan done day", plan_done)
print("S5 two gated subs post days", p)
print("S6 allowed posts at 8/9/18/27:", [allowed(n) for n in (8, 9, 18, 27)])
ok = d1 == 4 and d2 == 11 and bad and plan_done == 5 and p == [4, 11] and ident
print("RESULT: %s first promo day %s (ready day 2, thread day 4); half-split comments %s; two gated subs %s; show HN day %s"
      % ("PASS" if ok else "FAIL", d1, d2, p, plan_done))
