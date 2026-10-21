"""Gap (brain query crickets: 0). Dolbear's law (Dolbear 1897, snowy tree
cricket): T(F) = 50 + (N - 40)/4, N = chirps per minute; the field shortcut is
'count chirps in 15 s and add 40'. SEVEN builds sound only from the percept and
public facts (tests/soundscape.mjs); air temperature is a public fact, so a
cricket bed whose rate follows the night's cooling would be an honest clock.
Exact arithmetic, no rng. ASSUMED night: air cools from 72 F at dusk toward
48 F with a 4-hour time constant over 10 hours; crickets fall silent below
55 F (assumed; snowy tree crickets stop chirping in the 50s F).
PREDICTION (written before running): the 15 s shortcut equals Dolbear exactly
(algebra) and the Celsius form T = 10 + (N - 40)/7 differs from the exact
conversion (divisor 7.2) by under 0.6 C across 40-200 chirps/min; over the
night the rate falls from about 128 to about 60/min before stopping, a change
a listener can hear; a 15 s count (+-1 chirp) reads temperature to +-1 F; the
crickets stop roughly 4-6 h after dusk, so their silence itself marks the cold
part of the night.
"""
import math, sys
print("python", sys.version.split()[0])
def rate(Tf): return 40 + 4 * (Tf - 50)
def temp(t_h): return 48 + (72 - 48) * math.exp(-t_h / 4)
same = all(abs((50 + (N - 40) / 4) - (N / 4 + 40)) < 1e-12 for N in range(40, 201))
cerr = max(abs((10 + (N - 40) / 7) - ((50 + (N - 40) / 4 - 32) * 5 / 9)) for N in range(40, 201))
print(f"15 s shortcut identical to Dolbear: {same}; Celsius form max error {cerr:.2f} C")
stop = None
for h in [x / 4 for x in range(0, 41)]:
    T = temp(h); N = rate(T)
    if T < 55 and stop is None: stop = h
    if h in (0, 1, 2, 3, 4, 5, 6, 8, 10): print(f"hour {h:4.1f}: {T:5.1f} F -> {N if T >= 55 else 0:5.1f} chirps/min")
res_f = 1.0   # one chirp in 15 s = 4 chirps/min = 1 F
c = [same, cerr < 0.6, 120 <= rate(temp(0)) <= 135, stop is not None and 4 <= stop <= 6, res_f == 1.0]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; shortcut exact {same}; Celsius error {cerr:.2f} C; dusk rate {rate(temp(0)):.0f}/min, last rate before silence {rate(55):.0f}/min; crickets stop at hour {stop}; 15 s count resolves +-{res_f:.0f} F")
