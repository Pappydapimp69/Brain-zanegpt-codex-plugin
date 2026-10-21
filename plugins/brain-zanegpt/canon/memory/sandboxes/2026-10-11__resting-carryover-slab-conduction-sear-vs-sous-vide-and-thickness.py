# 1D slab conduction (both faces), explicit finite differences. Phase 1: faces held at Ts until the center reaches PULL.
# Phase 2: rest in air (Robin BC). Measure center overshoot after the pull. Compares sear, gentle heat, thickness, sous vide.
ALPHA, K, H_AIR, T_AIR = 1.4e-7, 0.45, 10.0, 20.0

SEAR_END, FINISH = 300.0, 75.0    # hard sear for a few minutes, then a gentle 75 C effective finish until the pull (assumed)
DRY_S = 120.0   # surface water caps the face near 100 C until it has dried (browning kernel)

def run(thick_cm, Ts, pull, T0=5.0, n=21, sous=False, rest_s=1800):
    half = thick_cm / 200.0
    dx = half / (n - 1)
    dt = 0.4 * dx * dx / ALPHA
    T = [T0] * n                      # index 0 = center, n-1 = surface
    t = 0.0
    def step(Tl, surface_fn):
        new = Tl[:]
        for i in range(n - 1):
            left = Tl[i - 1] if i > 0 else Tl[1]          # symmetry at center
            new[i] = Tl[i] + ALPHA * dt / dx**2 * (left - 2 * Tl[i] + Tl[i + 1])
        new[n - 1] = surface_fn(new)
        return new
    # phase 1
    while T[0] < pull - 1e-9 and t < 6 * 3600:
        T = step(T, lambda new: (Ts if sous else (min(Ts, 100.0) if t < DRY_S else (Ts if t < SEAR_END else FINISH)))); t += dt
    cook_t = t
    # phase 2: air Robin BC, node balance on a half cell at the surface
    def air(new):
        Ts_ = T[n - 1]
        flux_in = ALPHA * dt / dx**2 * 2 * (T[n - 2] - Ts_)
        loss = 2 * H_AIR * (Ts_ - T_AIR) * dt / (K / ALPHA * dx)
        return Ts_ + flux_in - loss
    peak, tp, t2 = T[0], 0.0, 0.0
    while t2 < rest_s:
        T = step(T, air); t2 += dt
        if T[0] > peak: peak, tp = T[0], t2
    return dict(cook_min=cook_t / 60, over=peak - pull, peak_min=tp / 60, surf_at_pull=None)

res = {}
sear = run(4.0, 230.0, 50.0)
thin = run(2.0, 230.0, 50.0)
thick = run(6.0, 230.0, 50.0)
gentle = run(4.0, 100.0, 50.0)
sous = run(4.0, 54.0, 53.9, T0=5.0, sous=True, rest_s=1800)
for k, v in dict(sear4=sear, thin2=thin, thick6=thick, gentle90=gentle, sous54=sous).items():
    print("%-9s cook=%.1f min overshoot=%.2f C peak at %.1f min" % (k, v['cook_min'], v['over'], v['peak_min']))
res["c1_sear_has_real_carryover"] = sear['over'] > 3.0
res["c2_thinner_carries_more_not_less"] = thin['over'] > sear['over'] >= thick['over']
res["c3_gentler_sear_trims_carryover_under_25pct"] = 0.75 * sear['over'] < gentle['over'] < sear['over']
res["c4_sous_vide_no_carryover"] = sous['over'] < 0.2
res["c5_peak_arrives_within_rest_window"] = 0 < sear['peak_min'] < 30
# target accuracy: pull at target-carryover lands on target; pulling AT target overshoots
# scan pull temperatures 35..50 (pulls near the start are degenerate: the slab is mostly raw) for the peak closest to 50
cands = [(abs(p / 2 + run(4.0, 230.0, p / 2)['over'] - 50.0), p / 2) for p in range(70, 101)]
pull_t = min(cands)[1]
land = run(4.0, 230.0, pull_t)
p47 = 47.0 + run(4.0, 230.0, 47.0)['over']
res["c6_pulling_3C_early_trims_peak_by_under_2C_and_still_overshoots"] = 50.0 < p47 and (50 + sear['over'] - p47) < 2.0 and pull_t <= 35.0
print("pull at 50 -> peak %.1f ; pull at %.2f -> peak %.2f ; naive 'pull 3 under' -> peak %.1f" % (50 + sear['over'], pull_t, pull_t + land['over'], 47 + run(4.0, 230.0, 47.0)['over']))
for k, v in res.items(): print(k, v)
print("RESULT:", "PASS" if all(res.values()) else "FAIL",
      "carryover C: sear4cm=%.1f thin2cm=%.1f thick6cm=%.1f gentle=%.1f sous=%.2f; peak after %.1f min" %
      (sear['over'], thin['over'], thick['over'], gentle['over'], sous['over'], sear['peak_min']))
