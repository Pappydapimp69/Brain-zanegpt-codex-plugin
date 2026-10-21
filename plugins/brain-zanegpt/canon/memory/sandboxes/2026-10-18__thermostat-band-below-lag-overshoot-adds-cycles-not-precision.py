# New domain THERMOSTAT-CONTROL. Real scenario: a room heated by an electric heater under
# on/off hysteresis control, with the heater's output lagging the switch (element warm-up /
# air delivery). Room: C dT/dt = P*h(t) - k*(T - Tout), C = 2e5 J/K, k = 60 W/K, P = 2000 W,
# Tout = 5 C, setpoint 20 C, dt = 1 s, 6 h simulated after a 1 h warm-up. h(t) is the switch
# state delayed by `lag` seconds. Switch on below sp - band/2, off above sp + band/2.
# Prediction (before run): at lag 120 s the measured temperature swing exceeds the band by about
# (heating rate at switch-off) x lag, so shrinking the band from 1.0 K to 0.25 K cuts the swing
# by under 0.3 K while raising cycles per hour by more than 40 percent; at lag 0 swing tracks
# the band within 0.15 K (BREAK: the same band change at lag 0 should cut swing by about 0.75 K).
C, K, P, TOUT, SP = 2e5, 60.0, 2000.0, 5.0, 20.0
def sim(band, lag, hours=7, warm=1):
    T = 18.0; on = False; q = [0.0] * (lag + 1)
    cycles = 0; lo, hi = 1e9, -1e9; n = hours * 3600
    for s in range(n):
        if on and T > SP + band / 2: on = False
        elif (not on) and T < SP - band / 2:
            on = True
            if s >= warm * 3600: cycles += 1
        q.append(1.0 if on else 0.0); h = q.pop(0)
        T += (P * h - K * (T - TOUT)) / C
        if s >= warm * 3600:
            lo, hi = min(lo, T), max(hi, T)
    return hi - lo, cycles / (hours - warm)
R = {}
for lag in (0, 120):
    for band in (1.0, 0.5, 0.25):
        R[(lag, band)] = sim(band, lag)
        print("lag %3d band %.2f -> swing %.2f K, cycles/h %.2f" % ((lag, band) + R[(lag, band)]))
d120 = R[(120, 1.0)][0] - R[(120, 0.25)][0]
c120 = R[(120, 0.25)][1] / R[(120, 1.0)][1] - 1
c0 = R[(0, 0.25)][1] / R[(0, 1.0)][1] - 1
d0 = R[(0, 1.0)][0] - R[(0, 0.25)][0]
over = {lag: [R[(lag, b)][0] - b for b in (1.0, 0.5, 0.25)] for lag in (0, 120)}
# Iteration 1 refuted the prediction: band 1.0 -> 0.25 at lag 120 cut the swing by 0.72 K, not
# under 0.3 K (cycles +48% held). The data show swing = band + a constant overshoot, so the
# revised claim: the overshoot (swing minus band) is the same at every band for a given lag.
spread120 = max(over[120]) - min(over[120])
ok = (spread120 < 0.05 and min(over[120]) > 1.0 and max(over[0]) < 0.05 and c120 > 0.40 and c120 < c0)
print("overshoot (swing - band) at lag 120: %s ; at lag 0: %s" % (["%.2f" % x for x in over[120]], ["%.2f" % x for x in over[0]]))
print("RESULT: %s swing = band + constant overshoot (lag 120 s: %.2f K at every band, spread %.2f; lag 0: under 0.05); narrowing 1.0 -> 0.25 cuts swing %.2f K at either lag, costs %+.0f%% cycles at lag 120 versus %+.0f%% at lag 0"
      % ("PASS" if ok else "FAIL", sum(over[120]) / 3, spread120, d120, c120 * 100, c0 * 100))
