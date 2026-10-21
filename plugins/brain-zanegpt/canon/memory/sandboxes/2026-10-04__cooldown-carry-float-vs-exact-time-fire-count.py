"""Prediction (before run): a carry-overshoot cooldown (STEP=100 ms, 60 s run) fires exactly 600 times with exact rational time at
30/60/144 fps; the same loop with float accumulation of dt=1/fps drifts and gets at least one fps wrong by >=1 fire
(float sums of 1/60 and 1/144 rarely land on exact multiples of 0.1); reset-to-STEP fires fewer than 600 at 144 fps.
Built to break: a float carry at STEP=125 ms (exactly representable) must NOT drift, i.e. the float error is a property of the step, not of carry.
Deterministic, stdlib only."""
from fractions import Fraction as F

def run_exact(step, fps, secs, carry):
    dt = F(1, fps); cd = F(0); fires = 0
    for _ in range(secs * fps):
        cd -= dt
        if carry:
            while cd <= 0: fires += 1; cd += step
        elif cd <= 0:
            fires += 1; cd = step
    return fires

def run_float(step, fps, secs):
    dt = 1.0 / fps; cd = 0.0; fires = 0; step = float(step)
    for _ in range(secs * fps):
        cd -= dt
        while cd <= 0: fires += 1; cd += step
    return fires

ok = True; out = []
S = F(1, 10)
for fps in (30, 60, 144):
    e = run_exact(S, fps, 60, True); f = run_float(0.1, fps, 60); r = run_exact(S, fps, 60, False)
    out.append(f"fps{fps} exact_carry={e} float_carry={f} reset={r}")
    print(out[-1], flush=True)
    ok = ok and e == 600
ex = {fps: run_exact(S, fps, 60, True) for fps in (30, 60, 144)}
fl = {fps: run_float(0.1, fps, 60) for fps in (30, 60, 144)}
drift = [fps for fps in ex if ex[fps] != fl[fps]]
reset144 = run_exact(S, 144, 60, False)
brk = {fps: (run_exact(F(1, 8), fps, 60, True), run_float(0.125, fps, 60)) for fps in (30, 60, 144)}
brk_ok = all(a == b for a, b in brk.values())
out.append(f"drift_fps={drift} reset144={reset144} step125_exact_vs_float={brk}")
print(out[-1])
ok = ok and len(drift) >= 1 and reset144 < 600 and brk_ok
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
