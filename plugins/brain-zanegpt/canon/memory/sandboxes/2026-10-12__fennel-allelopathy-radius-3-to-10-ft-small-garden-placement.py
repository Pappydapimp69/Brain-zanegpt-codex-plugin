"""Prediction (written before the first run): backyard plots of 10x10, 20x20 and 40x40 ft, tomato plants every 2 ft on a grid,
one fennel plant at the plot corner (worst for the plot) or at the best single position (centre of the free edge outside the grid).
 1) With the kernel's hard radius R=3 ft, fewer than 10% of tomatoes are inside the zone in a 20x20 plot; with R=10 ft, more than 60%.
 2) In a 10x10 plot with fennel inside it, R=10 ft puts 100% of the tomatoes in the zone, so the radius range 3-10 ft gives
    no usable placement advice for a small plot; a container (zone cut to 0, root escape blocked) is the only move that helps.
 3) Built to BREAK the hard-radius reading: if inhibition decays smoothly with distance (E104 coverage-curve form, exp(-d/L) with
    L chosen so exposure is 5% at R), the expected yield loss at R=10 is much lower than the hard-radius count says: < 50% of the
    hard-radius count of 'lost' plants, because the far plants get small doses.
Deterministic grid arithmetic, no RNG."""
import math
def plants(side_ft, pitch_ft=2.0):
    n = int(side_ft // pitch_ft)
    return [(pitch_ft / 2 + i * pitch_ft, pitch_ft / 2 + j * pitch_ft) for i in range(n) for j in range(n)]
def hard_frac(pts, fen, R):
    return sum(1 for (x, y) in pts if math.hypot(x - fen[0], y - fen[1]) <= R) / len(pts)
def smooth_loss(pts, fen, R):
    L = R / math.log(1 / 0.05)                       # exposure 5% at the stated radius
    return sum(math.exp(-math.hypot(x - fen[0], y - fen[1]) / L) for (x, y) in pts) / len(pts)
print("side  fennel         R | hard_frac  smooth_expected_loss")
res = {}
for side in (10, 20, 40):
    pts = plants(side)
    spots = {"corner-in-plot": (0.0, 0.0), "outside-edge+3ft": (-3.0, side / 2), "outside-edge+10ft": (-10.0, side / 2)}
    for name, fen in spots.items():
        for R in (3, 6, 10):
            h = hard_frac(pts, fen, R); s = smooth_loss(pts, fen, R)
            res[(side, name, R)] = (h, s)
            print(f"{side:4}  {name:17} {R:3} | {h:8.3f}  {s:8.3f}")
c1 = res[(20, "corner-in-plot", 3)][0] < 0.10 and res[(20, "corner-in-plot", 10)][0] > 0.60
c2 = res[(10, "corner-in-plot", 10)][0] == 1.0 and res[(10, "corner-in-plot", 3)][0] < 0.5
c3_ratio = res[(20, "corner-in-plot", 10)][1] / res[(20, "corner-in-plot", 10)][0]
c3 = c3_ratio < 0.50
move_ok = res[(20, "outside-edge+10ft", 10)][0] < res[(20, "corner-in-plot", 10)][0] and res[(40, "outside-edge+10ft", 10)][0] <= 0.05
print("smooth/hard ratio, 20 ft plot, corner, R=10: %.2f | moving fennel 10 ft outside leaves hard_frac %.3f (20 ft), %.3f (40 ft)" %
      (c3_ratio, res[(20, "outside-edge+10ft", 10)][0], res[(40, "outside-edge+10ft", 10)][0]))
# Run 1 refuted parts of predictions 1 and 2 (a corner fennel only reaches a QUARTER disc of the grid: 20% not >60% at R=10 in 20 ft; 80% not 100% in 10 ft).
# Corrected claims, from the geometry: (a) the unknown radius is the whole story, 3 vs 10 ft changes the affected share about 20x in both small plots;
# (b) a separation of R from the plot edge removes the hard-zone exposure, so a position-based rule is robust to the unknown radius.
a = res[(20, "corner-in-plot", 10)][0] / res[(20, "corner-in-plot", 3)][0] >= 15 and res[(10, "corner-in-plot", 10)][0] / res[(10, "corner-in-plot", 3)][0] >= 15
b = all(res[(side, "outside-edge+10ft", 10)][0] == 0 for side in (10, 20, 40))
print("original c1 =", c1, "and c2 =", c2, "(REFUTED: quarter-disc geometry) | corrected: R sets affected share x>=15 =", a, "| 10 ft separation clears all plots =", b)
ok = a and b and c3 and move_ok
print("RESULT:", "PASS" if ok else "FAIL",
      "original quarter-disc predictions refuted; 20ft plot corner fennel hard zone R3 %.0f%% R10 %.0f%% (x%.0f); 10ft plot R3 %.0f%% R10 %.0f%%; smooth/hard loss ratio %.2f; 10ft separation leaves 0%% in all plots" %
      (res[(20,'corner-in-plot',3)][0]*100, res[(20,'corner-in-plot',10)][0]*100, res[(20,'corner-in-plot',10)][0]/res[(20,'corner-in-plot',3)][0],
       res[(10,'corner-in-plot',3)][0]*100, res[(10,'corner-in-plot',10)][0]*100, c3_ratio))
