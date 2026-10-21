# Sandbox: a gravity drain needs a minimum fall per foot (common code figure: 1/4 inch per foot for small pipes).
# Total fall = run * slope. Check it against the vertical room available at the far end (ceiling void / joist depth).
def total_fall_in(run_ft, slope_in_per_ft=0.25):
    return run_ft * slope_in_per_ft
def fits(run_ft, room_in, slope=0.25):
    return total_fall_in(run_ft, slope) <= room_in
def max_run(room_in, slope=0.25):
    return room_in / slope
cases = [(8, 9.25), (20, 9.25), (37, 9.25), (38, 9.25), (40, 5.5)]
res = {c: (total_fall_in(c[0]), fits(*c)) for c in cases}
for c, v in res.items(): print("run %sft room %.2fin -> fall %.2fin fits=%s" % (c[0], c[1], v[0], v[1]))
# BREAK: a flatter slope (1/8 in/ft) doubles the max run but is below the stated minimum, so it must be rejected on slope not on fit
flat_ok = fits(70, 9.25, 0.125)
print("1/8 in/ft over 70ft fits geometrically:", flat_ok, "but below the 1/4 minimum -> reject")
ok = (res[(8, 9.25)][1] and res[(20, 9.25)][1] and res[(37, 9.25)][1]
      and not res[(38, 9.25)][1] and not res[(40, 5.5)][1]
      and max_run(9.25) == 37 and flat_ok and 0.125 < 0.25)
print("RESULT: %s max run in a 9.25in joist is %.0fft at 1/4 in/ft; 38ft and any 40ft run in a 5.5in void fail; flatter slope fits but is below minimum" % ("PASS" if ok else "FAIL", max_run(9.25)))
