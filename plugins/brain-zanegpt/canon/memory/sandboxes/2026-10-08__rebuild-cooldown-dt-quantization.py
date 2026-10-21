"""Rebuild sandbox: `cd -= dt; if cd <= 0: fire; cd = STEP` frame-rate fairness. Exact Fractions, no RNG/timing.
PREDICTION (before running): count over a 60 s hold at STEP=108 ms = floor(frames/ceil(STEP/dt)) (+1 if first
frame fires): 30fps ~450, 60fps ~514-515, 144fps ~540, ideal 555.6; at 8fps the `if` carry version = 480 (one
per frame cap) while the `while` carry version = ~555; relative 144-vs-30 gap ~16.7% at 30 s and 60 s holds,
absolute gap doubles with hold; a different STEP (250 ms) and fps (20, 90, 120) obey the same formula within +-1."""
from fractions import Fraction as F
import math

def run(fps, step, hold_ms, mode="plain"):
    dt = F(1000, fps); cd = F(0); n = 0; t = F(0)
    while t < hold_ms:
        t += dt; cd -= dt
        if mode == "plain":
            if cd <= 0: n += 1; cd = F(step)
        elif mode == "carry_if":
            if cd <= 0: n += 1; cd += step
        else:  # carry_while
            while cd <= 0: n += 1; cd += step
    return n

def formula(fps, step, hold_ms):
    dt = F(1000, fps); k = math.ceil(F(step) / dt)
    return float(F(hold_ms) / (k * dt))

fails = []
for fps, want in ((30, 450), (60, 515), (144, 540)):
    n = run(fps, 108, 60000); f = formula(fps, 108, 60000)
    print(f"S1 fps {fps}: sim {n} formula {f:.1f} claim {want}")
    if abs(n - want) > 1 or abs(n - f) > 1.5: fails.append(f"S1-{fps}")
for fps in (20, 90, 120):                       # my own fps values
    for step in (108, 250):
        n = run(fps, step, 60000); f = formula(fps, step, 60000)
        print(f"S2 fps {fps} step {step}: sim {n} formula {f:.1f}")
        if abs(n - f) > 1.5: fails.append(f"S2-{fps}-{step}")
ci, cw = run(8, 108, 60000, "carry_if"), run(8, 108, 60000, "carry_while")
print(f"S3 8fps carry-if {ci} carry-while {cw} ideal {60000/108:.1f}")
if ci != 480 or abs(cw - 555.6) > 1.5: fails.append("S3")
for hold in (30000, 60000):                     # BREAK: does the relative gap really stay ~16.7%?
    a, b = run(144, 108, hold), run(30, 108, hold)
    print(f"S4 hold {hold}: 144fps {a} 30fps {b} abs gap {a-b} rel {(a-b)/a:.3f}")
    if abs((a - b) / a - 0.1667) > 0.01: fails.append(f"S4-{hold}")
g30 = run(144, 108, 30000) - run(30, 108, 30000); g60 = run(144, 108, 60000) - run(30, 108, 60000)
print(f"S4 abs gap 30 s {g30} vs 60 s {g60}")
if not g60 > g30: fails.append("S4-abs")
print("RESULT: " + ("FAIL " + ",".join(fails) if fails else
      "PASS counts 450/515/540 reproduced, formula holds at 20/90/120fps and step 250, carry_if 480 vs carry_while 556, rel gap 16.7%"))
