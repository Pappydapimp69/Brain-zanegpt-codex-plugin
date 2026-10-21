"""Train edge: demo-disc E1 (particle liquid: cap speed under one radius per
tick or particles tunnel through thin walls) + brain E119 (semi-implicit Euler
is bounded only at a FIXED dt with dt*omega < 2; use an accumulator).
Composed claim: the speed cap is a per-TICK distance, so it only protects a
fixed-step sim; under a variable frame dt the same cap in px/s tunnels, and the
contact spring crosses dt*omega = 2 at the same time - one accumulator fixes
both. Exact arithmetic on a deterministic 1-D scene, no rng.
Scene: particle radius 7 falls from y = 200 under gravity 2000 px/s^2 onto a
wall occupying [96, 100] (4 px thick); contact = penalty spring k with
omega*dt_fixed = 1.0 (dt_fixed = 1/60); speed cap 0.9 * r / dt_fixed px/s.
Frame times: steady 60, 30, 10 fps, and a 60 fps run with one 250 ms hitch.
Integrators: (V) one semi-implicit step per frame with dt = frame time;
(F) fixed 1/60 steps via an accumulator (max 15 steps per frame).
Outcomes: tunnelled (ends below the wall), exploded (bounce peak above start).
PREDICTION (written before running): F never tunnels or explodes at any frame
rate; V is fine at 60 fps, tunnels at 10 fps and on the 250 ms hitch, and its
contact spring explodes or tunnels whenever dt*omega > 2 (from 30 fps down:
30 fps is dt*omega = 2.0, the edge).
"""
import math, sys
print("python", sys.version.split()[0])
R, G, TOP, BOT = 7.0, 2000.0, 100.0, 96.0
DTF = 1 / 60; OMEGA = 1.0 / DTF; K = OMEGA ** 2; VCAP = 0.9 * R / DTF
def step(y, v, dt):
    a = -G
    pen = (TOP + R) - y if y > BOT else 0.0
    if 0 < pen: a += K * pen
    v = max(-VCAP, min(VCAP, v + a * dt))
    y = y + v * dt
    return y, v
def run(frames, mode):
    y, v, acc, peak, tun = 200.0, 0.0, 0.0, 0.0, False
    landed = False
    for ft in frames:
        if mode == "V":
            y, v = step(y, v, ft)
        else:
            acc = min(acc + ft, 15 * DTF)
            while acc >= DTF - 1e-12:
                y, v = step(y, v, DTF); acc -= DTF
        if y < BOT - R: tun = True
        if y < TOP + R + 1: landed = True
        if landed: peak = max(peak, y)
    return tun, peak > 200.0, round(y, 2), round(peak, 1)
FR = {"60fps": [1 / 60] * 240, "30fps": [1 / 30] * 120, "10fps": [0.1] * 40,
      "60fps+hitch": [1 / 60] * 30 + [0.25] + [1 / 60] * 200}
res = {}
for nm, fr in FR.items():
    for mode in "VF":
        res[(nm, mode)] = run(fr, mode)
        t, e, y, pk = res[(nm, mode)]
        print(f"{nm:12s} {mode}: tunnelled {t!s:5s} exploded {e!s:5s} final y {y:8.2f} peak after landing {pk}  (dt*omega {max(fr) * OMEGA if mode == 'V' else 1.0:.2f})")
c = [all(not res[(n, "F")][0] and not res[(n, "F")][1] for n in FR),
     not res[("60fps", "V")][0] and not res[("60fps", "V")][1],
     res[("10fps", "V")][0] or res[("10fps", "V")][1],
     res[("60fps+hitch", "V")][0] or res[("60fps+hitch", "V")][1]]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; fixed+accumulator clean at all rates; variable dt: 30fps {res[('30fps','V')][:2]}, 10fps {res[('10fps','V')][:2]}, hitch {res[('60fps+hitch','V')][:2]} (tunnelled, exploded)")
