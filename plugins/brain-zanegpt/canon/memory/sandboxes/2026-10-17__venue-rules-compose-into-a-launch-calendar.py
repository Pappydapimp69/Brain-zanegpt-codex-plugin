# Sandbox: five DISTRIBUTION kernels as a checkable launch-plan linter + a greedy scheduler.
# Day 0 is a Monday; day%7==5 is the Saturday self-promo thread. Action = (day, venue, kind, copy_id).
# Rules encoded from the kernels (each is a plain predicate, applied to the plan, not to the scheduler):
#  R1 reddit-containment: a promo in r/gamedev needs >=9 participation comments earlier and must sit in the Saturday thread
#  R2 jam-first-hn-last: itch listing after the jam ends; Show HN is the last promo and happens once
#  R3 show-hn-survival: Show HN needs a live playable (itch listing exists) and a non-marketing title
#  R4 never-duplicate-copy: no copy_id used at two different venues
#  R5 itch-devlog-cadence: devlog posts at least 15 days apart
def lint(plan, jam_end):
    v = []
    def promos(venue): return [a for a in plan if a[1] == venue and a[2] == "promo"]
    for d, ven, k, c in plan:
        if ven == "r/gamedev" and k == "promo":
            comments = sum(1 for a in plan if a[1] == "r/gamedev" and a[2] == "comment" and a[0] < d)
            if comments < 9 or d % 7 != 5: v.append("R1")
        if ven == "itch" and k == "listing" and d <= jam_end: v.append("R2a")
    hn = promos("hn")
    if len(hn) > 1: v.append("R2b")
    if hn:
        hd = hn[0][0]
        if any(a[2] == "promo" and a[0] > hd for a in plan): v.append("R2c")
        if not any(a[2] == "listing" and a[0] < hd for a in plan): v.append("R3a")
        if hn[0][3].startswith("mkt"): v.append("R3b")
    seen = {}
    for d, ven, k, c in plan:
        if k == "promo":
            if c in seen and seen[c] != ven: v.append("R4")
            seen.setdefault(c, ven)
    dl = sorted(a[0] for a in plan if a[2] == "devlog")
    if any(b - a < 15 for a, b in zip(dl, dl[1:])): v.append("R5")
    return sorted(set(v))

def schedule(jam_end):
    plan, d = [], 0
    for i in range(9): plan.append((i // 3, "r/gamedev", "comment", "-"))     # 3 comments a day, days 0-2
    listing = jam_end + 1
    plan += [(listing, "itch", "listing", "-"), (listing, "itch", "devlog", "-"),
             (listing, "r/playmygame", "promo", "copy-b")]
    sat = next(x for x in range(listing, listing + 8) if x % 7 == 5)
    plan.append((sat, "r/gamedev", "promo", "copy-a"))
    plan.append((max(sat, listing) + 1, "hn", "promo", "plain-c"))
    return plan

for jam in (3, 8):
    p = schedule(jam)
    hn = [a for a in p if a[1] == "hn"][0][0]
    print("jam_end", jam, "lint", lint(p, jam), "hn_day", hn)
    if jam == 3:
        early = [a if a[1] != "hn" else (a[0] - 2,) + a[1:] for a in p]       # HN a day earlier
        print(" hn two days earlier:", lint(early, jam))
naive = [(4, "itch", "listing", "-"), (4, "r/gamedev", "promo", "copy-a"), (4, "r/WebGames", "promo", "copy-a"),
         (4, "hn", "promo", "mkt-a"), (5, "hn", "promo", "mkt-a"), (5, "itch", "devlog", "-"), (6, "itch", "devlog", "-")]
nl = lint(naive, 3)
print("naive", nl)
p3, p8 = schedule(3), schedule(8)
ok = (lint(p3, 3) == [] and lint(p8, 8) == [] and len(nl) >= 6
      and lint([a if a[1] != "hn" else (a[0] - 2,) + a[1:] for a in p3], 3) == ["R2c", "R3a"]
      and [a for a in p3 if a[1] == "hn"][0][0] == 6 and [a for a in p8 if a[1] == "hn"][0][0] == 13)
print("RESULT: %s greedy schedule lints clean (HN day 6 at jam_end 3, day 13 at jam_end 8: the Saturday thread, not the jam, sets HN); naive plan trips %d rules (%s); HN placed before the Saturday thread trips R2c and R3a" % ("PASS" if ok else "FAIL", len(nl), ",".join(nl)))
