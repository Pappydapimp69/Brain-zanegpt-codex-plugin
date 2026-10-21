"""Prediction (before first run): a contour swale (18 in = 0.457 m deep, 4 ft = 1.22 m wide, kernel dimensions) with a grade g along its trench floor
holds water only as a wedge pooled at the low end. Numerically stepping the floor and a flat water surface (no formula) should give, for a 30 m trench:
 g=0: 100% of the level capacity; g=0.5%: ~84%; g=1%: ~67%; g=2%: ~34%; g>=1.5% leaves the upper half of the trench dry (water reaches only d/g = 30 m at 1.5%, 15 m at 3%).
So for the 8-12x infiltration gain the 'level' requirement is a tolerance of well under 1 percent. Then chain with storm size: contributing strip 6 m wide, 0.5 runoff coefficient (assumed),
rain-barrel constant 0.623 gal per sq ft per inch for gallons: a 50 mm storm sends ~ (6*30 m2 *0.05 m *0.5)=4.5 m3 = 1190 gal; level capacity 30*0.557 m2=16.7 m3 (4400 gal); at 2% grade capacity ~5.7 m3 still above 4.5.
BREAK: at 2% grade a 100 mm storm (9 m3) should overflow while the level swale takes it; the tolerance matters only when storm volume nears the wedge capacity."""
D, W = 0.457, 1.22
SQFT_PER_M2 = 10.7639; GAL_PER_SQFT_IN = 0.623
def stored(L, g, n=3000):
    """volume (m3) holding a flat water surface in a trench whose floor drops g per metre along its length (floor depth at the low end = D)"""
    dx = L / n; vol = 0.0
    for i in range(n):
        x = (i + 0.5) * dx
        depth_here = D - g * (L - x)      # trench floor at x relative to the water surface set by the low-end rim
        if depth_here > 0: vol += depth_here * W * dx
    return vol
L = 30.0
full = stored(L, 0.0)
fr = {g: stored(L, g) / full for g in (0.0, 0.005, 0.01, 0.02, 0.03)}
print("capacity fraction by grade (30 m):", {k: round(v, 3) for k, v in fr.items()}, "full m3", round(full, 2))
dry = {g: max(0.0, L - D / g) for g in (0.015, 0.03)}
print("dry length at 1.5% and 3%:", dry)
def storm(mm, strip=6.0, c=0.5):
    m3 = strip * L * (mm / 1000) * c
    gal = strip * L * SQFT_PER_M2 * (mm / 25.4) * c * GAL_PER_SQFT_IN
    return m3, gal
for mm in (25, 50, 100):
    m3, gal = storm(mm)
    row = {g: ("holds" if stored(L, g) >= m3 else "overflows") for g in (0.0, 0.01, 0.02, 0.03)}
    print(f"storm {mm} mm: runoff {m3:.2f} m3 = {gal:.0f} gal (check {m3*264.172:.0f}); {row}")
m3_50, _ = storm(50); m3_100, _ = storm(100)
ok = (abs(fr[0.005] - 0.84) < 0.04 and abs(fr[0.01] - 0.67) < 0.04 and abs(fr[0.02] - 0.34) < 0.05 and stored(L, 0.02) > m3_50
      and stored(L, 0.02) < m3_100 < stored(L, 0.0) and abs(dry[0.015]) < 1e-6 and dry[0.03] > 14)
print("RESULT:", "PASS" if ok else "FAIL",
      f"capacity vs grade 0.5% {fr[0.005]:.2f} 1% {fr[0.01]:.2f} 2% {fr[0.02]:.2f} 3% {fr[0.03]:.2f}; 100 mm storm {m3_100:.1f} m3 overflows the 2% swale ({stored(L,0.02):.1f}) but not the level one ({full:.1f})")
