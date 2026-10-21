"""Compose: jar-test texture readout (Stokes settling) -> rain-garden divisor (clay /6, sandy /8) -> area and drain time.
Kernels/entries exercised: ideas:GARDEN/cheap-home-soil-diagnostics (sand ~1 min, silt ~3 min, clay 24-48 h),
ideas:GARDEN/passive-landscape-water-harvesting (rain garden = drainage area / 6 clay to / 8 sandy),
2026-10-09__home-soil-jar-test-stokes-timing-and-leaf-triage-order/E1 (silt not down at 3 min; read at ~2 h).
Constants assumed: particle density 2650, 20 C water, 10 cm fill, log-uniform sizes per class, clay floor 0.2 um,
infiltration mm/h sand 50, loam 13, clay 5, 6 in ponding, garden must drain in 48 h, 1000 sq ft drainage area.
Prediction (before run): reading silt at 3 min labels a true loam as clay-heavy (silt read < 15 pts) so it picks divisor 6 over 8;
for a true sandy soil it still picks 8 (sand dominates) - the error is in silt-rich soils; for a true loam divisor 6 gives a
garden 33% larger than divisor 8; loam at 13 mm/h drains 6 in in 11.7 h either way, clay at 5 mm/h in 30.5 h, so size error
costs area not drain time; reading at 2 h corrects the label on every tested true texture."""
import math
G, RHOP, RHOW, MU = 9.81, 2650.0, 998.0, 1.0e-3
def t_settle(d_um, depth=0.10):
    d = d_um * 1e-6
    v = (RHOP - RHOW) * G * d * d / (18 * MU)
    return depth / v      # seconds
def class_bins(lo, hi, n=200):
    return [lo * (hi / lo) ** ((i + .5) / n) for i in range(n)]
SAND, SILT, CLAY = class_bins(50, 2000), class_bins(2, 50), class_bins(0.2, 2)
def readout(true, t_sand=60, t_silt=180, t_clay=48 * 3600):
    """fractions read from settled layers: sand = settled by t_sand; sand+silt settled by t_silt; total by t_clay."""
    s, si, c = true
    sand_set = s * sum(t_settle(d) <= t_sand for d in SAND) / len(SAND)
    silt_set = si * sum(t_settle(d) <= t_silt for d in SILT) / len(SILT)
    clay_set = c * sum(t_settle(d) <= t_clay for d in CLAY) / len(CLAY)
    total = sand_set + silt_set + clay_set + 1e-9
    # layers: bottom sand mark at t_sand, silt mark at t_silt, total at t_clay; read heights as fractions of final deposit
    # sand layer = what settled by t_sand (all sand); silt layer = deposit at t_silt minus sand; clay = rest
    dep_silt_mark = sand_set + silt_set
    dep_total = sand_set + si + clay_set          # final deposit after 48 h
    return (100 * sand_set / dep_total, 100 * (dep_silt_mark - sand_set) / dep_total, 100 * (dep_total - dep_silt_mark) / dep_total)
def klass(r):
    sand, silt, clay = r
    if clay >= 35: return "clay"
    if sand >= 50: return "sandy"
    return "loam"
def divisor(k): return 6 if k == "clay" else 8
INF = {"sandy": 50.0, "loam": 13.0, "clay": 5.0}
def drain_h(k): return 152.4 / INF[k]
TRUE = {"loam": (40, 40, 20), "sandy": (70, 20, 10), "clayey": (20, 30, 50), "silt-loam": (20, 60, 20)}
TRUE_K = {"loam": "loam", "sandy": "sandy", "clayey": "clay", "silt-loam": "loam"}
ok = {}
AREA = 1000.0
print("name        true-class | kernel 3min read -> class div area | 2h read -> class div area")
wrong3 = wrong2h = 0
for n, tr in TRUE.items():
    r3 = readout(tr); r2 = readout(tr, t_silt=2 * 3600)
    k3, k2 = klass(r3), klass(r2)
    wrong3 += k3 != TRUE_K[n]; wrong2h += k2 != TRUE_K[n]
    print(f"  {n:9s} {TRUE_K[n]:5s} | {tuple(round(x) for x in r3)} {k3:5s} /{divisor(k3)} {AREA/divisor(k3):.0f} | {tuple(round(x) for x in r2)} {k2:5s} /{divisor(k2)} {AREA/divisor(k2):.0f}")
ok["loam_mislabel"] = klass(readout(TRUE["loam"])) == "clay" and klass(readout(TRUE["loam"], t_silt=7200)) == "loam"
ok["sandy_ok"] = klass(readout(TRUE["sandy"])) == "sandy"
ok["silt_mislabel"] = klass(readout(TRUE["silt-loam"])) != TRUE_K["silt-loam"]
ok["fix_2h"] = wrong2h == 0
big = AREA / 6 / (AREA / 8) - 1
print(f"divisor 6 vs 8 area difference: {big*100:.0f}%; drain hours loam {drain_h('loam'):.1f}, clay {drain_h('clay'):.1f} (limit 48)")
ok["area33"] = abs(big - 1/3) < 1e-9
ok["drain"] = drain_h("clay") < 48 and drain_h("loam") < drain_h("clay")
print("wrong class: 3-min kernel read", wrong3, "of 4 | 2h read", wrong2h, "of 4")
print("ok:", ok)
print(("RESULT: PASS" if all(ok.values()) else "RESULT: FAIL") + f" 3-min read mislabels {wrong3}/4 textures, 2h read {wrong2h}/4; wrong divisor sizes area {big*100:.0f}% off; drain loam {drain_h('loam'):.1f} h clay {drain_h('clay'):.1f} h")
