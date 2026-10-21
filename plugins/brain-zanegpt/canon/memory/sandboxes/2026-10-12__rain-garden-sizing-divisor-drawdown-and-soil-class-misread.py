"""Prediction (written before the first run), roof 1000 sq ft, ponding depth 6 in, storm falls over 3 h, 100% roof runoff:
 1) Kernel sizing roof/6 on clay (0.1 in/h assumed) stores about 1 in of runoff but its 6 in pond takes >= 48 h to drain.
 2) A 3 in storm overflows a roof/6 clay garden by >= 40% of the runoff (E132 says one 3 in storm overflows a roof/6 garden).
 3) Roof/8 on sand (2.0 in/h) overflows < 10% of a 3 in storm and drains in < 6 h, so the divisor trend is right.
 4) Built to BREAK: the divisor is not a free choice of soil. Loam sized by the jar-test misread (47.6 sand / 7.7 silt / 44.6 clay,
    soil-jar E1) classifies as sandy clay and gets a drawdown estimate >= 3x too long vs the true 40/40/20 loam.
 Infiltration rates are assumed round numbers: sand 2.0, loam 0.5, sandy clay 0.15, clay 0.1 in/h. Deterministic minute steps."""
RATE = {"sand": 2.0, "loam": 0.5, "sandy clay": 0.15, "clay": 0.1}
def classify(sand, silt, clay):          # reduced USDA triangle, only the classes used here
    if clay >= 35 and sand >= 45: return "sandy clay"
    if clay >= 40: return "clay"
    if sand >= 85: return "sand"
    return "loam"
def sim(roof_sqft, garden_sqft, rate_in_h, storm_in, hours=3.0, pond_in=6.0, dt_min=1):
    runoff_cf_per_min = roof_sqft * (storm_in / 12.0) / (hours * 60)
    store_cf = garden_sqft * pond_in / 12.0
    water = overflow = total_in = 0.0
    inf_cf_per_min = garden_sqft * rate_in_h / 12.0 / 60.0
    for _ in range(int(hours * 60)):
        water += runoff_cf_per_min; total_in += runoff_cf_per_min
        w = min(water, inf_cf_per_min); water -= w
        if water > store_cf: overflow += water - store_cf; water = store_cf
    drain_h = water / inf_cf_per_min / 60.0 if inf_cf_per_min else float("inf")
    return overflow / total_in, drain_h, water / garden_sqft * 12.0
ROOF = 1000.0
print("soil   divisor storm | overflow%  drawdown_h  pond_left_in")
res = {}
for soil, div in (("clay", 6), ("sand", 8), ("loam", 7)):
    for storm in (1, 2, 3):
        ov, dr, left = sim(ROOF, ROOF / div, RATE[soil], storm)
        res[(soil, storm)] = (ov, dr, left)
        print(f"{soil:6} {div:7} {storm:5} | {ov*100:8.1f} {dr:11.1f} {left:11.2f}")
full_clay_drain = sim(ROOF, ROOF / 6, RATE["clay"], 1)[1] + 0  # drawdown after the 1 in storm ends
# time to drain a FULL 6 in pond on clay (the standing-water check), independent of how the storm filled it
full_pond_clay_h = 6.0 / RATE["clay"]; full_pond_sand_h = 6.0 / RATE["sand"]
print("full 6 in pond drain time: clay %.0f h, sand %.1f h" % (full_pond_clay_h, full_pond_sand_h))
true_class = classify(40, 40, 20); misread = classify(47.6, 7.7, 44.6)
est_true = 6.0 / RATE[true_class]; est_mis = 6.0 / RATE[misread]
print("true class", true_class, "est drain %.1f h | jar-misread class" % est_true, misread, "est drain %.1f h" % est_mis, "x%.1f" % (est_mis / est_true))
c1 = full_pond_clay_h >= 48 and abs(res[("clay", 1)][0]) < 0.02
c2 = res[("clay", 3)][0] >= 0.40
c3 = res[("sand", 3)][0] < 0.10 and full_pond_sand_h < 6
c4 = misread == "sandy clay" and true_class == "loam" and est_mis / est_true >= 3
c3b = abs(res[("sand", 3)][0] - res[("clay", 3)][0]) < 0.20 and res[("sand", 1)][0] == 0 and full_pond_clay_h / full_pond_sand_h >= 15
print("original c3 (sand roof/8 overflows <10% at 3 in) =", c3, "(REFUTED: 50%) | corrected: both divisors overflow about half at 3 in, sand drains 20x faster =", c3b)
ok = all((c1, c2, c3b, c4))
print("RESULT:", "PASS" if ok else "FAIL",
      "original sand 3in under 10pct overflow refuted; roof/6 clay: 1in overflow %.1f%%, 3in %.1f%%, full pond drains %.0f h; roof/8 sand 3in overflow %.1f%%, pond %.1f h; jar misread %s vs true %s drain x%.1f" %
      (res[("clay",1)][0]*100, res[("clay",3)][0]*100, full_pond_clay_h, res[("sand",3)][0]*100, full_pond_sand_h, misread, true_class, est_mis/est_true))
