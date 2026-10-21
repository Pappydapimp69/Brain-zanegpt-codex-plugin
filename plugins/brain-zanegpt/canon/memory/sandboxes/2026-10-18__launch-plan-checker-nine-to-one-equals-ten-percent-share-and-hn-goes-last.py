# Launch-plan checker built from three kernels: where-to-post (order jam > itch > dedicated
# subreddits > Show HN last, about 10 percent self-promo share on general subreddits,
# never resubmit to a venue in short succession), reddit-containment (participation outnumbers
# self-promo about 9:1; direct promo goes in the dedicated thread) and show-hn-survival
# (live playable URL, author comment, no marketing words).
# PREDICTION (before run): (1) the 9:1 participation rule and the 10 percent promo share allow
# the same maximum promo posts for every participation count 0..200 (p <= C/9 both ways), while
# the misreading "promo <= 10 percent of participation" allows fewer posts at C = 9, 18, 27 (1
# vs 0, 2 vs 1, 3 vs 2); (2) a plan that posts Show HN before the dedicated subreddits or without
# a playable URL fails; (3) the good plan passes with 3 promo posts needing 27 participation actions.
ORDER = ["jam", "itch", "dedicated_sub", "show_hn"]
MARKETING = ("amazing", "revolutionary", "best ever", "game-changing")
def max_promo_ratio(c): return c // 9                       # 9 participation : 1 promo
def max_promo_share(c):                                      # promo / (promo + c) <= 10 %
    p = 0
    while 10 * (p + 1) <= (p + 1) + c: p += 1
    return p
def max_promo_wrong(c): return c // 10                       # promo <= 10 % of participation
def check(plan, participation):
    """plan: list of dict(venue, day, playable_url, title). returns list of problems."""
    errs = []
    venues = [p["venue"] for p in plan]
    idx = [ORDER.index(v) for v in venues]
    if idx != sorted(idx): errs.append("order")
    if venues.count("show_hn") > 1: errs.append("hn resubmitted")
    for p in plan:
        if p["venue"] == "show_hn":
            if not p.get("playable_url"): errs.append("hn no playable url")
            if any(w in p["title"].lower() for w in MARKETING): errs.append("hn marketing voice")
    promo = sum(1 for p in plan if p["venue"] in ("dedicated_sub", "show_hn"))
    if promo > max_promo_ratio(participation): errs.append("ratio")
    return errs
good = [dict(venue="jam", day=1), dict(venue="itch", day=20), dict(venue="dedicated_sub", day=25),
        dict(venue="dedicated_sub", day=40), dict(venue="show_hn", day=60, playable_url="https://x.test/play", title="Show HN: a tiny tide puzzle")]
bad_order = [good[0], good[1], good[4], good[2]]
bad_url = good[:4] + [dict(venue="show_hn", day=60, playable_url="", title="Show HN: a tiny tide puzzle")]
bad_voice = good[:4] + [dict(venue="show_hn", day=60, playable_url="u", title="Show HN: the best ever amazing game")]
same = all(max_promo_ratio(c) == max_promo_share(c) for c in range(0, 201))
diff = [(c, max_promo_ratio(c), max_promo_wrong(c)) for c in (9, 18, 27)]
r_good, r_order, r_url, r_voice = check(good, 27), check(bad_order, 27), check(bad_url, 27), check(bad_voice, 27)
r_ratio = check(good, 26)
print("ratio==share on 0..200:", same, "| misreading differs at", diff)
print("good", r_good, "order", r_order, "url", r_url, "voice", r_voice, "ratio at 26", r_ratio)
ok = (same and diff == [(9, 1, 0), (18, 2, 1), (27, 3, 2)] and r_good == [] and "order" in r_order
      and "hn no playable url" in r_url and "hn marketing voice" in r_voice and r_ratio == ["ratio"])
print("RESULT: %s 9:1 equals 10 percent share on 201 counts, misreading allows %s, good plan clean at 27 actions, order/url/voice/ratio violations each caught"
      % ("PASS" if ok else "FAIL", [(c, w) for c, _, w in diff]))
