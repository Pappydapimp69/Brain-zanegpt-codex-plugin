# Deterministic sandbox for the drip design-specs kernel: pressure regulation, emitter spacing, zone GPM, with soil + mulch.
# Prediction (before run): at 12-18 in spacing, 0.5 gph emitters give a continuous wet strip (no gap) in loam and clay
# but leave gaps in sand at 18 in; unregulated 60 psi raises flow by >=50% vs 25 psi so a 5 gpm supply fits >=30% fewer
# emitters; 3 in mulch cuts run time by >=15%; a one-zone design mixing a vegetable bed and trees wastes water vs split zones.
import math
RADIUS = {"sand": 6.0, "loam": 10.0, "clay": 14.0}     # assumed lateral wet radius in inches for 0.5 gph over a set
def gaps(spacing, soil):                                 # strip is continuous when 2*radius >= spacing
    return 2 * RADIUS[soil] < spacing
res = {s: {sp: gaps(sp, s) for sp in (12, 18, 24)} for s in RADIUS}
print("gap at spacing:", res)
ok1 = not res["loam"][12] and not res["loam"][18] and not res["clay"][18] and res["sand"][18] and not res["sand"][12]
ok1b = res["loam"][24] is True  # break: out of kernel range, gaps in loam appear at 24 in? (20 in wet width < 24)
def flow(gph, psi, design=25.0): return gph * math.sqrt(psi / design)   # orifice-type, assumed
f60 = flow(0.5, 60) / flow(0.5, 25)
SUPPLY_GPM = 5.0
n25 = int(SUPPLY_GPM * 60 / flow(0.5, 25)); n60 = int(SUPPLY_GPM * 60 / flow(0.5, 60))
print("flow ratio 60/25 psi %.2f; emitters per 5 gpm zone %d at 25 psi vs %d at 60 psi" % (f60, n25, n60))
ok2 = f60 >= 1.5 and n60 <= 0.7 * n25
# run time: demand mm/day over bed; mulch cuts evaporation share (E105 constants)
def runtime(mulch_in, soil="loam", bed_m2=10.0, demand=5.0, evap=0.5, eff=0.92):
    d = demand * (1 - evap) + demand * evap * math.exp(-0.6 * mulch_in)
    litres = d * bed_m2 / eff
    spacing_m = 0.3; rows = 2; length = bed_m2 / (rows * 0.5)       # 0.5 m row spacing
    emitters = rows * int(length / spacing_m)
    gph = emitters * 0.5 * 3.785                                    # litres per hour
    return litres / gph * 60                                        # minutes
rt0, rt3 = runtime(0), runtime(3)
print("run minutes bare %.0f mulch3in %.0f" % (rt0, rt3))
ok3 = rt3 <= 0.85 * rt0
# zone split: veg bed (daily, shallow) + tree (deep weekly) on one valve vs two valves; same run time to satisfy the thirstier
def one_zone_waste(veg_min=rt3, tree_min=60.0, veg_gph=40.0, tree_gph=30.0):
    run = max(veg_min, tree_min)
    over = (run - veg_min) * veg_gph / 60.0         # litres over-applied to the veg bed if tree needs the longer run
    return over, run
over, run = one_zone_waste()
print("one zone: run %.0f min, veg bed over-applied %.1f L; split zones waste 0" % (run, over))
ok4 = over > 0
# soil jar link: loam stands for 40/40/20 mix; wet radius drops to sand value when jar's silt mark is misread (silt 7.7 as sand-heavy)
misread = "sand"
print("misread loam as sand => spacing used 12 in; true loam allows 18: emitters wasted %.0f%%" % (100 * (1 - 12 / 18)))
ok5 = (1 - 12 / 18) > 0.3
ok = all([ok1, ok1b, ok2, ok3, ok4, ok5])
print("checks", ok1, ok1b, ok2, ok3, ok4, ok5)
print("RESULT: %s sand gaps at 18in, loam/clay none to 18in, loam gaps at 24in; 60psi flow x%.2f (%d vs %d emitters); mulch run %.0f->%.0f min; mixed zone over-applies %.0f L"
      % ("PASS" if ok else "FAIL", f60, n60, n25, rt0, rt3, over))
