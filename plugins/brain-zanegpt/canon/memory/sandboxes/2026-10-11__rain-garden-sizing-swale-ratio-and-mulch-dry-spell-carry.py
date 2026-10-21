# Deterministic sandbox: rain garden sizing rule, swale-vs-flat ratio, and dry-spell carry with mulch.
# Prediction (written before run): 1/6 clay & 1/8 sand gardens capture >=90% of a 25mm/2h storm,
# clay garden fails (<70%) for a 75mm/2h storm; swale/flat ratio lands in 8-12x for a mid storm only;
# mulch adds at least 20% to days of crop cover from the infiltrated water.
import math
INF = {"sand": 25.0, "clay": 3.0}   # mm/h assumed saturated infiltration
DIV = {"sand": 8, "clay": 6}        # kernel sizing divisors
POND = 150.0                        # mm ponding depth, assumed
def garden_capture(soil, rain_mm, hours, div=None, runoff_c=0.9, drain=1000.0):
    ag = drain / (div or DIV[soil])
    inflow = drain * rain_mm * runoff_c            # litres (m2*mm)
    cap = ag * (POND + INF[soil] * hours)
    return min(inflow, cap) / inflow
res = {}
for soil in INF:
    for rain in (25, 75):
        res[(soil, rain)] = garden_capture(soil, rain, 2)
    res[(soil, "undersized /20", 25)] = garden_capture(soil, 25, 2, div=20)
print({str(k): round(v, 2) for k, v in res.items()})
ok1 = res[("sand", 25)] >= .9 and res[("clay", 25)] >= .9
ok2 = res[("clay", 75)] < .7
# swale: 1.2 m wide x 0.45 m deep trench on contour, catchment strip 3 m uphill (flat ground, 10% runoff-free)
def swale_vs_flat(rain, hours, soil="clay", catch=3.0, width=1.2, depth=450.0):
    flat_inf = min(rain, INF[soil] * hours)                       # mm per m2 on ungraded ground
    flat_per_m = flat_inf * (catch + width)                       # litres per metre of length
    inflow = rain * (catch + width)
    cap = width * (depth * 0.4 + INF[soil] * hours)               # gravel/soil void 40%
    sw = min(inflow, cap)
    return sw / flat_per_m
ratios = {r: round(swale_vs_flat(r, 2), 1) for r in (10, 25, 50, 100, 200)}
print("swale/flat ratio by storm mm:", ratios)
in_band = [r for r, v in ratios.items() if 8 <= v <= 12]
ok3 = 0 < len(in_band) < len(ratios)
# dry-spell carry: infiltrated water (mm over 20 m2 bed) vs daily demand, mulch evap cut per E105
def carry_days(store_mm, mulch_in):
    demand = 5.0; evap_share = 0.5
    d = demand * (1 - evap_share) + demand * evap_share * math.exp(-0.6 * mulch_in)
    return store_mm / d
store = 40.0
bare, m3 = carry_days(store, 0), carry_days(store, 3)
print("carry days bare %.1f mulch3in %.1f" % (bare, m3))
ok4 = m3 / bare >= 1.2
# drip hand-off: drip at 0.92 vs sprinkler 0.60 for topping up the same 60 mm need
top = {k: round(60 / e, 1) for k, e in (("drip", .92), ("sprinkler", .60))}
print("topup mm", top)
ok5 = top["sprinkler"] / top["drip"] > 1.4
ok = ok1 and ok2 and ok3 and ok4 and ok5
print("checks", ok1, ok2, ok3, ok4, ok5)
print("RESULT: %s garden sizing holds small storms only (clay 75mm %.2f); swale ratio in 8-12x for %s of %s mm storms; mulch carry x%.2f"
      % ("PASS" if ok else "FAIL", res[("clay", 75)], in_band, list(ratios), m3 / bare))
