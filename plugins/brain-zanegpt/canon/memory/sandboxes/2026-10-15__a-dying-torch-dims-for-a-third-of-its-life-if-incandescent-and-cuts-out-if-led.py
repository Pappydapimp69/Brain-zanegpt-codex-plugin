"""Gap (brain query flashlight / headlamp: 0). Horror games drain a torch
battery as a linear bar. What does a real torch do as its batteries die?
Exact arithmetic, no rng. Real relations used:
  incandescent bulb luminous flux ~ (V / V_rated)^3.4 (standard lamp rule of
  thumb; flux exponent 3.4 to 3.6);
  a regulated LED torch holds constant output until the cells fall below the
  driver's cut-off, then drops out.
ASSUMED alkaline AA discharge under a steady torch load: cell voltage falls
1.50 -> 1.20 V over the first 70% of runtime, then 1.20 -> 0.90 V over the last
30% (piecewise linear stand-in for a datasheet curve); 2 cells; incandescent
rated at 2.4 V (1.2 V per cell); LED driver cut-off 1.0 V per cell.
PREDICTION (written before running): the incandescent torch is far brighter
than rated at the start (> 2x), falls through its rated brightness around 70%
of runtime, and is under 25% of rated before the cells reach 0.9 V - a long
gradual dimming (useful for dread); the LED holds 100% to about 90% of runtime
then cuts out in one step (a cliff); a linear bar matches neither.
"""
import sys
print("python", sys.version.split()[0])
def v(f):
    return 1.50 - 0.30 * f / 0.70 if f <= 0.70 else 1.20 - 0.30 * (f - 0.70) / 0.30
def inc(f): return (v(f) / 1.2) ** 3.4
def led(f): return 1.0 if v(f) >= 1.0 else 0.0
fr = [i / 100 for i in range(0, 101)]
for f in (0, 0.25, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0):
    print(f"runtime {f:4.2f}: cell {v(f):.3f} V  incandescent {inc(f):5.2f} x rated  LED {led(f):.0f}  linear bar {1 - f:.2f}")
cross = next(f for f in fr if inc(f) <= 1.0)
quarter = next((f for f in fr if inc(f) <= 0.25), None)
cut = next(f for f in fr if led(f) == 0)
c = [inc(0) > 2, 0.65 <= cross <= 0.75, quarter is not None, 0.85 <= cut <= 0.95]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; incandescent starts {inc(0):.2f}x rated, passes rated at {cross:.2f} of runtime, under 25% at {quarter} (ends at {inc(1.0):.2f}x); LED full until {cut:.2f} then off")
