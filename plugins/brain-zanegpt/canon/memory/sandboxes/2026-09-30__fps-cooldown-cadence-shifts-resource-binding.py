# Deterministic sandbox: kernel-determinism#E4 (reset-to-STEP cooldown is fps dependent) x dbz-combat#E4 (cost must bind).
# PREDICTION (before run): STEP=108 ms, 60 s window, pool 500, cost 1 per fire, fire whenever ready.
# Fires ~450/515/540 at 30/60/144 fps (E4), so denied wants = 0 / ~15 / ~40 and binding rate
# 0.000 / ~0.029 / ~0.074: the SAME cost binds at 60 and 144 fps but never at 30 fps.
# A carry-overshoot while-loop cooldown should give equal fires (~555) and equal binding rate at all fps.
from fractions import Fraction as F
import math

def fires_reset(fps, window_ms=60000, step=108):
    dt = F(1000, fps); cd = F(0); t = F(0); n = 0
    while t < window_ms:
        cd -= dt
        if cd <= 0:
            n += 1; cd = F(step)
        t += dt
    return n

def fires_carry(fps, window_ms=60000, step=108):
    dt = F(1000, fps); cd = F(0); t = F(0); n = 0
    while t < window_ms:
        cd -= dt
        while cd <= 0:
            n += 1; cd += step
        t += dt
    return n

def rate(fires, pool=500):
    return max(0, fires - pool) / fires

fps_list = (30, 60, 144)
r = [fires_reset(f) for f in fps_list]
c = [fires_carry(f) for f in fps_list]
rr = [round(rate(x), 3) for x in r]
cr = [round(rate(x), 3) for x in c]
print("reset fires", r, "rate", rr)
print("carry fires", c, "rate", cr)
assert abs(r[0] - 450) <= 1 and abs(r[1] - 515) <= 2 and abs(r[2] - 540) <= 2
assert rr[0] == 0.0 and rr[1] > 0 and rr[2] > rr[1]
assert max(c) - min(c) <= 2   # breaker: carry cooldown removes fps dependence
ok = rr[0] == 0.0 and rr[2] > rr[1] > 0 and max(cr) - min(cr) < 0.02
print("RESULT:", "PASS" if ok else "FAIL", "reset rate", rr, "carry rate", cr)
