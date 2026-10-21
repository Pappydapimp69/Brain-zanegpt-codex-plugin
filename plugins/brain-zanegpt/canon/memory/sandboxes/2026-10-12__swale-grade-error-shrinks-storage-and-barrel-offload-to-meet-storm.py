"""Swale level tolerance. A trench L ft long, D ft deep, W ft wide on a grade error g (rise/run).
Water pools at the low end: wedge of length D/g (capped at L). Storage = integral of the wedge.
Storm demand: roof runoff 1000 sq ft x inches x 0.623 gal, minus a rain barrel that takes first Vb gallons.
Deterministic, no RNG; exact numeric integration by slices."""
L, D, W = 30.0, 1.5, 4.0
GAL = 7.48
ROOF = 1000.0

def storage_gal(g, slices=3000):
    tot = 0.0
    for i in range(slices):
        x = (i + 0.5) * L / slices              # distance from low end
        depth = max(0.0, D - g * x)             # water depth at x with the low end full
        tot += depth * W * (L / slices)
    return tot * GAL
def storm_gal(inches): return ROOF * inches * 0.623

level = storage_gal(0.0)
print("level capacity %.0f gal (closed form %.0f)" % (level, L * D * W * GAL))
rows = []
for g in (0.0, 0.01, 0.02, 0.05, 0.10, 0.20):
    s = storage_gal(g); rows.append((g, round(s), round(s / level, 3)))
print("grade, gal, fraction:", rows)
# largest storm swale alone holds at each grade, and with a 55 gal barrel upstream
def max_storm_in(g, barrel=0.0):
    s = storage_gal(g) + barrel
    return s / (ROOF * 0.623)
tab = [(g, round(max_storm_in(g), 2), round(max_storm_in(g, 55), 2)) for g in (0.0, 0.02, 0.05, 0.10)]
print("grade, max storm in (swale), (swale+55gal):", tab)
frac = dict((g, f) for g, _, f in rows)
checks = {
    "level_matches_closed_form": abs(level - L * D * W * GAL) / level < 1e-3,
    "one_pct_costs_under_15pct": frac[0.01] > 0.85,
    "five_pct_halves_it": 0.45 < frac[0.05] < 0.55,
    "twenty_pct_under_15pct_left": frac[0.20] < 0.15,
    "level_swale_holds_2in_storm": max_storm_in(0.0) > 2.0,
    "ten_pct_grade_fails_1in_storm_alone": max_storm_in(0.10) < 1.0,
    "barrel_alone_does_not_rescue_10pct": max_storm_in(0.10, 55) < 1.0,
}
print(checks)
print("RESULT: %s level swale %.0f gal holds %.2f in; 1%% grade keeps %.0f%%, 5%% keeps %.0f%%, 10%% holds only %.2f in even with a 55 gal barrel (%.2f)" % (
    "PASS" if all(checks.values()) else "FAIL", level, max_storm_in(0.0), 100 * frac[0.01], 100 * frac[0.05], max_storm_in(0.10), max_storm_in(0.10, 55)))
