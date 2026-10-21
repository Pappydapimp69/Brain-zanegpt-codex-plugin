# Deterministic railway following-train sim (dt = 0.05 s, no RNG). Leader runs at constant v; follower is
# limited by movement authority: fixed block = start of the block holding the leader's tail, moving block = leader tail.
import math
def steady_headway(v, b, L, mode, B=0.0, dt=0.05, T=900.0, start_gap=50.0):
    lead_tail = 0.0 - 0.0      # leader tail position (front = tail + L)
    lead = L                   # leader front
    pos = -start_gap           # follower front, starts close behind the leader (gap grows to its safe equilibrium)
    speed = v; t = 0.0
    while t < T:
        lead += v * dt; tail = lead - L
        auth = tail if mode == "moving" else math.floor(tail / B) * B        # fixed: start of occupied block
        room = max(auth - pos, 0.0)
        vmax = min(v, math.sqrt(2 * b * room))
        speed = min(vmax, speed + 1.0 * dt)            # accel 1 m/s^2
        pos += speed * dt; t += dt
        if pos > auth + 0.5: return None, "overrun"
    return (lead - L - pos + L) / v, None               # time gap between fronts = distance between fronts / v
b = 0.7; L = 100.0
H = {}
for v in (10.0, 20.0, 40.0):
    H[v] = {"moving": steady_headway(v, b, L, "moving")[0]}
    for B in (100, 300, 750, 1500): H[v][B] = steady_headway(v, b, L, "fixed", B=float(B))[0]
    cf = v / (2 * b) + L / v
    print("v=%2.0f closed-form moving %.1f sim %.1f | fixed:" % (v, cf, H[v]["moving"]), {B: round(H[v][B], 1) for B in (100, 300, 750, 1500)})
cf_err = max(abs(H[v]["moving"] - (v / (2 * b) + L / v)) / (v / (2 * b) + L / v) for v in H)
pen_err = max(abs((H[v][B] - H[v]["moving"]) - B / v) / (B / v) for v in H for B in (100, 300, 750, 1500))
ratio = {v: round(H[v][1500] / H[v]["moving"], 2) for v in H}
close = round(H[40.0][100] / H[40.0]["moving"], 2)          # BREAK of "moving block always gains a lot"
print("fixed(B=1500)/moving by speed", ratio, "fixed(B=100)/moving at 40 m/s", close, "model errors", round(cf_err, 4), round(pen_err, 3))
ok = cf_err < 0.01 and pen_err < 0.12 and ratio[10.0] > ratio[20.0] > ratio[40.0] and close < 1.1
print("RESULT: %s moving-block headway = v/(2b)+L/v (max error %.4f); a fixed block adds about B/v seconds (max error %.3f), so the moving-block gain FALLS with speed (1500 m blocks: %s) and a 100 m block at 40 m/s costs only %.2fx"
      % ("PASS" if ok else "FAIL", cf_err, pen_err, ratio, close))
