# Sandbox: a left-to-right reveal wipe (withheld -> shown) over a 400x240 pixel-art film frame shown on 1920x1080.
# Kernels: tension-as-information-gap (reveal rate is the authored discourse), one-grid-integer-scale-no-mixels
# (integer scale only), film (24 fps; wipe of 1 native column per frame = 400 frames... use 2 native cols/frame = 200 frames).
# Prediction (written before running): largest integer scale that fits is 4 (5 needs 1200 rows > 1080), leaving
# 320 of 1920 columns (16.7%) as bars; at 4.5x the screen edge advance per frame (2 native cols) alternates 9 px only
# when rounding is exact, but individual native-column widths take BOTH values 4 and 5 (about 50/50 each), the wipe's
# per-frame step on screen takes at least 2 distinct values for the 1-col/frame wipe and exactly 1 value at 4x;
# at 4.5x no column-width uniformity: spread 1 px; at 4x spread 0.
def edges(scale, n=400):
    return [round(i * scale) for i in range(n + 1)]
def widths(scale): 
    e = edges(scale); return [b - a for a, b in zip(e, e[1:])]
best = max(s for s in range(1, 10) if 400 * s <= 1920 and 240 * s <= 1080)
print("largest integer scale", best, "bars", 1920 - 400 * best, "px =", round(100 * (1920 - 400 * best) / 1920, 1), "%")
w45, w4 = widths(4.5), widths(4)
print("4.5x widths", {v: w45.count(v) for v in set(w45)}, "; 4x widths", {v: w4.count(v) for v in set(w4)})
def steps(scale, per_frame):
    e = edges(scale); return [e[i + per_frame] - e[i] for i in range(0, 400 - per_frame + 1, per_frame)]
s45_1, s4_1, s45_2 = steps(4.5, 1), steps(4, 1), steps(4.5, 2)
print("1 col/frame step values at 4.5x", sorted(set(s45_1)), "at 4x", sorted(set(s4_1)), "; 2 cols/frame at 4.5x", sorted(set(s45_2)))
ok = (best == 4 and 1920 - 400 * best == 320 and set(w45) == {4, 5} and abs(w45.count(4) - w45.count(5)) <= 2
      and len(set(s45_1)) >= 2 and len(set(s4_1)) == 1 and len(set(s45_2)) == 1)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"integer scale {best} leaves {1920 - 400*best}px bars; 4.5x columns 4/5 px = {w45.count(4)}/{w45.count(5)}; "
      f"1 col/frame wipe steps {sorted(set(s45_1))} at 4.5x vs {sorted(set(s4_1))} at 4x; 2 cols/frame at 4.5x {sorted(set(s45_2))}")
