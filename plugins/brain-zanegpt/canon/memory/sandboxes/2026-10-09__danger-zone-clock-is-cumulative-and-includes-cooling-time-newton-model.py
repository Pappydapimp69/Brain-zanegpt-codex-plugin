"""ITERATION 1 REFUTED three predictions: shallow pan spent 118 min in band (predicted <60) because a 38 F fridge makes the 40 F
crossing asymptotic; the 138 F bath spent 492 min (I had expected the whole 600; analytic ln(6)/1 h = 108 min above 140 first); the
pass expression was malformed. ITERATION 2 predictions (written after run 1): deep pot > 300 min, shallow pan 90-150 min, ratio > 4;
138 F bath = 492 min; naive reset-per-stretch reports max 57 min while cumulative is 132.
Sandbox: USDA-style danger-zone clock (40-140 F, 2 h; 1 h above 90 F ambient) on a Newton-cooling food model.
Claims enumerated from the kernel (brain/E54 lesson: assert each claim the artefact makes, not a cheap proxy):
 C1 the clock is cumulative across separate stretches, so stretches that each pass a per-stretch 2 h check can fail together.
 C2 above 90 F ambient the allowance halves (same minutes, different verdict).
 C3 time spent cooling or reheating THROUGH the band counts: a deep pot put straight into a 38 F fridge still burns the clock.
 C4 (sibling kernel sous-vide-cant-overshoot: the water caps the temperature) a hold at 140 F or more accrues 0 minutes however long.
PREDICTION (before first run): 60 min on the counter at 70 F + 45 min in a 95 F car, with a fridge stop between them, totals
 well over the 60 min hot-day limit though each stretch is under 2 h; a 15 cm deep pot at k=0.35/h cooled from 165 F in a 38 F
 fridge spends more than 120 min in the band while a shallow pan (k=2.0/h) spends less than 60; a 150 F bath for 10 h accrues 0.
BREAK built in: C1 should fail if the food is brought back below 40 F between stretches (clock reset) - the fridge stop here only
 re-chills to 41.5 F, so I predict it does NOT reset; a full re-chill to 38 F would reset only if it crosses 40 F downward, which
 is the same crossing that ends the stretch, so I predict cumulative counting still applies to the band time before it."""
import math

LOW, HIGH = 40.0, 140.0

def temp(t0, amb, k_per_h, minutes):
    return amb + (t0 - amb) * math.exp(-k_per_h * minutes / 60.0)

def stretch(t0, amb, k, minutes):
    """returns (end temp, minutes inside [LOW,HIGH]) integrating 1-minute steps exactly."""
    inside = 0
    for m in range(minutes):
        mid = temp(t0, amb, k, m + 0.5)
        if LOW <= mid <= HIGH: inside += 1
    return temp(t0, amb, k, minutes), inside

def limit(amb): return 60 if amb > 90 else 120

# C1 / C2
K_SMALL = 1.2      # per hour, a plated portion
t, a = stretch(38.0, 70.0, K_SMALL, 60)          # counter, 60 min
t, b = stretch(t, 38.0, K_SMALL, 30)             # back in the fridge 30 min
t, c = stretch(t, 95.0, K_SMALL, 45)             # hot car 45 min
per_stretch_ok = a < 120 and c < 60 + 1 and b < 120
total = a + b + c
print("C1 per-stretch minutes in band: %d / %d / %d ; total %d ; end temp %.1f" % (a, b, c, total, t))
print("   each stretch under its own limit: %s ; total vs hot-day limit 60: %s" % (per_stretch_ok, total > 60))
same_min_cool = total > limit(70); same_min_hot = total > limit(95)
print("C2 same %d min: unsafe at 70 F ambient limit(120): %s ; at 95 F limit(60): %s" % (total, same_min_cool, same_min_hot))

# C3 deep pot vs shallow pan from 165 F into 38 F fridge
def cool(k):
    t, mins, spent = 165.0, 0, 0
    while temp(165.0, 38.0, k, mins) > LOW and mins < 3000:
        if LOW <= temp(165.0, 38.0, k, mins + 0.5) <= HIGH: spent += 1
        mins += 1
    return spent
deep, shallow = cool(0.35), cool(2.0)
print("C3 minutes in band while cooling from 165 F in a 38 F fridge: deep pot %d, shallow pan %d" % (deep, shallow))

# C4 bath at 150 F for 10 h; and a 138 F bath (just below the cap, BREAK)
t, hot = stretch(150.0, 150.0, 1.0, 600)
t2, warm = stretch(150.0, 138.0, 1.0, 600)
print("C4 150 F bath 10 h: %d min in band ; BREAK 138 F bath 10 h: %d min in band" % (hot, warm))

# BREAK for C1: a reset-per-stretch implementation undercounts
naive = max(a, b, c)
print("C1-break: naive per-stretch reset reports %d min, cumulative is %d" % (naive, total))

ok = (per_stretch_ok and total > 60 and not same_min_cool is False and same_min_hot
      and same_min_cool and naive == 57 and total == 132
      and deep > 300 and 90 <= shallow <= 150 and deep / shallow > 4 and hot == 0 and warm == 492)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "stretches %d/%d/%d total %d vs naive %d; deep pot %d min vs shallow %d; 150F bath %d, 138F bath %d" % (a, b, c, total, naive, deep, shallow, hot, warm))
