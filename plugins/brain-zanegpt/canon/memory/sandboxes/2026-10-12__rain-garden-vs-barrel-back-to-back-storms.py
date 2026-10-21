# Deterministic hourly model: does a rain garden (roof/6 clay, roof/8 sand) "sink" water better than a
# 55 gal barrel when storms arrive back to back? Only drain-down between storms refills capacity.
GAL_PER_SQFT_IN = 0.623          # rain-barrel kernel constant
ROOF = 1000.0                    # sqft
POND_IN = 6.0                    # ponding depth in garden
def run(storms, soil, barrel_draw_gal_hr):
    area = ROOF / (6 if soil == "clay" else 8)
    infil = 0.1 if soil == "clay" else 2.0       # in/hr, assumed
    garden_cap = area * POND_IN / 12 * 7.48      # gal
    barrel_cap = 55.0
    g = b = 0.0; ov_g = ov_b = 0.0; total = 0.0
    horizon = max(h for h, _ in storms) + 200
    rain = {h: i for h, i in storms}
    for h in range(horizon):
        inflow = rain.get(h, 0.0) * ROOF * GAL_PER_SQFT_IN   # 1-hour burst
        total += inflow
        # barrel
        b += inflow; ex = max(0, b - barrel_cap); ov_b += ex; b -= ex
        b = max(0.0, b - barrel_draw_gal_hr)
        # garden: infiltrate out of pond first (bottom area * rate)
        g += inflow; ex = max(0, g - garden_cap); ov_g += ex; g -= ex
        g = max(0.0, g - area * infil / 12 * 7.48)
    return total, ov_g, ov_b, garden_cap
def pct(a, t): return 100 * a / t if t else 0
S = {"one 1in": [(0, 1.0)], "3x1in gap 1h": [(0,1.0),(1,1.0),(2,1.0)],
     "3x1in gap 48h": [(0,1.0),(48,1.0),(96,1.0)]}
res = {}
for name, st in S.items():
    for soil in ("clay", "sand"):
        t, og, ob, cap = run(st, soil, 0.5)
        res[(name, soil)] = pct(og, t)
        print(f"{name:14s} {soil}: cap {cap:.0f} gal, garden overflow {pct(og,t):.1f}%, barrel(55gal,0.5gph) overflow {pct(ob,t):.1f}%")
# prediction: clay garden overflows ~0% on single 1in, but >=50% on tight 3x1in; spaced 48h clay recovers partially; sand ~0 everywhere
ok = (res[("one 1in","clay")] < 5 and res[("3x1in gap 1h","clay")] > 40 and res[("3x1in gap 48h","clay")] < res[("3x1in gap 1h","clay")] and res[("3x1in gap 1h","sand")] < 5)
print("RESULT:", "PASS" if ok else "FAIL", f"clay overflow single {res[('one 1in','clay')]:.1f}% tight {res[('3x1in gap 1h','clay')]:.1f}% spaced48 {res[('3x1in gap 48h','clay')]:.1f}% sand tight {res[('3x1in gap 1h','sand')]:.1f}%")
