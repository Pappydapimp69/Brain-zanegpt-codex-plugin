"""Apply DARK-ADAPTATION/campfire kernel as a game mechanic: is the night-sight cost
'in proportion to how long the player looked at the fire'? The kernel's threshold
model: rod floor -6 log cd/m2, elevation = 5 x bleach fraction, S2 recovery 0.23
log/min (under 45). Targets back-solved from the kernel's own numbers: starlit woods
-4.0, overcast canopy -5.5 (glance 0.2 -> canopy 2.17 min; stare 0.9 -> 10.9 / 17.4).
Added assumption (stated, not from the kernel): bleach builds toward the fire's
equilibrium 0.9 as B = 0.9 (1 - exp(-t/tau_b)) with tau_b = 3.98 s, fitted so a 1 s
glance gives the kernel's 0.2; between looks pigment regenerates with tau_r = 400 s
(order of Rushton's rhodopsin time constant). Deterministic, 0.1 s steps.
PREDICTION (written before running): canopy cost saturates: a 120 s stare costs under
25% more than a 10 s stare; ten 1 s glances 30 s apart cost within 15% of one 10 s
stare; so cost tracks exposure only over the first ~10 s."""
import math
FLOOR, ELEV, SLOPE, BMAX, TAUB, TAUR, DT = -6.0, 5.0, 0.23, 0.9, 3.98, 400.0, 0.1
TARGETS = {"starlit woods": -4.0, "overcast canopy": -5.5}

def bleach_after(schedule):
    """schedule: list of (seconds, looking_at_fire). Returns bleach fraction at the end."""
    b = 0.0
    for secs, on in schedule:
        for _ in range(int(round(secs / DT))):
            if on: b += (BMAX - b) * DT / TAUB
            else:  b -= b * DT / TAUR
    return b

def minutes_to_see(b, target):
    need = FLOOR + ELEV * b - target
    return max(0.0, need / SLOPE)

def report(name, sched):
    b = bleach_after(sched)
    m = {t: minutes_to_see(b, v) for t, v in TARGETS.items()}
    print(f"{name:34s} bleach {b:.3f}  starlit {m['starlit woods']:5.2f} min  canopy {m['overcast canopy']:5.2f} min")
    return m["overcast canopy"]

c = {}
for s in (1, 2, 5, 10, 20, 60, 120):
    c[s] = report(f"stare {s:3d} s", [(s, True)])
glances = report("ten 1 s glances, 30 s apart", [(1, True), (30, False)] * 9 + [(1, True)])
spaced = report("ten 1 s glances, 5 min apart (break)", [(1, True), (300, False)] * 9 + [(1, True)])
sat = c[120] / c[10] - 1
rel = abs(glances - c[10]) / c[10]
print(f"cost ratio exposure 120 s / 10 s = 12x, canopy minutes {c[120]:.2f} / {c[10]:.2f} = {c[120]/c[10]:.2f}x")
ok = sat < 0.25 and rel < 0.15
print(f"RESULT: {'PASS' if ok else 'FAIL'} 120 s stare costs {sat:.0%} more than 10 s; ten spaced-30s glances "
      f"{glances:.2f} min vs 10 s stare {c[10]:.2f} ({rel:.0%} apart); 5-min spacing {spaced:.2f} min")
