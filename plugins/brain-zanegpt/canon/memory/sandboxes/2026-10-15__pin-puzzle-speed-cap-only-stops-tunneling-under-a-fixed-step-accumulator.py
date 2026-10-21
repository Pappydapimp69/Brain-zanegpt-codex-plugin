# Sandbox: demo-disc's pin-puzzle fix caps particle speed "below one radius per
# tick" (400 px/s at 60 Hz = 6.7 px/tick) so water stops tunneling through 10 px
# walls. brain#E119 says integrate at a fixed dt via an accumulator; demo-disc#E1
# says the test hook must own the clock. Composed question: is the px/s cap still
# a no-tunnel guarantee when the step is the render frame time instead of a
# fixed 1/60 s?
# PREDICTION (written before the first run): fixed 60 Hz 0% tunnel; raw 30 fps
# frames (13.3 px/step) tunnel on a sizeable share of start phases (>= 20%);
# the same 30 fps render driving a 60 Hz accumulator 0%; a 10-frame hitch
# schedule tunnels on some phases; an uncapped 900 px/s ball tunnels even
# under the accumulator (break case: the accumulator alone is not enough).
# Model: a particle centre falls at constant speed onto a wall [100,110) (10 px);
# a discrete check pushes it back above the wall if the centre lands inside.
# Tunnel = the centre ends below the wall. Start phase swept over 0..9.9 px in
# 0.1 px steps (100 phases). Deterministic, no RNG, no timing.
WALL_TOP, WALL = 100.0, 10.0
def run(speed, frames, substep=None, T=1.5):
    tunnels = 0
    for k in range(100):
        y = 50.0 + k * 0.1
        t, i, acc = 0.0, 0, 0.0
        through = False
        while t < T and not through:
            dt = frames[i % len(frames)]; i += 1; t += dt
            steps = [dt] if substep is None else []
            if substep is not None:
                acc += dt
                while acc >= substep - 1e-12:
                    steps.append(substep); acc -= substep
            for h in steps:
                y += speed * h
                if WALL_TOP <= y < WALL_TOP + WALL:
                    y = WALL_TOP - 0.001   # pushed out above; it rests on the wall
                    speed_local = 0
                if y >= WALL_TOP + WALL:
                    through = True; break
            if y >= WALL_TOP - 0.01 and not through:
                break   # settled on the wall
        tunnels += through
    return tunnels
cases = [
 ("fixed 60 Hz, cap 400", 400, [1/60], None),
 ("raw 30 fps frames, cap 400", 400, [1/30], None),
 ("raw 60 Hz with a 1/20 s hitch every 10th frame, cap 400", 400, [1/60]*9 + [1/20], None),
 ("30 fps render into a 60 Hz accumulator, cap 400", 400, [1/30], 1/60),
 ("hitch schedule into a 60 Hz accumulator, cap 400", 400, [1/60]*9 + [1/20], 1/60),
 ("BREAK: uncapped 900 px/s into a 60 Hz accumulator", 900, [1/60], 1/60),
]
res = {}
for name, v, fr, sub in cases:
    n = run(v, fr, sub); res[name] = n
    print(f"{name:<58} tunnels {n:3d}/100 phases")
# Iteration 2: the first hitch run never coincided with the wall crossing
# (the ball lands about frame 8, the hitch was frame 10). Sweep the hitch
# position over the 10-frame cycle.
hit_raw = sum(run(400, [1/60]*j + [1/20] + [1/60]*(9-j)) for j in range(10))
hit_acc = sum(run(400, [1/60]*j + [1/20] + [1/60]*(9-j), 1/60) for j in range(10))
print(f"hitch at each of 10 positions, raw frames:      tunnels {hit_raw:4d}/1000")
print(f"hitch at each of 10 positions, 60 Hz accumulator: tunnels {hit_acc:4d}/1000")
ok = (res[cases[0][0]] == 0 and res[cases[1][0]] >= 20 and res[cases[3][0]] == 0
      and res[cases[4][0]] == 0 and res[cases[5][0]] > 0 and hit_raw > 0 and hit_acc == 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"cap holds at fixed 60 Hz (0) and under the accumulator (0, 0) but raw 30 fps tunnels {res[cases[1][0]]}/100 and one 1/20 s hitch {hit_raw}/1000 when swept over its position (0/1000 with the accumulator); uncapped 900 px/s tunnels {res[cases[5][0]]}/100 even with the accumulator")
