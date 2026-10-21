"""Swale chain on a hillside: spacing, soil, storm depth, cascading overflow, and a
rain-barrel roof overflow feeding the top swale.
Kernels exercised: GARDEN passive-landscape-water-harvesting (swale 18in x 4ft, >=2 m
spacing, 8-12x infiltration), rain-barrel-sizing (0.623 roof formula feeds the top swale),
brainwork/E115 (swale gain appears only for big storms) and E-rain-barrel sandbox overflow.
Prediction (written before the first run): at 2 m spacing a 5-swale chain absorbs a 100 mm
storm on sand but not on clay; at 6 m spacing even sand spills below the chain at 100 mm;
the swale/flat infiltration ratio is within 8-12x for some storm but falls below 8x at
small storms and the ratio for clay at 100 mm is below 8x; adding 1100 gal of roof overflow
on the top swale makes the chain spill on clay at 50 mm. Constants assumed."""
SWALE_VOL = 0.28     # m3 per m of swale (18 in deep x 4 ft wide, triangular ~ 0.457*1.22/2)
SWALE_BASE_W = 1.0   # m of wetted base that infiltrates, per m of swale
STORM_H = 6.0        # h of storm + ponding
N = 5
RUNOFF = 0.8
SOIL = {"sand": 50.0, "clay": 5.0}   # mm/h infiltration

def chain(depth_mm, spacing, soil, extra_m3=0.0, n=N):
    """per m of swale length. returns (absorbed, spilled below chain)"""
    carry = extra_m3
    absorbed = 0.0
    for _ in range(n):
        inflow = carry + RUNOFF * depth_mm / 1000.0 * spacing
        infil = SOIL[soil] / 1000.0 * STORM_H * SWALE_BASE_W
        cap = SWALE_VOL + infil
        take = min(inflow, cap)
        absorbed += take
        carry = inflow - take
    return absorbed, carry

def flat(depth_mm, spacing, soil, n=N):
    rain = depth_mm / 1000.0 * spacing * n
    soak = min(rain, SOIL[soil] / 1000.0 * STORM_H * spacing * n)   # whole strip infiltrates
    return soak

ok = {}
print("1) absorption by spacing, soil, storm (m3 per m of swale length, spill below chain)")
for soil in SOIL:
    for sp in (2, 4, 6):
        row = []
        for d in (25, 50, 100):
            a, s = chain(d, sp, soil)
            row.append(f"{d}mm abs {a:.2f} spill {s:.2f}")
        print(f"   {soil:4s} {sp} m:", " | ".join(row))
ok["sand2_100"] = chain(100, 2, "sand")[1] < 1e-9
ok["clay2_100"] = chain(100, 2, "clay")[1] > 0   # predicted to fail on clay
ok["sand6_100"] = chain(100, 6, "sand")[1] > 0   # predicted to spill
print("2) swale/flat infiltration ratio (chain absorbed vs flat strip of the same area)")
band = []
ratios = {}
for soil in SOIL:
    for d in (10, 25, 50, 100, 200, 400):
        a, _ = chain(d, 2, soil)
        f = flat(d, 2, soil)
        ratios[(soil, d)] = a / f if f else float("inf")
        print(f"   {soil:4s} {d:3d} mm ratio {ratios[(soil, d)]:.1f}")
        if 8 <= ratios[(soil, d)] <= 12: band.append((soil, d))
print("   ratios inside 8-12x:", band)
ok["band_some"] = len(band) > 0
ok["small_below"] = ratios[("sand", 10)] < 8 or ratios[("clay", 10)] < 8
ok["clay100_below8"] = ratios[("clay", 100)] < 8
# roof overflow: 1000 sq ft roof, 650 gal overflow from the barrel sandbox (= 2.46 m3) over 10 m of swale
roof_m3 = 650 * 0.003785
per_m = roof_m3 / 10.0
a, s = chain(100, 4, "clay", extra_m3=per_m)
a0, s0 = chain(100, 4, "clay")
print(f"3) top swale fed by {roof_m3:.2f} m3 roof overflow over 10 m: clay 100mm 4 m spacing spill {s:.2f} vs {s0:.2f} without")
ok["roof_spills"] = s > s0
# what makes the roof feed safe: how many swales on sand absorb roof + 100 mm?
need = next((n for n in range(1, 40) if chain(100, 4, "clay", extra_m3=per_m, n=n)[1] < 1e-9), None)
print(f"4) clay, 100 mm at 4 m + roof overflow needs a chain of {need} swales (5 in the base case)")
ok["need_found"] = need is not None
print("checks", ok)
allok = all(ok.values())
print(f"RESULT: {'PASS' if allok else 'FAIL'} sand2m100mm spill {chain(100,2,'sand')[1]:.2f}, clay2m100mm spill {chain(100,2,'clay')[1]:.2f}, sand6m100mm spill {chain(100,6,'sand')[1]:.2f}, ratios in 8-12x {band}, roof feed chain needs {need} swales")
