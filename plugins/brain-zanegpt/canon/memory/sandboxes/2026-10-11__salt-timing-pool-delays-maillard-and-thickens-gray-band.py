"""Sandbox: kitchen timeline chaining three kernels: salt-timing (surface pool peaks mid-window), maillard (no browning until surface water is gone,
surface capped near 100 C), resting/carryover (heat already pushed inward keeps travelling after the pan).
ASSUMPTION (labelled, not derived): surface water layer d(t_salt) in mm = 0.10 baseline (patted); rises linearly to 0.60 at 28 min; falls linearly back to 0.10 by 45 min.
Computed: 1-D conduction in a 3 cm steak seared on one face (far face insulated), evaporative cap at 100 C while water remains, browning starts at surface 177 C.
Prediction (before run): browning delay (s) is largest at 28 min salting (>=4x the 0-min delay), the 45+ min and 0-min delays are within 10% of each other;
gray band depth (T>=60 C) after 60 s of browning is larger at 28 min than at 0 or 60 min by >=0.5 mm; after a 5-minute rest the band is deeper than at pull time for all
cases; and an 'unpatted' wetter surface (0.60 mm baseline) at 0 min salt equals the 28-min case within 15% (the pool IS the mechanism, not the salt itself)."""
ALPHA, K = 1.4e-7, 0.5
RHO_L = 2.26e6   # J/kg latent; water 1000 kg/m3 -> J/m2 per metre of water = 2.26e9
H_PAN, T_PAN = 300.0, 230.0
L, N = 0.03, 31
dx = L / (N - 1); dt = 0.4 * dx * dx / ALPHA
def pool_mm(salt_min):
    if salt_min <= 28: return 0.10 + 0.50 * salt_min / 28
    if salt_min < 45: return 0.60 - 0.50 * (salt_min - 28) / 17
    return 0.10
def sear(water_mm, brown_secs=60, rest_secs=300):
    T = [4.0] * N; water = water_mm / 1000.0 * 2.26e9  # J/m2 left to evaporate
    r = ALPHA * dt / dx ** 2; t = 0.0; t_brown = None
    def band(T):
        # depth (mm) of the 60 C isotherm from the pan face, linearly interpolated
        for i in range(N - 1):
            if T[i] >= 60.0 > T[i + 1]: return (i + (T[i] - 60.0) / (T[i] - T[i + 1])) * dx * 1000
        return N * dx * 1000 if T[-1] >= 60.0 else 0.0
    while True:
        # surface node 0 gets pan flux
        Ts = T[0]
        if water > 0: Ts = 100.0
        q = H_PAN * (T_PAN - Ts)
        N_ = T[:]
        for i in range(1, N - 1): N_[i] = T[i] + r * (T[i - 1] - 2 * T[i] + T[i + 1])
        N_[N - 1] = T[N - 1] + 2 * r * (T[N - 2] - T[N - 1])
        # surface node energy balance with half cell
        cond = K * (T[1] - T[0]) / dx
        dE = (q + cond) * dt
        if water > 0:
            used = min(water, max(dE, 0)); water -= used; dE -= used
            N_[0] = 100.0 if water > 0 else 100.0 + dE / (RHO_C * dx / 2)
        else:
            N_[0] = T[0] + dE / (RHO_C * dx / 2)
        T = N_; t += dt
        if t_brown is None and water <= 0 and T[0] >= 177.0: t_brown = t
        if t_brown is not None and t - t_brown >= brown_secs: break
        if t > 3000: break
    pull_band = band(T)
    # rest: pan removed, surface insulated (air)
    for _ in range(int(rest_secs / dt)):
        N_ = T[:]
        N_[0] = T[0] + 2 * r * (T[1] - T[0])
        for i in range(1, N - 1): N_[i] = T[i] + r * (T[i - 1] - 2 * T[i] + T[i + 1])
        N_[N - 1] = T[N - 1] + 2 * r * (T[N - 2] - T[N - 1])
        T = N_
    return t_brown, pull_band, band(T)
RHO_C = 3.6e6   # volumetric heat capacity J/m3K (alpha*rho_c = k)
ok = True
res = {}
for ts in (0, 10, 20, 28, 35, 45, 60):
    res[ts] = sear(pool_mm(ts))
    print("salt %2d min: pool %.2f mm browning starts at %.0f s, band at pull %.1f mm, after 5 min rest %.1f mm" % (ts, pool_mm(ts), res[ts][0], res[ts][1], res[ts][2]))
d0, d28, d45, d60 = res[0][0], res[28][0], res[45][0], res[60][0]
cond1 = d28 / d0 >= 4   # run 1 missed this: ratio was 1.26 because heating a dry surface from 4 C to 177 C dominates the 26 s of evaporation
cond2 = abs(d45 - d0) / d0 <= 0.10 and abs(d60 - d0) / d0 <= 0.10
cond3 = res[28][1] - res[0][1] >= 0.5 and res[28][1] - res[60][1] >= 0.5
cond4 = all(res[k][2] > res[k][1] for k in res)
wet = sear(0.60)
cond5 = abs(wet[0] - d28) / d28 <= 0.15
print("delay ratio 28/0 = %.2f; 45 vs 0: %.3f; 60 vs 0: %.3f; wet unsalted %.0f s vs 28-min %.0f s" % (d28 / d0, (d45 - d0) / d0, (d60 - d0) / d0, wet[0], d28))
print("conds:", cond1, cond2, cond3, cond4, cond5)
ok = cond1 and cond2 and cond3 and cond4 and cond5
print("RESULT: %s browning delay 0min %.0fs, 28min %.0fs (x%.1f), 45min %.0fs; gray band 0min %.1f mm, 28min %.1f mm, 60min %.1f mm; rest deepens band in all cases=%s; wet unsalted %.0fs vs 28min %.0fs" % (
    "PASS" if ok else "FAIL", d0, d28, d28 / d0, d45, res[0][1], res[28][1], res[60][1], cond4, wet[0], d28))
