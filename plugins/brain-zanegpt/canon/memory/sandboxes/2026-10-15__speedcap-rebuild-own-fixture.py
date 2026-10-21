"""Blind rebuild: a speed cap of one radius per tick guards only a fixed step.
Own fixture (not the original's): radius 2.5 px, wall 3 px thick at y=200..203,
gravity 1500 px/s^2, drop from y=0 with initial downward 300 px/s, penalty-spring
contact k = omega^2 with omega = 60 rad/s and light damping. Speed cap = radius per
60 Hz tick, i.e. 150 px/s (a velocity, so a long dt moves further than one radius).
Semi-implicit Euler. Discrete contact: the spring acts only while the centre is
inside the band [top - r, bottom + r]. Tunnelled = ends below the wall.
PREDICTION (written before running): band is 8 px; a capped step moves 150*dt px,
so variable dt tunnels when dt > 8/150 s (below ~18.75 fps): fixed 1/60 accumulator
never tunnels at any frame rate or hitch; variable dt is fine at 60 and 30 fps,
tunnels at 15 and 10 fps and on a single 200 ms hitch."""
R, TOP, BOT, G, OMEGA, VCAP, FIX = 2.5, 200.0, 203.0, 1500.0, 60.0, 150.0, 1 / 60

def step(y, v, dt):
    a = G
    if TOP - R <= y <= BOT + R:                      # in contact band
        depth = y - (TOP - R)
        a += -OMEGA ** 2 * depth - 2 * 0.1 * OMEGA * v
    v += a * dt
    v = max(-VCAP, min(VCAP, v))                     # the speed cap
    y += v * dt
    return y, v

def simulate(frames, fixed, y0=0.0):
    y, v, acc, peak_v = y0, 300.0, 0.0, 0.0
    v = min(v, VCAP)
    for f in frames:
        if fixed:
            acc += f
            while acc >= FIX:
                y, v = step(y, v, FIX); acc -= FIX; peak_v = max(peak_v, abs(v))
        else:
            y, v = step(y, v, f); peak_v = max(peak_v, abs(v))
        if y > BOT + R + 1:
            return "TUNNEL", peak_v
    return "held", peak_v

def frames(fps, seconds=4.0, hitch_at=None):
    n = int(seconds * fps); fr = [1 / fps] * n
    if hitch_at is not None: fr[hitch_at] = 0.200
    return fr

# Iteration 2: a single hitch only matters if it lands during the approach, and a
# low frame rate only tunnels if a step straddles the band, so sweep the phase:
# 40 start heights (0..39 px, 1 px apart) per frame rate, and a 200 ms hitch at
# every 60 fps frame in the first 2 s.
res = {}
for fps in (60, 30, 15, 10):
    fx = sum(simulate(frames(fps), True, y0)[0] == "TUNNEL" for y0 in range(40))
    vr = sum(simulate(frames(fps), False, y0)[0] == "TUNNEL" for y0 in range(40))
    res[f"{fps} fps"] = (fx, vr, 40)
hx = sum(simulate(frames(60, hitch_at=k), True)[0] == "TUNNEL" for k in range(120))
hv = sum(simulate(frames(60, hitch_at=k), False)[0] == "TUNNEL" for k in range(120))
res["one 200 ms hitch at 60 fps (break)"] = (hx, hv, 120)
for n, (fx, vr, tot) in res.items():
    print(f"{n:36s} tunnelled  fixed+accumulator {fx:3d}/{tot}   variable dt {vr:3d}/{tot}")
fixed_ok = all(r[0] == 0 for r in res.values())
var_t = [n for n, r in res.items() if r[1] > 0]
ok = fixed_ok and res["60 fps"][1] == 0 and "10 fps" in var_t and res["one 200 ms hitch at 60 fps (break)"][1] > 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} fixed step tunnelled 0 times in every case: {fixed_ok}; variable dt tunnelled at "
      + "; ".join(f"{n} {res[n][1]}/{res[n][2]}" for n in var_t))
