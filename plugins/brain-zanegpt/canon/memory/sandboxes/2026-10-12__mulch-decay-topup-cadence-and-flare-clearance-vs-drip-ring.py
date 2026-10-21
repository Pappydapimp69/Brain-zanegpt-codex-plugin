"""Mulch kernel under decay: depth 2-4 in, clearance 3-5 in (young stem) / 8-12 in (mature trunk), organic vs stone.
Kernels/entries exercised: ideas:GARDEN/mulch-benefits-and-stem-clearance-rule (2-4 in depth, clearance, organic adds
fertility, stone does not), ideas:GARDEN/drip-irrigation-efficiency-plus-design-specs (2-4 point emitters at the dripline,
1-2 gph), brainwork/E105 (stem stays dry only while clearance > 0).
Constants assumed: organic decay 1.0 in/yr of depth, stone 0; organic OM release 0.04 lb per sq ft per inch decayed;
weed suppression needs depth >= 2 in; bed radius 36 in; mature trunk radius 6 in + flare growth 0.5 in/yr.
Prediction (before run): a 4 in layer with no top-up drops below 2 in after 2.0 yr, a 3 in layer after 1.0 yr, so the top-up
interval is (d0-2)/decay; stone never needs top-up and adds 0 OM; topping up by dumping mulch against the stem gives wet
days within one season (clearance 0), raking back keeps 0; a mulch ring fixed at c in from the trunk CENTER has a gap to the
FLARE edge of c-(6+0.5*yr): 2 in at c=8 yr0, 0 in at yr4 (kernel's 8-12 in is measured from the flare, so a fixed ring
silently closes); dripline ring 24 in from the trunk is outside all clearances."""
DECAY = {"organic": 1.0, "stone": 0.0}
OM = {"organic": 0.04, "stone": 0.0}
def years_to_floor(d0, kind, floor=2.0):
    return float("inf") if DECAY[kind] == 0 else (d0 - floor) / DECAY[kind]
def depth_series(d0, kind, years, topup_to=None, floor=2.0, step=0.25):
    d, t, out, tops = d0, 0.0, [], 0
    while t < years - 1e-9:
        d -= DECAY[kind] * step; t += step
        if topup_to is not None and d < floor:
            d = topup_to; tops += 1
        out.append(d)
    return min(out), tops
ok = {}
print("1) years until depth < 2 in, no top-up")
for d0 in (2.5, 3, 4):
    print(f"   organic {d0} in: {years_to_floor(d0,'organic'):.2f} yr; stone: {years_to_floor(d0,'stone')}")
ok["y4"] = years_to_floor(4, "organic") == 2.0 and years_to_floor(3, "organic") == 1.0
ok["stone"] = years_to_floor(3, "stone") == float("inf")
print("2) 5-year bed (area 28.3 sq ft), top-up to 3 in whenever depth < 2 in")
area = 3.14159 * (36/12) ** 2
for kind in ("organic", "stone"):
    lo, tops = depth_series(3.0, kind, 5, topup_to=3.0)
    om = OM[kind] * DECAY[kind] * 5 * area
    print(f"   {kind}: min depth {lo:.2f} in, top-ups {tops}, OM released {om:.1f} lb")
    ok[f"min_{kind}"] = lo >= 1.9 if kind == "organic" else lo == 3.0
ok["om"] = OM["stone"] == 0 and OM["organic"] > 0
print("3) stem wet days per year (E105 style: wet while mulch touches the stem), top-up policy")
def wet_days(clear_in, season=120): return season if clear_in <= 0 else 0
dump = wet_days(0); rake = wet_days(3)
print(f"   dump against stem: {dump} wet days; rake back to 3 in: {rake}")
ok["dump"] = dump > 0 and rake == 0
print("4) mature trunk: clearance measured from trunk CENTER vs from FLARE edge (flare radius grows 0.5 in/yr from 6 in)")
for c in (8, 10, 12):
    print(f"   ring fixed {c} in from center: gap to flare edge", " | ".join(f"yr{yr} {c - (6 + 0.5 * yr):.1f} in" for yr in (0, 4, 8)))
# gap from flare edge when ring is fixed at c from center: c - flare_radius
gap = lambda c, yr: c - (6 + 0.5 * yr)
ok["flare"] = gap(8, 0) == 2 and gap(8, 4) == 0 and gap(12, 8) == 2 
print("   (a ring fixed 8 in from center is 2 in clear of the flare at yr0 and 0 in at yr4; 12 in from center is 2 in clear at yr8)")
print("5) dripline emitters (24 in from trunk) vs clearance ring")
ok["ring"] = all(24 > c for c in (3, 5, 8, 12)) and 24 > 6 + 0.5 * 8 + 12
print("   24 in ring outside 12 in clearance + flare at yr8 (10 in):", ok["ring"])
print("ok:", ok)
print(("RESULT: PASS" if all(ok.values()) else "RESULT: FAIL") +
      f" 4 in lasts 2.0 yr, 3 in 1.0 yr; stone 0 OM; dump=wet {dump} d vs rake {rake}; 8 in center ring is 0 in from flare at yr4")
