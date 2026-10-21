"""Gap sandbox: ideas:GARDEN/passive-landscape-water-harvesting gives swale dims (18 in deep x 4 ft wide, spaced >=2 m apart, slopes
<=18-25%) but no UPPER spacing bound. Cross-checks ideas:GARDEN/rain-barrel-sizing (0.623 gal per sqft per inch) for the volume
conversion and brainwork E132 (one 3 in storm overflows a barrel and a roof/6 rain garden alike).
Prediction (before run): trench cross-section ~0.28 m3 per metre (V-shaped, 0.457 m x 1.219 m, half-fill factor 0.5), runoff coefficient 0.5.
Largest overflow-free spacing with zero infiltration: ~11 m at 50 mm, ~5.6 m at 100 mm, ~3.7 m at 150 mm; so the kernel's 2 m minimum
never overflows up to 150 mm, and a 10 m spacing overflows at 100 mm by about 44%. With clay infiltration (5 mm/h x 1 h over 1.2 m width)
the bound moves by under 10%; the 0.623 conversion agrees with the m3 route within 1%. Slope: the level trench's excavated depth on the
uphill edge shrinks the usable depth on a 25% slope across a 1.22 m width by ~0.30 m (BREAK): usable capacity falls by more than 50% there."""
M3_TO_GAL, MM_TO_IN, SQM_TO_SQFT = 264.172, 1 / 25.4, 10.7639
W, DEEP = 1.219, 0.457          # 4 ft x 18 in
RUNOFF = 0.5
def capacity_m3_per_m(slope=0.0):
    # level trench cut into a slope: uphill wall height = DEEP, downhill lip is at grade minus slope*W; usable depth = DEEP - slope*W/2 (mean)
    d = max(DEEP - slope * W / 2.0, 0.0) if slope else DEEP
    if slope and d <= 0: return 0.0
    return 0.5 * W * d
def overflow_frac(spacing_m, storm_mm, ksat_mm_h=0.0, slope=0.0, hours=1.0):
    inflow = spacing_m * (storm_mm / 1000.0) * RUNOFF                # m3 per metre of swale
    sink = capacity_m3_per_m(slope) + W * (ksat_mm_h * hours / 1000.0)
    return max(0.0, inflow - sink) / inflow if inflow else 0.0
def max_spacing(storm_mm, ksat=0.0, slope=0.0):
    lo, hi = 0.1, 200.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if overflow_frac(mid, storm_mm, ksat, slope) > 1e-9: hi = mid
        else: lo = mid
    return lo
cap = capacity_m3_per_m()
print(f"capacity {cap:.3f} m3/m ({cap*M3_TO_GAL:.0f} gal per metre)")
bounds = {s: max_spacing(s) for s in (50, 100, 150)}
for s, b in bounds.items(): print(f"storm {s} mm: max overflow-free spacing {b:.1f} m (no infiltration), clay-infil {max_spacing(s, 5.0):.1f} m")
# conversion cross-check at 10 m spacing, 100 mm, per 1 m of swale
inflow_m3 = 10 * 0.1 * RUNOFF; inflow_gal_kernel = (10 * SQM_TO_SQFT) * (100 * MM_TO_IN) * 0.623 * RUNOFF
conv_err = abs(inflow_m3 * M3_TO_GAL - inflow_gal_kernel) / (inflow_m3 * M3_TO_GAL)
of10 = overflow_frac(10, 100)
print(f"10 m @100 mm overflow {of10*100:.1f}%; 2 m @150 mm overflow {overflow_frac(2,150)*100:.1f}%; conversion error {conv_err*100:.2f}%")
shift = max_spacing(100, 5.0) / bounds[100] - 1
cap25 = capacity_m3_per_m(0.25) / cap
print(f"clay infiltration shifts the 100 mm bound by {shift*100:.1f}%; capacity on a 25% slope = {cap25*100:.0f}% of flat")
# added after the first run (not in the original prediction): the E132 3 in storm
b76 = max_spacing(76.2)
print(f"E132 3 in storm (76.2 mm): swale max overflow-free spacing {b76:.1f} m; 5 m spacing overflow {overflow_frac(5,76.2)*100:.1f}%")
checks = {
 "bounds 11/5.6/3.7": abs(bounds[50] - 11.2) < 0.7 and abs(bounds[100] - 5.6) < 0.4 and abs(bounds[150] - 3.7) < 0.3,
 "2m never overflows <=150mm": overflow_frac(2, 150) == 0,
 "10m@100mm ~44%": abs(of10 - 0.44) < 0.04,
 "infil shift <10%": shift < 0.10,
 "conversion <1%": conv_err < 0.01,
 "25% slope halves capacity": cap25 < 0.5,
 "E132 3 in storm held at 5 m (added post hoc)": overflow_frac(5, 76.2) == 0}
for k, v in checks.items(): print(("ok   " if v else "FAIL ") + k)
print("RESULT:", "PASS" if all(checks.values()) else "FAIL", f"bounds {bounds[50]:.1f}/{bounds[100]:.1f}/{bounds[150]:.1f} m at 50/100/150 mm; 10 m at 100 mm overflows {of10*100:.0f}%; slope 25% keeps {cap25*100:.0f}% of capacity; conv err {conv_err*100:.2f}%; 3 in storm bound {b76:.1f} m")
