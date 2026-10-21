"""Prediction (before run): with a 100 ms cooldown and a 400 ms stall every 2 s at 60 fps (10 s run, integer microseconds),
a max-delta cap of 50 ms makes the sim lose exactly the clipped time: sim clock trails wall by 350 ms per stall, so the carry
cooldown fires 10 * 3.5 = 35 fewer times than the uncapped run (uncapped = 100 fires); a cap of 500 ms (above the stall) loses none.
Built to break: the loss must scale with the number of stalls, so doubling stall frequency must double the lost fires (70), not leave it at 35.
Deterministic, stdlib only."""
STEP = 100_000          # us
FRAME = 16_667          # us, ~60 fps (integer)

def run(cap, stall_every, stall_len, wall_total=10_000_000):
    wall = 0; sim = 0; cd = 0; fires = 0; next_stall = stall_every; n = 0
    while wall < wall_total:
        dt = FRAME
        if wall >= next_stall:
            dt = stall_len; next_stall += stall_every
        wall += dt
        sdt = min(dt, cap) if cap else dt
        sim += sdt
        cd -= sdt
        while cd <= 0:
            fires += 1; cd += STEP
    return fires, wall - sim

ok = True; out = []
base, _ = run(None, 2_000_000, 400_000)
capped, lag = run(50_000, 2_000_000, 400_000)
high, lag_high = run(500_000, 2_000_000, 400_000)
base2, _ = run(None, 1_000_000, 400_000)
capped2, lag2 = run(50_000, 1_000_000, 400_000)
out.append(f"uncapped={base} cap50={capped} lost={base-capped} lag_us={lag} cap500={high} lag500={lag_high}")
out.append(f"double_stalls uncapped={base2} cap50={capped2} lost={base2-capped2} lag_us={lag2}")
print(out[0]); print(out[1])
ok = (base - capped == 35) and high == base and (base2 - capped2 == 70)
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
