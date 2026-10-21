# Deterministic 60-day dry-spell bucket model: mulch depth x irrigation method x soil, plus stem-wet days by clearance.
import math
DAYS, ET = 60, 5.0
EVAP_SHARE, WEED_USE = 0.4, 1.5
# soil: loam fixture is the 40/40/20 sand/silt/clay mix from the soil-jar entry; capacity = mm available water (assumed)
CAP = {"sand": 10.0, "loam": 22.0, "clay": 26.0}
EFF = {"drip": 0.92, "soaker": 0.75, "sprinkler": 0.60}   # drip kernel figures (midpoints)

def season(soil, method, depth):
    cap = CAP[soil]; w = cap; applied = 0.0; wet_days = 0; irrigations = 0; last_irrig = -99
    evap = ET * EVAP_SHARE * math.exp(-0.6 * depth)
    weeds = WEED_USE * math.exp(-0.8 * depth)
    trans = ET * (1 - EVAP_SHARE)
    for d in range(DAYS):
        w -= evap + trans + weeds
        if w < 0.5 * cap:
            need = cap - w
            applied += need / EFF[method]; w = cap; irrigations += 1; last_irrig = d
        wet_days += (d - last_irrig) < 1 + 2 * depth    # surface stays damp longer under mulch
    return applied, irrigations, wet_days

def stem_wet_days(depth, clearance, emitter_at_stem):
    _, _, wet = season("loam", "drip", depth)
    touching = clearance < 3
    exposure = 1.0 if (touching and emitter_at_stem) else (0.5 if touching else 0.0)
    return wet * exposure

res = {}
print("water applied (mm) by depth in loam, drip:", {d: round(season("loam", "drip", d)[0]) for d in (0, 1, 2, 3, 4, 6, 8)})
bare = season("loam", "drip", 0)[0]
save = {d: 1 - season("loam", "drip", d)[0] / bare for d in (1, 2, 3, 4, 6, 8)}
res["m1_3in_saves_25pct"] = save[3] >= 0.25
marg = {d: save[d] - save[p] for p, d in ((1, 2), (2, 3), (3, 4), (4, 6), (6, 8))}
res["m2_diminishing_returns_past_4in"] = (save[8] - save[4]) < 0.5 * save[2]
m = {meth: season("loam", meth, 3)[0] for meth in EFF}
res["m3_method_order_drip_lt_soaker_lt_sprinkler"] = m["drip"] < m["soaker"] < m["sprinkler"]
ratio = m["sprinkler"] / m["drip"]
res["m4_ratio_matches_efficiency"] = abs(ratio - EFF["drip"] / EFF["sprinkler"]) < 0.1   # same crop need, so water ~ 1/eff
saved_mm = {s: season(s, "drip", 0)[0] - season(s, "drip", 3)[0] for s in CAP}
irr = {s_: season(s_, "drip", 3)[1] for s_ in CAP}
res["m5_soil_changes_interval_not_water_saved"] = len(set(round(v) for v in saved_mm.values())) == 1 and irr["sand"] > irr["loam"] >= irr["clay"]
pct = {s: saved_mm[s] / season(s, "drip", 0)[0] for s in CAP}
sw = {c: stem_wet_days(3, c, True) for c in (0, 1, 3, 5)}
res["s1_clearance_3in_cuts_stem_wet_to_zero"] = sw[0] > 0 and sw[3] == 0 and sw[5] == 0
res["s2_touching_stem_wet_near_saturated_for_any_mulch_depth_clearance_decides"] = abs(stem_wet_days(6, 0, True) - stem_wet_days(2, 0, True)) <= 2 and stem_wet_days(2, 0, True) > 1.8 * season("loam", "drip", 0)[2] and stem_wet_days(6, 4, True) == stem_wet_days(2, 4, True) == 0
res["s3_emitter_away_from_stem_halves_touching_exposure"] = stem_wet_days(3, 0, False) == 0.5 * stem_wet_days(3, 0, True)
print("save by depth", {d: round(v, 3) for d, v in save.items()})
print("marginal", {d: round(v, 3) for d, v in marg.items()})
print("method water at 3in", {k: round(v) for k, v in m.items()})
print("mm saved by soil", {k: round(v) for k, v in saved_mm.items()}, "pct", {k: round(v, 3) for k, v in pct.items()})
print("stem wet days by clearance", sw, "irrigations by soil at 3in", irr)
for k, v in res.items(): print(k, v)
ok = all(res.values())
print("RESULT:", "PASS" if ok else "FAIL", "3in mulch saves %.0f%% in loam drip; 8in adds %.0f points over 4in; stem-wet days %s by clearance 0/1/3/5in; soils mm saved %s irrigations %s"
      % (save[3] * 100, (save[8] - save[4]) * 100, [round(sw[c], 1) for c in (0, 1, 3, 5)], {k: round(v) for k, v in saved_mm.items()}, irr))
