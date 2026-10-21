"""Toy model: required stem clearance vs mulch depth, emitter offset, and water saving.
Assumed constants: wet-pulse wicking length in mulch lam = LAM_PER_IN * depth (in);
stem is 'wet' on a day if emitter-fed wetness at the stem exceeds THRESH, with
wetness = exp(-gap/lam) where gap = max(clearance, 0) + emitter offset from stem ring.
Evaporation saving = 1 - exp(-K*depth) (saturating). Deterministic, no RNG."""
import math
LAM_PER_IN = 0.45
THRESH = 0.10
K = 0.55
DAYS = 120
IRRIG = [d % 2 == 0 for d in range(DAYS)]  # drip every 2nd day, fixed

def stem_wet_days(depth, clearance, offset):
    lam = LAM_PER_IN * depth
    gap = clearance + offset
    w = math.exp(-gap / lam) if lam > 0 else 0.0
    return sum(1 for d in range(DAYS) if IRRIG[d] and w > THRESH)

def min_clearance(depth, offset):
    for c10 in range(0, 121):
        c = c10 / 10
        if stem_wet_days(depth, c, offset) == 0:
            return c
    return None

def saving(depth):
    return 1 - math.exp(-K * depth)

print("depth_in  min_clear(offset0)  min_clear(offset4)  saving%")
res = {}
for depth in (1, 2, 3, 4, 6, 8):
    a, b = min_clearance(depth, 0), min_clearance(depth, 4)
    res[depth] = (a, b)
    print(depth, a, b, round(100 * saving(depth), 1))

# checks
ok = True
# 1) kernel's 2-4 in band is enough at 2-4 in depth with emitter at stem edge
band_ok = all(res[d][0] <= 4 for d in (2, 3, 4))
# 2) 3 in clearance is NOT enough at 8 in depth (built to BREAK the fixed band)
break_ok = res[8][0] > 3
# 3) a 4 in emitter offset removes the need at 3 in depth with zero clearance
off_ok = res[3][1] == 0.0
# 4) saving flattens: gain 4->8 in smaller than 1->2 in
flat_ok = saving(8) - saving(4) < saving(2) - saving(1)
# 5) required clearance monotone increasing in depth
mono_ok = all(res[a][0] <= res[b][0] for a, b in ((1, 2), (2, 3), (3, 4), (4, 6), (6, 8)))
print(band_ok, break_ok, off_ok, flat_ok, mono_ok)
status = "PASS" if all((band_ok, break_ok, off_ok, flat_ok, mono_ok)) else "FAIL"
print(f"RESULT: {status} min clearance by depth(offset0) {[(d, res[d][0]) for d in res]}; offset4 3in={res[3][1]}; saving 4in={saving(4):.2f} 8in={saving(8):.2f}")
