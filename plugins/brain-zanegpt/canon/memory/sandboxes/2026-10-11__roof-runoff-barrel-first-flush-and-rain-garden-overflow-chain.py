"""Deterministic chain: roof -> first-flush diverter -> barrel -> overflow -> rain garden.
Roof 1000 sq ft. Gross gal = area*inches*0.623 (kernel). Gutter loss 10% (kernel haircut).
Diverter discards FF gal per storm event (dirty-roof 2 mm = 0.0787 in => ~49 gal; clean 0.5 L/m2 => ~13 gal).
Barrel capacity CAP gal, emptied between events (used for irrigation) -> isolates per-event capture.
Overflow (gutter-netted water above CAP) goes to a rain garden: area = roof/6 sq ft, 6 in ponding,
1 in/hr infiltration over a 2 h storm (assumed constants). Storms in inches, fixed list."""
ROOF = 1000.0; K = 0.623
FF = {"clean": 0.5 * ROOF * 0.092903 / 3.785, "dirty": 0.0787402 * ROOF * K}
def event(inches, ff, cap, garden_div=6.0):
    gross = ROOF * inches * K
    net = gross * 0.9                       # gutter loss
    after_ff = max(0.0, net - ff)           # diverter eats first flush
    stored = min(after_ff, cap)
    over = after_ff - stored                # barrel full -> overflow path
    # rain garden receives overflow PLUS the diverted first flush if plumbed to it
    g_area = ROOF / garden_div
    g_cap_gal = (g_area * 0.5 + g_area * (1.0 * 2 / 12)) * 7.48052
    to_garden = over + ff * (1 if net > ff else net / ff if ff else 0)
    absorbed = min(to_garden, g_cap_gal)
    return gross, stored, over, absorbed, to_garden - absorbed, g_cap_gal
storms = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 2.95]
res = {}
print("inches  gross   net_stored(dirty,cap55)  stored/gross  garden_gal  escaped_gal")
for s in storms:
    g, st, ov, ab, esc, gc = event(s, FF["dirty"], 55)
    res[s] = (g, st, ov, ab, esc)
    print(f"{s:5.2f} {g:7.1f} {st:8.1f} {st/g if g else 0:12.3f} {ab:10.1f} {esc:10.1f}")
print("FF clean/dirty gal:", round(FF["clean"], 1), round(FF["dirty"], 1))
# S1 kernel formula: 1 in on 1000 sq ft ~ 623 gross
s1 = abs(res[1.0][0] - 623) < 1
# S2 10% haircut is realistic only above the diverter: net-vs-gross ratio at 1 in, dirty roof, big barrel
g, st, *_ = event(1.0, FF["dirty"], 1e9)
ratio_1in = st / g
g, st, *_ = event(0.1, FF["dirty"], 1e9)
ratio_01in = st / g
# S3 small-storm capture is zero for dirty-roof diverter below this depth
dead_in = FF["dirty"] / (ROOF * K * 0.9)
# S4 garden catches a 2.95 in (75 mm) storm only partly
frac_75 = res[2.95][3] / (res[2.95][3] + res[2.95][4]) if res[2.95][3] + res[2.95][4] else 1
frac_25mm = None
g, st, ov, ab, esc, gc = event(0.984, FF["dirty"], 55)
frac_25 = ab / (ab + esc) if ab + esc else 1
print(f"S2 stored/gross 1in={ratio_1in:.3f} 0.1in={ratio_01in:.3f}; S3 dead depth={dead_in:.3f} in; "
      f"S4 garden share 25mm={frac_25:.2f} 75mm={frac_75:.2f}")
ok = (s1 and 0.85 < ratio_1in < 0.9 and ratio_01in < 0.5
      and 0.07 < dead_in < 0.10 and frac_25 == 1.0 and frac_75 < 0.95)
print("RESULT:", "PASS" if ok else "FAIL",
      f"formula 623 gal/in ok; haircut 10% is {1-ratio_1in:.0%} at 1 in but {1-ratio_01in:.0%} at 0.1 in (dirty diverter); "
      f"no capture below {dead_in:.2f} in; rain garden /6 takes {frac_25:.0%} of 25 mm and {frac_75:.0%} of 75 mm")
