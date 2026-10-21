"""Prediction (before run): frame index from integer microseconds (elapsed_us * hz // 1_000_000) matches the exact Fraction oracle on
every render over 60 s at 30 Hz sprite rate with 60 fps rendering; float acc += 1/60 with floor(acc*hz) disagrees with the oracle on
at least 1 render (recorded 294/1800 was at a different setup, so I predict only >=1, not that number).
Built to break: after a rate change from 30 to 12 Hz at t=30 s, naive elapsed*new_hz jumps frames (>=1 jump larger than 1 frame at the change)
while phase-accumulating integer time does not (max step <=1 everywhere). Deterministic, stdlib only."""
from fractions import Fraction as F
FPS = 60; SECS = 60; N = FPS * SECS
US = 1_000_000 // FPS * 0  # unused; exact frame time handled by integer math below

def oracle(i, hz): return (F(i, FPS) * hz).__floor__()
def int_frame(i, hz): return (i * 1_000_000 // FPS) * hz // 1_000_000   # integer us (truncated per frame)
def int_frame_exact(i, hz): return (i * hz) // FPS                       # pure integer ticks

bad_int_us = bad_int_tick = bad_float = 0
acc = 0.0
for i in range(1, N + 1):
    acc += 1 / FPS
    o = oracle(i, 30)
    bad_float += int(acc * 30) != o
    bad_int_us += int_frame(i, 30) != o
    bad_int_tick += int_frame_exact(i, 30) != o
print(f"float_bad={bad_float}/{N} int_us_bad={bad_int_us}/{N} int_tick_bad={bad_int_tick}/{N}", flush=True)

# rate change at t=30 s from 30 Hz to 12 Hz
naive_prev = None; naive_jump = 0; phase = 0; phase_prev = None; phase_jump = 0
for i in range(1, N + 1):
    hz = 30 if i <= 1800 else 12
    naive = (i * hz) // FPS
    if naive_prev is not None: naive_jump = max(naive_jump, abs(naive - naive_prev))
    naive_prev = naive
    # phase accumulation in integer units of 1/(FPS) tick-hz: phase += hz per render, frame = phase // FPS
    phase += hz
    pf = phase // FPS
    if phase_prev is not None: phase_jump = max(phase_jump, abs(pf - phase_prev))
    phase_prev = pf
print(f"max_step naive={naive_jump} phase={phase_jump}")
ok = bad_float >= 1 and bad_int_us == 0 and bad_int_tick == 0 and naive_jump > 1 and phase_jump <= 1
print("RESULT:", "PASS" if ok else "FAIL", f"float_bad={bad_float}/{N} int_us_bad={bad_int_us}/{N} int_tick_bad={bad_int_tick}/{N} naive_max_step={naive_jump} phase_max_step={phase_jump}")
