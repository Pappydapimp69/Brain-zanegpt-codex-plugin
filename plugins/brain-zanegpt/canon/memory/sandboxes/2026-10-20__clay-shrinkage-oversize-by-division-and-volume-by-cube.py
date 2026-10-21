# Pottery: throw oversize so the fired piece hits a target. Shrinkage s is a fraction of the WET size.
def fired(wet, s): return wet * (1 - s)
target_mm, s = 200.0, 0.12
naive_wet = target_mm * (1 + s)             # "add 12 percent"
right_wet = target_mm / (1 - s)             # divide by the retained fraction
short_mm = target_mm - fired(naive_wet, s)
print("naive wet %.2f fires to %.2f (short %.2f mm); divide wet %.2f fires to %.2f" % (naive_wet, fired(naive_wet, s), short_mm, right_wet, fired(right_wet, s)))
# volume scales with the cube of the linear retention
target_l = 1.0
naive_clay = target_l * (1 + s)
cube_clay = target_l / (1 - s) ** 3
vol_under = 1 - naive_clay * (1 - s) ** 3 / target_l
print("naive clay %.3f L gives %.3f L (%.1f%% under); cube rule clay %.3f L" % (naive_clay, naive_clay * (1 - s) ** 3, 100 * vol_under, cube_clay))
# two-stage shrink (drying then firing) compounds: not additive
d, f = 0.06, 0.06
comb = 1 - (1 - d) * (1 - f)
print("drying 6 + firing 6 combine to %.4f, not %.2f" % (comb, d + f))
# BREAK: spread of the error over a range of shrinkage rates
errs = {x: target_mm - fired(target_mm * (1 + x), x) for x in (0.08, 0.10, 0.12, 0.14)}
print("naive short by mm at s:", {k: round(v, 2) for k, v in errs.items()})
ok = abs(short_mm - 2.88) < 0.01 and abs(right_wet - 227.27) < 0.01 and abs(fired(right_wet, s) - target_mm) < 1e-9 and 0.23 < vol_under < 0.24 and abs(comb - 0.1164) < 1e-9 and all(v > 0 for v in errs.values())
print("RESULT: %s naive wet %.1f mm fires %.2f mm short; divide gives %.2f mm; naive clay volume %.1f%% under; two-stage 6+6 = %.2f%% not 12%%" % ("PASS" if ok else "FAIL", naive_wet, short_mm, right_wet, 100 * vol_under, 100 * comb))
