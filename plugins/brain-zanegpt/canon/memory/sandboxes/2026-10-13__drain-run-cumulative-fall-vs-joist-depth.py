# Prediction (before run): a horizontal drain falling 1/4 in per foot drops L/4 inches over L feet. Under a floor
# with a 9.25 in joist bay and 1.5 in of clearance kept above the pipe bottom's lowest point, a 3 in pipe
# (3.5 in outside) starting 1.5 in below the joist top can run at most (9.25-1.5-3.5-... ) feet: the run limit is
# floor((bay - top_gap - outside_dia - bottom_gap)*4) feet. For bay 9.25, top gap 1.5, OD 3.5, bottom gap 0.75 the
# usable fall is 3.5 in so the limit is 14 ft. Splitting the run with a 1/8 in per foot flatter section
# lengthens the limit, and a single 2 ft section at 1/2 in per foot (steeper) shortens it. BREAK: the same
# limit when measured with a straight line from rounded-off 1/4 in per 4 ft marks (a tape marked in 1 in steps)
# is off by up to 1 in = 4 ft.
import math
BAY, TOP, OD, BOT = 9.25, 1.5, 3.5, 0.75
def usable(): return BAY - TOP - OD - BOT
def max_run(slope_in_per_ft): return usable() / slope_in_per_ft
def fall(sections):  # list of (length_ft, in_per_ft)
    return sum(l * s for l, s in sections)
u = usable()
print("S1 usable fall %.2f in; limit at 1/4 in/ft %.1f ft, 1/8 %.1f ft, 1/2 %.1f ft" % (u, max_run(0.25), max_run(0.125), max_run(0.5)))
mixed = [(10, 0.25), (2, 0.5)]
print("S2 10 ft at 1/4 + 2 ft at 1/2: fall %.2f in vs usable %.2f in -> fits %s" % (fall(mixed), u, fall(mixed) <= u))
def marked(l, step=1.0): return math.ceil(l * 0.25 / step) * step   # fall rounded up to whole inches by tape marks
worst = max(marked(l) - l * 0.25 for l in range(1, 41))
lim_marked = max(l for l in range(1, 41) if marked(l) <= u)
print("S3 BREAK tape marked in whole inches: worst overestimate %.2f in, run limit %d ft vs exact %d ft" % (worst, lim_marked, math.floor(max_run(0.25))))
ok = abs(max_run(0.25) - 14.0) < 1e-9 and abs(max_run(0.125) - 28.0) < 1e-9 and fall(mixed) <= u and lim_marked < math.floor(max_run(0.25)) + 1 and worst > 0.5
print("RESULT: %s run limit %.0f ft at 1/4 in/ft (usable fall %.2f in), %.0f ft at 1/8, %.0f ft at 1/2; 10 ft + 2 ft steep fall %.2f in; whole-inch tape marks cut the limit to %d ft with up to %.2f in overestimate"
      % ("PASS" if ok else "FAIL", max_run(0.25), u, max_run(0.125), max_run(0.5), fall(mixed), lim_marked, worst))
