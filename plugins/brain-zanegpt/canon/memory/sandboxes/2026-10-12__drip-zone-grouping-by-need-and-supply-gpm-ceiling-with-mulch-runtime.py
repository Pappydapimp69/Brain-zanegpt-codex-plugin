"""Toy drip zoning model. Plants have weekly needs; one valve = one run time for everything on it.
Compare 1 mixed zone vs zones grouped by need, check the supply-GPM ceiling on emitters per zone,
and see how mulch (run time x0.58, assumed from the 42 percent run-time cut) changes zone counts.
Deterministic, no RNG."""
SUPPLY_GPH = 4.0 * 60          # spigot supply 4 gpm assumed
PLANTS = [  # (name, count, weekly need gal per plant, emitters per plant, emitter gph)
    ("lettuce", 20, 1.0, 1, 0.5),
    ("tomato", 10, 7.0, 2, 1.0),
    ("fruit_tree", 3, 35.0, 4, 2.0),
]
def per_plant_delivery(hours, em, gph): return hours * em * gph
def mismatch(zones, mulch=1.0):
    """zones: list of lists of plant indices. Run time per zone = mean need/(mean flow) (one compromise value)."""
    worst, total_gph = 0.0, []
    for z in zones:
        needs = [PLANTS[i][2] * mulch for i in z]
        flows = [PLANTS[i][3] * PLANTS[i][4] for i in z]
        hours = sum(needs) / sum(flows)          # compromise: total need over total flow, per plant weighted equally
        for i in z:
            got = per_plant_delivery(hours, PLANTS[i][3], PLANTS[i][4])
            worst = max(worst, abs(got - PLANTS[i][2] * mulch) / (PLANTS[i][2] * mulch))
        total_gph.append(sum(PLANTS[i][1] * PLANTS[i][3] * PLANTS[i][4] for i in z))
    return worst, total_gph
one = mismatch([[0, 1, 2]])
three = mismatch([[0], [1], [2]])
print("single zone worst mismatch %.2f, zone gph %s" % (one[0], [round(x, 1) for x in one[1]]))
print("grouped worst mismatch %.2f, zone gph %s" % (three[0], [round(x, 1) for x in three[1]]))
# GPH ceiling: does each zone fit the 240 gph supply?
fit_single = one[1][0] <= SUPPLY_GPH
fit_grouped = all(g <= SUPPLY_GPH for g in three[1])
# scale up: 60 lettuce -> zone flow rises; find the lettuce count where a zone breaks the supply
n_break = next(n for n in range(1, 2000) if n * 0.5 > SUPPLY_GPH)
# mulch: grouped mismatch unchanged (scale-free), but hours per zone scale 0.58
hours = lambda m: [sum(PLANTS[i][2] * m for i in z) / sum(PLANTS[i][3] * PLANTS[i][4] for i in z) for z in ([0], [1], [2])]
h_bare, h_mulch = hours(1.0), hours(0.58)
sched_bare, sched_mulch = sum(h_bare), sum(h_mulch)
# weekly watering window of 7 days x 1 h per zone? sequential zones total hours needed
print("break at %d lettuce emitters; hours/zone bare %s mulch %s; total %.1f vs %.1f h" % (n_break, [round(h, 1) for h in h_bare], [round(h, 1) for h in h_mulch], sched_bare, sched_mulch))
mism_mulch = mismatch([[0], [1], [2]], 0.58)[0]
checks = {
    "single_zone_mismatch_over_50pct": one[0] > 0.5,
    "grouped_exact": three[0] < 1e-9,
    "supply_fits_both_at_base": fit_single and fit_grouped,
    "ceiling_breaks_at_481_lettuce_emitters": n_break == 481,
    "mulch_cuts_total_runtime_42pct": abs(1 - sched_mulch / sched_bare - 0.42) < 1e-9,
    "mulch_keeps_grouping_exact": mism_mulch < 1e-9,
}
print(checks)
print("RESULT: %s single-zone worst mismatch %.0f%% vs grouped 0%%; supply ceiling at %d emitters of 0.5 gph; mulch total run %.1f -> %.1f h" % ("PASS" if all(checks.values()) else "FAIL", one[0] * 100, n_break, sched_bare, sched_mulch))
