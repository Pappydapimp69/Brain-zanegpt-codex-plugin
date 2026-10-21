"""Gap (brain query koschmieder: 0). SEVEN's raycaster fogs linearly:
fog = min(1, dist / FOG_DIST), FOG_DIST = 22 cells (src/view.js, seven-1.18.0,
read not modified), so apparent contrast = 1 - dist/22. Real air attenuates
contrast exponentially, C = C0 exp(-sigma d) (Beer-Lambert), and Koschmieder's
law (1924) defines the visual range as the distance where contrast falls to the
2% threshold: V = -ln(0.02)/sigma = 3.912/sigma.
Exact arithmetic, no rng. Match the two at the same visual range V (where
linear contrast = 0.02: d = 0.98 x 22 = 21.56 cells).
PREDICTION (written before running): at half the visual range linear fog keeps
50% contrast, real fog ~14%; contrast halves within ~4 cells in real fog vs 11
in SEVEN's; near the visual range a linear-fog object fades about 10x faster per
cell than in real fog (pop-in edge); the distance where contrast is above 30%
(clearly readable, assumed) is about 2.5x farther in linear fog.
"""
import math, sys
print("python", sys.version.split()[0])
FOG = 22.0
lin = lambda d: max(0.0, 1 - d / FOG)
V = FOG * (1 - 0.02); sigma = 3.912 / V
ex = lambda d: math.exp(-sigma * d)
print(f"matched visual range {V:.2f} cells, sigma {sigma:.4f}/cell")
for d in (2, 4, 8, 11, 16, 20, 21.5):
    print(f"d {d:5}: linear {lin(d):.3f}  exponential {ex(d):.3f}")
half_l, half_e = FOG * 0.5, math.log(2) / sigma
slope_l = 1 / FOG; slope_e = sigma * ex(V)
read_l = FOG * 0.7; read_e = -math.log(0.3) / sigma
print(f"contrast halves at {half_l:.1f} (linear) vs {half_e:.1f} (real); slope at visual range {slope_l:.4f} vs {slope_e:.4f} per cell (x{slope_l/slope_e:.1f}); >30% contrast to {read_l:.1f} vs {read_e:.1f} cells (x{read_l/read_e:.2f})")
c = [abs(lin(V / 2) - 0.51) < 0.02, abs(ex(V / 2) - 0.141) < 0.01, abs(half_e - 3.8) < 0.3, 8 <= slope_l / slope_e <= 14, 2.2 <= read_l / read_e <= 2.8]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; at half range linear {lin(V/2):.2f} vs real {ex(V/2):.2f}; halves at {half_l:.0f} vs {half_e:.1f} cells; edge fade x{slope_l/slope_e:.1f} faster; readable range x{read_l/read_e:.2f}")
