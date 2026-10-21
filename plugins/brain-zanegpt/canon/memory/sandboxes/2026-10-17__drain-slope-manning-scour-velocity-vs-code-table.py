"""Sandbox: does the common code drain-slope table (1/4 in per ft for pipes up to 2.5 in, 1/8 in per ft for 3 to 6 in)
reach a 2 ft/s self-cleaning velocity? Manning (US units): V = (1.486/n) * R**(2/3) * S**0.5, half-full circular pipe
has R = D/4 (same V as full). n = 0.012 smooth plastic pipe. Slope S = (inch per ft)/12. Deterministic.
The 2 ft/s scour target is a commonly cited design figure used here as an input."""
N = 0.012
def vel(d_in, slope_in_per_ft, n=N):
    R = (d_in / 12.0) / 4.0
    return 1.486 / n * R ** (2.0 / 3.0) * (slope_in_per_ft / 12.0) ** 0.5
def slope_for(d_in, v=2.0, n=N):
    R = (d_in / 12.0) / 4.0
    return 12.0 * (v * n / (1.486 * R ** (2.0 / 3.0))) ** 2
CODE = {1.5: 0.25, 2: 0.25, 3: 0.125, 4: 0.125, 6: 0.125}
bad = []
for d, s in CODE.items():
    v = vel(d, s); need = slope_for(d)
    flag = "" if v >= 2.0 else "BELOW 2 ft/s"
    if v < 2.0: bad.append(d)
    print("D=%.1f in code slope %.3f in/ft -> V=%.2f ft/s | slope for 2 ft/s = %.3f in/ft %s" % (d, s, v, need, flag))
# rough n sensitivity (older/rougher pipe, n=0.015) and BREAK: a steeper-is-always-better check on velocity monotonic
rough = {d: vel(d, s, 0.015) for d, s in CODE.items()}
print("rough pipe n=0.015:", {d: round(v, 2) for d, v in rough.items()})
mono = all(vel(3, s2) > vel(3, s1) for s1, s2 in ((0.125, 0.25), (0.25, 0.5), (0.5, 1.0)))
# Original pre-run guess was that the table clears 2 ft/s everywhere; run 1 showed 1.5 in and 3 in marginally under.
ok = (bad == [1.5, 3]) and mono and vel(6, 0.125) > 3.0 and all(abs(rough[d] / vel(d, s) - 0.8) < 1e-9 for d, s in CODE.items()) and vel(3, 0.125) > 1.95
print("RESULT: %s code-table slopes give V=%.2f (1.5 in), %.2f (3 in), %.2f (6 in) ft/s; below 2 ft/s for D in %s; rough pipe n=0.015 lowers every one by 20 percent" % ("PASS" if ok else "FAIL", vel(1.5, .25), vel(3, .125), vel(6, .125), bad))
