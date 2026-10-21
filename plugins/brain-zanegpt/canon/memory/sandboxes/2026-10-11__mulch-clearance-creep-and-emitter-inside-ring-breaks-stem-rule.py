"""Deterministic model: does a fixed stem-clearance gap keep a stem dry?
Mulch inner edge sits at gap g (in) from the stem. Mulch creeps inward
`creep` in/day (settling, wind, foot traffic); raking resets gap to g0.
A day is a stem-wet day if (a) mulch touches the stem and mulch is moist
(moist for MOIST_DAYS after any wetting, 3-4in depth keeps it longer), or
(b) a drip emitter sits within the stem splash/wet radius of the stem.
Wetting events: every 3rd day (irrigation/rain), fixed schedule."""
DAYS = 120
MOIST_DAYS = {2: 2, 3: 3, 4: 4}   # mulch depth -> days moist after wetting

def stem_wet_days(g0, creep, rake_every, depth, emitter_r, wet_r):
    gap = float(g0); wet_days = 0; last_wet = -99
    for d in range(DAYS):
        if rake_every and d and d % rake_every == 0:
            gap = float(g0)
        gap = max(0.0, gap - creep)
        if d % 3 == 0:
            last_wet = d
        moist = d - last_wet < MOIST_DAYS[depth]
        touch = gap <= 0.0 and moist
        direct = emitter_r is not None and emitter_r <= wet_r and d % 3 == 0
        if touch or direct:
            wet_days += 1
    return wet_days

res = {}
# S1 static ring, no creep: gap 0 vs 3 vs 5
for g in (0, 3, 5):
    res[f"S1 gap{g} nocreep"] = stem_wet_days(g, 0.0, 0, 4, None, 6)
# S2 creep 0.05 in/day (3 in lost by day 60) -- built to BREAK static rule
for g in (3, 5):
    res[f"S2 gap{g} creep.05"] = stem_wet_days(g, 0.05, 0, 4, None, 6)
# S3 same creep, rake every 30 days
for g in (3, 5):
    res[f"S3 gap{g} creep.05 rake30"] = stem_wet_days(g, 0.05, 30, 4, None, 6)
# S4 depth effect on wet days at gap 0 (contact)
for dp in (2, 3, 4):
    res[f"S4 gap0 depth{dp}"] = stem_wet_days(0, 0, 0, dp, None, 6)
# S5 drip emitter inside ring (4 in from stem, wet radius 6) with correct 3in gap
res["S5 gap3 emitter4in wet6"] = stem_wet_days(3, 0, 0, 4, 4, 6)
res["S5 gap3 emitter8in wet6"] = stem_wet_days(3, 0, 0, 4, 8, 6)
for k, v in res.items():
    print(f"{k}: {v}")
ok = (res["S1 gap3 nocreep"] == 0 and res["S1 gap5 nocreep"] == 0
      and res["S1 gap0 nocreep"] > 80
      and res["S2 gap3 creep.05"] > 0 and res["S2 gap5 creep.05"] == 0
      and res["S3 gap3 creep.05 rake30"] == 0
      and res["S4 gap0 depth4"] > res["S4 gap0 depth2"]
      and res["S5 gap3 emitter4in wet6"] > 0 and res["S5 gap3 emitter8in wet6"] == 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"gap3 static dry; creep .05 breaks gap3 ({res['S2 gap3 creep.05']} wet days) not gap5; "
      f"rake30 restores; emitter inside wet radius wets stem despite gap ({res['S5 gap3 emitter4in wet6']})")
