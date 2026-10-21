"""Cel loop 7 - limited animation (GGXrd: 'we just stopped using interpolations between key
frames. Every frame now is a key frame', Motomura GDC 2015): poses are HELD for 2 or 3 game
frames (on twos / threes) of a 60 Hz game. How evenly do held poses reach the eye on
displays that are not 60 Hz? A pose is visible from the first display refresh at or after
its game-frame start until the first refresh at or after the next pose starts (simple
latest-frame presentation, no frame pacing tricks). Exact rational arithmetic, no RNG.
Metric: max/min on-screen duration over 120 consecutive poses.
PREDICTION (written before running): 60 and 120 Hz show every pose for equal time (ratio
1.00); 144 Hz on twos alternates 4/5 refreshes (ratio 1.25); 50 Hz on twos shows some
poses for 1 refresh and others for 2 or more (ratio >= 2)."""
from fractions import Fraction as F
import math
def durations(hold, hz, n=120):
    starts = [F(k * hold, 60) for k in range(n + 1)]                      # pose k starts at game frame k*hold
    first_refresh = lambda t: F(math.ceil(t * hz), hz)                     # first refresh at or after t
    shown = [first_refresh(starts[k + 1]) - first_refresh(starts[k]) for k in range(n)]
    return [d for d in shown]
res = {}
for hold in (2, 3):
    for hz in (60, 120, 144, 165, 50):
        d = durations(hold, hz)
        lo, hi = min(d), max(d)
        res[(hold, hz)] = (hi / lo if lo > 0 else float("inf"), sorted(set(round(float(x) * hz) for x in d)))
        print(f"on {hold}s at {hz:3d} Hz: refreshes per pose {res[(hold, hz)][1]}, max/min {float(res[(hold, hz)][0]):.2f}")
ok = (res[(2, 60)][0] == 1 and res[(2, 120)][0] == 1 and abs(float(res[(2, 144)][0]) - 1.25) < 1e-9
      and float(res[(2, 50)][0]) >= 2)
print(f"RESULT: {'PASS' if ok else 'FAIL'} twos: 60Hz {float(res[(2,60)][0]):.2f}, 120Hz {float(res[(2,120)][0]):.2f}, "
      f"144Hz {float(res[(2,144)][0]):.2f}, 165Hz {float(res[(2,165)][0]):.2f}, 50Hz {float(res[(2,50)][0]):.2f}; "
      f"threes: 144Hz {float(res[(3,144)][0]):.2f}, 50Hz {float(res[(3,50)][0]):.2f}")
