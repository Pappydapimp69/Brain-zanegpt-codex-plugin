"""Edge pass: ideas ACCESSIBILITY/keep-repetitive-screen-motion-out-of-the-2-to-5-second-period-band
(2.5-5 s whole-screen cycles are the most nauseating; worse with more screen moving) composed with
GAME-DESIGN/sound-first-then-sight-as-sanity-falls (visual effects arrive only in the deep stages,
stronger with depth). Deterministic. Four stages (shore, wading, chest-deep, undercurrent); visual
stages are the last two. Time share per stage: equal, and deep-heavy (0.15/0.2/0.3/0.35).
Effect designs for the visual stages (period ramps linearly with depth inside each stage):
  breath   whole-screen sway synced to a breathing rate rising 12 -> 30 /min (period 5.0 -> 2.0 s)
  swell    whole-screen 'undercurrent' swell, period 10 -> 6 s
  edge     the breath design applied only to the screen edge (area 0.15)
  jitter   small fast jitter, period 0.15 s, whole screen
  lurch    one-off lurches: no repetition (period undefined -> never in band)
Exposure = sum over visual time of (screen area moving) x [period in 2.5-5 s]; also in-band TIME share.
Predictions written before running:
 P1 the breath design keeps >= 60% of visual-stage time in the 2.5-5 s band.
 P2 edge-only cuts area-weighted exposure by >= 80% versus breath.
 P3 the slow swell (10 -> 6 s) never enters the band.
 P4 a deep-heavy time split raises breath's in-band share of ALL play time vs equal split.
"""
STEPS = 1000

def stage_periods(design, stage):  # stage 2 or 3 (chest-deep, undercurrent); periods across that stage
    out = []
    for k in range(STEPS):
        x = (stage - 2 + (k + 0.5) / STEPS) / 2  # 0..1 across the two visual stages
        if design in ("breath", "edge"):
            rate = 12 + (30 - 12) * x; out.append(60 / rate)
        elif design == "swell": out.append(10 - 4 * x)
        elif design == "jitter": out.append(0.15)
        else: out.append(None)
    return out

AREA = {"breath": 1.0, "swell": 1.0, "edge": 0.15, "jitter": 1.0, "lurch": 1.0}
SPLITS = {"equal": (0.25, 0.25, 0.25, 0.25), "deep-heavy": (0.15, 0.2, 0.3, 0.35)}
res = {}
for sname, w in SPLITS.items():
    for d in AREA:
        inband_vis = exposure = 0.0
        for st in (2, 3):
            ps = stage_periods(d, st)
            frac = sum(1 for p in ps if p is not None and 2.5 <= p <= 5.0) / STEPS
            inband_vis += w[st] * frac; exposure += w[st] * frac * AREA[d]
        vis = w[2] + w[3]
        res[(sname, d)] = (inband_vis / vis, inband_vis, exposure)
    print(sname + ": " + "  ".join(f"{d} vis-in-band {res[(sname,d)][0]:.2f} all-play {res[(sname,d)][1]:.2f} exposure {res[(sname,d)][2]:.3f}" for d in AREA))
p1 = res[("equal", "breath")][0] >= 0.60
p2 = res[("equal", "edge")][2] <= 0.2 * res[("equal", "breath")][2]
p3 = res[("equal", "swell")][0] == 0
p4 = res[("deep-heavy", "breath")][1] > res[("equal", "breath")][1]
checks = [("P1 breath >= 60% of visual time in band", p1), ("P2 edge-only cuts exposure >= 80%", p2),
          ("P3 slow swell never in band", p3), ("P4 deep-heavy raises all-play in-band share", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; breath in-band {res[('equal','breath')][0]:.2f} of visual time "
      f"(all play {res[('equal','breath')][1]:.2f} equal, {res[('deep-heavy','breath')][1]:.2f} deep-heavy); edge exposure "
      f"{res[('equal','edge')][2]:.3f} vs {res[('equal','breath')][2]:.3f}; swell {res[('equal','swell')][0]:.2f}; jitter {res[('equal','jitter')][0]:.2f}")
