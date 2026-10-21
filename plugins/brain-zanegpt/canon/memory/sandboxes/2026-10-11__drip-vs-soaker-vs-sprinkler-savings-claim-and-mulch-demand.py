"""Check the drip kernel's internal consistency and its interaction with mulch.
Kernel claims: efficiency drip 90-95, soaker 70-80, sprinkler 50-70 percent; a drip kit uses
30-50 percent less water than a sprinkler and 30-40 percent less than a soaker over a season.
Water applied = crop need / efficiency, so saving = 1 - e_other/e_drip. Mulch input: E105 mulch with drip
saved about 47 percent and E112 cut run time 42 percent (used as the crop-need reduction, applied
equally to all methods since mulch lowers soil evaporation, not application loss).
Prediction (before running): the 30-50 percent vs sprinkler claim is reachable inside the efficiency
ranges (needs e_sprinkler/e_drip between 0.5 and 0.7), the 30-40 percent vs soaker claim is NOT reachable
(the max possible is 1-0.70/0.95 = 26 percent), mulch leaves the percent saving unchanged but cuts the
gallons saved by the same 42-47 percent, and a 1000 sq ft bed at 1 in/week for 20 weeks needs about
12.4k gal with 92.5 percent drip."""
RANGE = {"drip": (0.90, 0.95), "soaker": (0.70, 0.80), "sprinkler": (0.50, 0.70)}
def saving(other, ed, eo): return 1 - eo / ed
lo_hi = {}
for m in ("soaker", "sprinkler"):
    vals = [saving(m, ed, eo) for ed in RANGE["drip"] for eo in RANGE[m]]
    lo_hi[m] = (min(vals), max(vals))
    print(f"1) drip saving vs {m}: {lo_hi[m][0]:.1%} to {lo_hi[m][1]:.1%} across the efficiency ranges")
spr_claim, soak_claim = (0.30, 0.50), (0.30, 0.40)
spr_overlap = lo_hi["sprinkler"][1] >= spr_claim[0] and lo_hi["sprinkler"][0] <= spr_claim[1]
spr_cover = lo_hi["sprinkler"][0] >= spr_claim[0]
soak_reach = lo_hi["soaker"][1] >= soak_claim[0]
print(f"   sprinkler claim 30-50 percent: overlaps {spr_overlap}, fully implied {spr_cover}; soaker claim 30-40 reachable {soak_reach}")
# gallons: 1000 sq ft, 1 in/week for 20 weeks, 0.623 gal per sq ft per in
need = 1000 * 0.623 * 1 * 20
mid = {"drip": 0.925, "soaker": 0.75, "sprinkler": 0.60}
gal = {m: need / e for m, e in mid.items()}
print("2) bare soil gallons:", {m: round(g) for m, g in gal.items()})
for mulch in (0.42, 0.47):
    g2 = {m: need * (1 - mulch) / e for m, e in mid.items()}
    pct = 1 - g2["drip"] / g2["sprinkler"]
    abs_saved = gal["sprinkler"] - gal["drip"], g2["sprinkler"] - g2["drip"]
    print(f"3) mulch cut {mulch:.0%}: drip {g2['drip']:.0f} sprinkler {g2['sprinkler']:.0f}; percent saving {pct:.1%} (bare {1-gal['drip']/gal['sprinkler']:.1%}); gallons saved {abs_saved[0]:.0f} -> {abs_saved[1]:.0f} ({abs_saved[1]/abs_saved[0]-1:+.0%})")
# break case: mulch that also stops sprinkler loss (sprinkler wets mulch, interception 10 percent extra loss)
g_spr_int = need * (1 - 0.47) / (0.60 * 0.90)
print(f"4) sprinkler on mulch with 10 percent extra interception: {g_spr_int:.0f} gal vs drip {need*(1-0.47)/0.925:.0f}; saving {1-(need*(1-0.47)/0.925)/g_spr_int:.1%}")
gal_pred_ok = abs(need / mid['drip'] - 12400) < 600   # prediction as written; arithmetic slip in the docstring figure
print('5) docstring gallon prediction (about 12.4k) held:', gal_pred_ok)
ok = spr_overlap and not soak_reach and lo_hi['soaker'][1] < 0.30 and gal_pred_ok
print(f"RESULT: {'PASS' if ok else 'FAIL'} drip vs sprinkler {lo_hi['sprinkler'][0]:.0%}-{lo_hi['sprinkler'][1]:.0%} (claim 30-50), vs soaker {lo_hi['soaker'][0]:.0%}-{lo_hi['soaker'][1]:.0%} (claim 30-40, unreachable), mulch keeps percent but cuts gallons saved 42-47 percent, drip bed {need/mid['drip']:.0f} gal (predicted 12.4k: {'held' if gal_pred_ok else 'missed'})")
