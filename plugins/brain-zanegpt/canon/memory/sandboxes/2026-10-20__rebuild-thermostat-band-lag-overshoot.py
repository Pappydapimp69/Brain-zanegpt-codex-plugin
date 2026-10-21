# Own fixture: 1.5 kW heater, 150 kJ/K room, 40 W/K loss, ambient 5C, setpoint 21C.
# Lag modelled two ways: first-order power lag (tau) and pure dead time.
def run(band, lag, kind, dt=1.0, T=8*3600, P=1500.0, C=150e3, G=40.0, Ta=5.0, sp=21.0):
    temp = sp; on = False; out = 0.0; buf = []
    n = int(T/dt); lo = []; ev = 0; hist = []
    delay = int(lag/dt)
    for i in range(n):
        if temp > sp + band/2: on = False
        elif temp < sp - band/2:
            if not on: ev += (i > n//2)
            on = True
        cmd = P if on else 0.0
        if kind == "tau":
            out += (cmd - out) * dt / max(lag, 1e-9) if lag > 0 else cmd - out
        else:
            buf.append(cmd); out = buf[-delay-1] if len(buf) > delay else 0.0 if delay else cmd
        temp += (out - G*(temp - Ta)) / C * dt
        if i > n//2: hist.append(temp)
    return max(hist) - min(hist), ev / ((T - T//2) / 3600.0)
print("kind lag band swing cycles/h")
res = {}
for kind in ("tau", "dead"):
    for lag in (0, 90, 240):
        for band in (1.0, 0.5, 0.25):
            s, c = run(band, lag, kind); res[(kind, lag, band)] = (s, c)
            print(kind, lag, band, round(s, 3), round(c, 2))
ok = True; notes = []
for kind in ("tau", "dead"):
    cut0 = res[(kind,0,1.0)][0] - res[(kind,0,0.25)][0]
    cut90 = res[(kind,90,1.0)][0] - res[(kind,90,0.25)][0]
    cyc = res[(kind,90,0.25)][1] / res[(kind,90,1.0)][1] - 1
    over = res[(kind,90,0.25)][0] - 0.25
    notes.append(f"{kind}: cut@lag0={cut0:.2f} cut@lag90={cut90:.2f} cycles+{cyc*100:.0f}% overshoot@0.25={over:.2f}")
    ok &= cut0 > 0.55 and cut90 < cut0 and cyc > 0.4 and over > 0.3
# BREAK: very long lag -- is overshoot still constant in band?
ov = [res[("dead",240,b)][0]-b for b in (1.0,0.5,0.25)]
notes.append("dead240 overshoot by band: " + ", ".join(f"{o:.2f}" for o in ov))
const = max(ov) - min(ov) < 0.15
notes.append(f"overshoot constant across bands within 0.15: {const}")
ok &= const
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + "; ".join(notes))
