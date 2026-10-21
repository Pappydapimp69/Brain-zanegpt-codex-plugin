# Sandbox: ladder 4-to-1 rule (base 1 unit out per 4 units of working height) and reach.
import math
def base_out_ft(height_ft): return height_ft / 4.0
def angle_deg(height_ft): return math.degrees(math.atan2(height_ft, base_out_ft(height_ft)))
def min_ladder_ft(height_ft, overlap_ft=3.0):
    # ladder length along the slope must reach the support height plus 3 ft above the landing for a handhold
    h = height_ft + overlap_ft
    return math.hypot(h, base_out_ft(height_ft))
# angle is independent of height: the rule is a fixed 75.5 degree setting
angles = {h: round(angle_deg(h), 2) for h in (8, 12, 16, 20)}
print("angles", angles)
for h in (8, 12, 16, 20): print("height %dft base out %.1fft min ladder %.2fft" % (h, base_out_ft(h), min_ladder_ft(h)))
# BREAK: a ladder that is too short at the standard stock size: 16 ft stock cannot serve a 14 ft landing with the 3 ft extension
stock = 16
fits = {h: min_ladder_ft(h) <= stock for h in (8, 12, 13, 14, 16)}
print("fits 16ft stock:", fits)
max_h = max(h for h in range(1, 40) if min_ladder_ft(h) <= stock)
ok = len(set(angles.values())) == 1 and abs(angles[8] - 75.96) < 0.1 and not fits[16] and fits[12] and max_h == 12 or max_h >= 12
ok = len(set(angles.values())) == 1 and angles[8] == 75.96 and fits[12] and not fits[16]
print("RESULT: %s 4-to-1 is a fixed %.2f degree angle at every height; a 16ft ladder serves a landing up to %dft with a 3ft extension, not 16ft" % ("PASS" if ok else "FAIL", angles[8], max_h))
