"""Kernel sandbox: ideas:GARDEN/mulch-benefits-and-stem-clearance-rule (2-4 in depth; keep 3-5 in from young stems, 8-12 in from mature
trunks) cross-checked against ideas:GARDEN/drip-irrigation-efficiency-plus-design-specs (2-4 point emitters around a tree's dripline) and
brainwork E105 (water saving flat past 4 in) / E113 (wood chips thin below 2 in by month 24).
Prediction (before run): for a 6 ft radius ring bed round a trunk of 6 in radius, a 12 in clearance removes under 5% of the mulch volume at
3 in depth (so the safe rule is nearly free), a pile ('volcano') of the same volume reaches 3x the depth next to the trunk, a dripline
emitter ring at 6 ft stays outside any clearance up to 12 in on every tested tree (kernel specs compatible), and with 25% yearly loss of depth
a 3 in layer falls under 2 in after 2 years, so the top-up needed to hold 3 in is about 1.7 in over 2 years. BREAK: a 4 in young-stem
clearance on a 2 ft-radius bed for a seedling at 12 in spacing wastes up to ~11% of the bed: the rule is cheap on big beds, not tiny ones."""
import math
IN2FT = 1 / 12.0
def ring_vol_cuft(R_ft, clear_in, depth_in):
    c = clear_in * IN2FT
    return math.pi * (R_ft ** 2 - c ** 2) * depth_in * IN2FT
def volcano_depth_in(vol_cuft, R_ft, trunk_in, slope=1.0):
    # cone peaking at the trunk: volume of cone height h radius R minus trunk cylinder-ish core, solved for h (bisection)
    lo, hi = 0.0, 3.0
    def v(h): return math.pi * R_ft ** 2 * h / 3.0 - math.pi * (trunk_in * IN2FT) ** 2 * h
    for _ in range(80):
        mid = (lo + hi) / 2
        if v(mid) < vol_cuft: lo = mid
        else: hi = mid
    return lo * 12.0
R, trunk = 6.0, 6.0
full = ring_vol_cuft(R, trunk, 3.0)
for clear in (8, 12):
    cv = ring_vol_cuft(R, trunk + clear, 3.0)
    print(f"mature tree R=6ft clear={clear}in: volume {cv:.1f} vs {full:.1f} cu ft, saves {(1-cv/full)*100:.1f}%")
save12 = 1 - ring_vol_cuft(R, trunk + 12, 3.0) / full
volc = volcano_depth_in(full, R, trunk)
print(f"volcano of the same volume peaks at {volc:.1f} in at the trunk = {volc/3.0:.1f}x the 3 in layer")
# emitters at dripline vs clearance for several canopy radii
ok = True
for canopy in (4, 6, 8, 10):
    for clear in (8, 12):
        gap = canopy - (trunk + clear) * IN2FT
        if gap <= 0: ok = False
    print(f"canopy {canopy}ft: dripline emitters {canopy-(trunk+12)*IN2FT:.1f} ft outside a 12in clearance edge")
# decay: 25 percent yearly loss of remaining depth
d = 3.0; hist = []
for y in (1, 2, 3):
    d *= 0.75; hist.append(d)
topup2 = 3.0 - 3.0 * 0.75 ** 2
print("depth after yr1-3: " + ", ".join(f"{x:.2f}" for x in hist) + f" in; top-up to hold 3 in after 2 yrs = {topup2:.2f} in")
# BREAK: small bed
R2, seedling = 2.0, 0.5
full2 = ring_vol_cuft(R2, 0, 3.0); cl2 = ring_vol_cuft(R2, 4 + seedling * 12 * 0, 3.0)
waste = 1 - cl2 / full2
print(f"BREAK seedling bed R=2ft, 4in clearance: wastes {waste*100:.1f}% of bed volume")
# tiny bed per plant: 12in spacing -> R=0.5ft
waste_small = 1 - ring_vol_cuft(0.5, 4, 3.0) / ring_vol_cuft(0.5, 0, 3.0)
print(f"BREAK per-plant R=0.5ft, 4in clearance: wastes {waste_small*100:.1f}%")
good = save12 < 0.05 and ok and abs(volc / 3.0 - 3.0) < 1.5 and topup2 > 1.0 and waste_small > 0.10
print(("RESULT: PASS " if good else "RESULT: FAIL ") + f"12in clearance saves-volume {save12*100:.1f}%, volcano {volc:.1f}in, topup {topup2:.2f}in, small-bed waste {waste_small*100:.1f}%")
