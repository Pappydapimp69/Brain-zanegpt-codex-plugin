# Sandbox: semi-implicit vs explicit Euler on a lossless spring; find where the kernel stops holding.
# Also exercises: fixed-dt per-frame travel vs a thin wall (sandbox-collision/E1) and frame-rate
# dependence of a fixed-step sim (sandbox-kernel-system-determinism/E4). No RNG, no timing.
import math
def run(method, w, dt, T=200.0):
    x, v = 1.0, 0.0
    e0 = 0.5*v*v + 0.5*w*w*x*x
    n = int(round(T/dt)); emax = e0
    for _ in range(n):
        a = -w*w*x
        if method == "explicit":
            x, v = x + v*dt, v + a*dt
        else:
            v = v + a*dt; x = x + v*dt
        e = 0.5*v*v + 0.5*w*w*x*x
        if not math.isfinite(e) or e > 1e300: return float("inf")
        emax = max(emax, e)
    return emax/e0
w = 2*math.pi
# S1 kernel claim at 60fps
ex, si = run("explicit", w, 1/60), run("semi", w, 1/60)
print("S1 dt=1/60 explicit=%.3g semi=%.4f" % (ex, si))
# S2 BREAK: stability bound w*dt<2 for semi-implicit
for wdt in (1.9, 1.99, 2.01, 2.5):
    print("S2 w*dt=%.2f semi=%.3g" % (wdt, run("semi", wdt, 1.0, 400.0)))
bound_ok = run("semi", 1.99, 1.0, 400.0) < 1e4 and run("semi", 1.99, 1.0, 400.0) > 100 and run("semi", 2.01, 1.0, 400.0) > 1e6
# S3 fps dependence: bounded energy error is not fps independent (phase drift)
for fps in (30, 60, 144):
    dt = 1/fps; n = int(round(10/dt)); x, v = 1.0, 0.0
    for _ in range(n):
        v += -w*w*x*dt; x += v*dt
    print("S3 fps=%d x(10s)=%.4f exact=%.4f" % (fps, x, math.cos(w*10)))
xs = []
for fps in (30, 60, 144):
    dt = 1/fps; x, v = 1.0, 0.0
    for _ in range(int(round(10/dt))):
        v += -w*w*x*dt; x += v*dt
    xs.append(x)
fps_differ = max(xs) - min(xs) > 0.01
# S4 thin wall: ball falling under gravity, discrete overlap check vs swept check, semi-implicit
def fall(dt, swept):
    y, v, wall_lo, wall_hi = 100.0, 0.0, 0.0, 0.5   # fall toward wall slab [0,0.5]
    while y > -50:
        v -= 9.81*dt; ny = y + v*dt
        if swept:
            if ny <= wall_hi and y >= wall_lo: return "hit"
        else:
            if wall_lo <= ny <= wall_hi: return "hit"
        y = ny
    return "tunnel"
res = {(dt, s): fall(dt, s) for dt in (1/60, 1/2) for s in (False, True)}
print("S4", res)
tunnel_ok = res[(1/2, False)] == "tunnel" and res[(1/2, True)] == "hit" and res[(1/60, True)] == "hit"
ok = ex > 1e20 and si < 1.1 and bound_ok and fps_differ and tunnel_ok
print("RESULT: %s explicit=%.3g semi=%.4f; semi stable w*dt<2 only (bounded but 200x at 1.99, blows at 2.01); fps drift %.3f; tunnel=%s"
      % ("PASS" if ok else "FAIL", ex, si, max(xs)-min(xs), tunnel_ok))
