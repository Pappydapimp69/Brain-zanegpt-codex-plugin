# Equilibrium (brine/bag) cure: Cure #1 is 6.25% sodium nitrite. US ingoing limit for bacon-style
# immersion cures: 156 ppm nitrite on GREEN MEAT weight; dose 0.25% of cure #1 on meat weight = 156 ppm.
# Prediction (before run): dosing 0.25% on TOTAL (meat+water) weight gives ppm on meat = 156*(m+w)/m
# -> 195 ppm at w/m=0.25, 234 at 0.5, 312 at 1.0; under-dosing happens if the base is trimmed meat but
# the batch is weighed with the fat cap (BREAK: ppm falls to 156*trim/total).
CURE_NITRITE = 0.0625
def ppm_on_meat(cure_g, meat_g): return cure_g * CURE_NITRITE / meat_g * 1e6
meat = 1000.0
ok = abs(ppm_on_meat(0.0025*meat, meat) - 156.25) < 0.01
over = {}
for ratio in (0.0, 0.25, 0.5, 1.0):
    water = meat*ratio
    dose = 0.0025*(meat+water)           # wrong base: total weight
    over[ratio] = ppm_on_meat(dose, meat)
    print("water/meat %.2f dose %.2f g -> %.1f ppm on meat (limit 156)" % (ratio, dose, over[ratio]))
ok = ok and abs(over[0.25]-195.3)<0.1 and abs(over[0.5]-234.4)<0.1 and abs(over[1.0]-312.5)<0.1
# break case: weigh batch with 20% fat cap trimmed away before curing
trimmed = 800.0
under = ppm_on_meat(0.0025*meat, trimmed)   # dose on untrimmed weight, applied to trimmed meat -> OVER
under2 = ppm_on_meat(0.0025*trimmed, meat)  # dose on trimmed weight, but limit counted on full -> under
print("dose on untrimmed, cure trimmed meat: %.1f ppm; dose on trimmed, report on full: %.1f ppm" % (under, under2))
ok = ok and abs(under-195.3)<0.1 and abs(under2-125.0)<0.1
print("RESULT: %s total-weight base gives %.0f/%.0f/%.0f ppm at water/meat 0.25/0.5/1.0; wrong weighing stage %.0f or %.0f ppm" % ("PASS" if ok else "FAIL", over[0.25], over[0.5], over[1.0], under, under2))
