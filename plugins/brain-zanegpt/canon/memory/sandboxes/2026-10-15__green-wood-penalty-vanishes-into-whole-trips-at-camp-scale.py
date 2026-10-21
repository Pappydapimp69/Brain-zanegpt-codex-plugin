"""Train kernel (apply): FIREWOOD/moisture (green wood at 50% moisture gives 56%
of seasoned heat per kg but 90% per log; count what the player counts) applied
to a camp night where the fire is fed one log per action (sevin E15's 'feed'
action at the campfire) and wood is gathered in trips.
Question: what does green wood cost the player - feeds, or carrying?
Exact arithmetic, no rng. Net heat per log from the kernel's formula with a
2 kg dry-mass log: q = (19 (1-m) - 2.443 m) * 2 / (1-m) MJ. A night needs 300 MJ
into the fire (assumed). Carry limits: WEIGHT-limited (20 kg a trip) or
COUNT-limited (one log per gather action, SEVEN 1.15.0's rule).
PREDICTION (written before running): green (m 0.5) vs seasoned (m 0.2): feeds
+11%; weight-limited trips +75-80%; count-limited trips +11%; at m 0.65 feeds
+27% and weight-limited trips about 2.6x; so if the game counts logs per action,
green wood is nearly free, and the cost only appears when the carry is by
weight.
"""
import math, sys
print("python", sys.version.split()[0])
def per_log(m): return (19 * (1 - m) - 2.443 * m) * 2 / (1 - m)
def wet_kg(m): return 2 / (1 - m)
NEED, CARRY = 300.0, 20.0
def night(m):
    logs = math.ceil(NEED / per_log(m))
    per_trip_w = int(CARRY // wet_kg(m))
    return logs, math.ceil(logs / per_trip_w), logs          # feeds, weight trips, count trips (1 log/action)
R = {m: night(m) for m in (0.12, 0.20, 0.35, 0.50, 0.65)}
for m, (f, tw, tc) in R.items():
    print(f"m {m:.2f}: {per_log(m):5.2f} MJ/log, {wet_kg(m):5.2f} kg/log -> feeds {f}, weight-limited trips {tw}, gather actions {tc}")
s, g, v = R[0.20], R[0.50], R[0.65]
feeds_g = g[0] / s[0] - 1; trips_g = g[1] / s[1]; trips_v = v[1] / s[1]; feeds_v = v[0] / s[0] - 1
print(f"green vs seasoned: feeds {feeds_g:+.0%}, weight trips x{trips_g:.2f}; m 0.65: feeds {feeds_v:+.0%}, weight trips x{trips_v:.2f}")
c = [0.08 <= feeds_g <= 0.14, 1.70 <= trips_g <= 1.85, abs(g[2] / s[2] - 1 - feeds_g) < 1e-9, 0.22 <= feeds_v <= 0.32, 2.3 <= trips_v <= 2.9]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; green(0.5) feeds {feeds_g:+.0%}, weight-limited trips x{trips_g:.2f}, count-limited +{feeds_g:.0%}; m 0.65 feeds {feeds_v:+.0%}, trips x{trips_v:.2f}")
