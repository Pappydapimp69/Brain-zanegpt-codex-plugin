# Deterministic: a reaction pause (hold) over a gliding film score. Two mute mechanisms:
#  glide  - level glides to 0 over G seconds on pause, glides back over G seconds on resume (E2: zeroing levels)
#  fast   - separate mute path: release in R seconds, snap back on resume
# Metrics per pause of P seconds: leak = level integral during pause that should be silent,
# lost = level deficit integral after resume (score missing under the film), in level-seconds.
G, R, DT = 2.0, 0.15, 0.01

def level_glide(t, P):          # t seconds since pause start
    if t < P: return max(0.0, 1 - t / G)
    return min(1.0, max(0.0, 1 - P / G) + (t - P) / G)    # glide up from the level reached when the pause ended

def level_fast(t, P):
    if t < P: return max(0.0, 1 - t / R)
    return 1.0

def metrics(fn, P):
    leak = lost = 0.0
    n = int((P + 3 * G) / DT)
    for i in range(n):
        t = i * DT
        v = fn(t, P)
        if t < P: leak += v * DT
        else: lost += (1 - v) * DT
    return leak, lost

# Caption gaps in the 2:00 film are 0.4-0.85 s (reaction-cut lesson); authored holds are P.
rows = {}
for P in (0.5, 1.0, 2.0, 4.0):
    g = metrics(level_glide, P); f = metrics(level_fast, P)
    rows[P] = (g, f)
    print(f"P={P}: glide leak {g[0]:.2f} lost {g[1]:.2f} | fast leak {f[0]:.3f} lost {f[1]:.2f}")
# six reaction pauses of 1.0 s (the film's six triggers)
six_glide = sum(metrics(level_glide, 1.0)[0] for _ in range(6)); six_fast = sum(metrics(level_fast, 1.0)[0] for _ in range(6))
print(f"six 1.0 s pauses leaked level-seconds: glide {six_glide:.2f} fast {six_fast:.3f}")
ok = (rows[1.0][0][0] > 0.4 and rows[1.0][1][0] < 0.1 and rows[0.5][1][0] < 0.1
      and rows[4.0][0][0] <= 1.05 and rows[4.0][0][1] > 0.4 and rows[0.5][0][1] < rows[4.0][0][1]
      and rows[1.0][1][1] == 0.0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} 1.0 s pause leaks {rows[1.0][0][0]:.2f} level-s via glide vs {rows[1.0][1][0]:.3f} fast; glide leaves {rows[1.0][0][1]:.2f} level-s missing after resume vs {rows[1.0][1][1]:.2f}; 4 s pause loses {rows[4.0][0][1]:.2f} after resume, 0.5 s only {rows[0.5][0][1]:.2f}")
