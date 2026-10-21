"""Variable-first (measure the hidden floor/base, then set the knob) vs knob-first
on two linked problems: thermostat swing spec and curing dose.
PREDICTION (before first run): across a 3x3 thermostat grid (lag x spec) plus a
3-cell curing grid, variable-first meets spec in every feasible cell (0 failures)
while knob-first (band=spec; dose on total weight) fails in >= 50% of cells.
Break case: if the floor is measured at the wrong lag (half the real one) the
variable-first rule also fails, so 'always measure first' needs 'measure under
the deployed conditions'."""
def swing(band, lag, rate_up=0.1, rate_dn=0.05, steps=4000):
    T, on, hist, lo, hi = 20.0, True, [20.0]*(lag+1), 1e9, -1e9
    for i in range(steps):
        sensed = hist[-1-lag]
        if sensed >= 20.0 + band/2: on = False
        elif sensed <= 20.0 - band/2: on = True
        T += rate_up if on else -rate_dn
        hist.append(T)
        if i > steps//2: lo, hi = min(lo, T), max(hi, T)
    return hi - lo
def floor(lag): return swing(0.0, lag) - 0.0        # measured overshoot at band 0
def knob_first(spec, lag): return swing(spec, lag) <= spec
def var_first(spec, lag, measure_lag=None):
    f = floor(lag if measure_lag is None else measure_lag)
    band = spec - f
    if band <= 0: return True   # correctly declared infeasible, no false promise
    return swing(band, lag) <= spec + 1e-9
cells = [(s, l) for s in (0.5, 1.0, 2.0) for l in (5, 10, 20)]
kf = sum(not knob_first(s, l) for s, l in cells)
vf = sum(not var_first(s, l) for s, l in cells)
mis = sum(not var_first(s, l, measure_lag=l//2) for s, l in cells)
# curing: nitrite ppm in the meat = cure_g * 6.25% nitrite / meat_g. Target = 156 ppm (0.25% of MEAT weight).
def ppm_in_meat(cure_g, meat_g): return cure_g * 0.0625 / meat_g * 1e6
TARGET = ppm_in_meat(0.0025 * 1000, 1000)
cur = [(1000, 250), (1000, 100), (1000, 500)]       # (meat g, brine g)
def cure_knob(m, b):  return abs(ppm_in_meat(0.0025 * (m + b), m) - TARGET) / TARGET > 0.10   # dose on total weight
def cure_var(m, b):   return abs(ppm_in_meat(0.0025 * m, m) - TARGET) / TARGET > 0.10          # dose on meat weight
ck = sum(cure_knob(m, b) for m, b in cur); cv = sum(cure_var(m, b) for m, b in cur)
n = len(cells) + len(cur)
print("knob-first fails %d/%d  variable-first fails %d/%d  mismeasured-floor fails %d/%d" % (kf + ck, n, vf + cv, n, mis, len(cells)))
ok = (kf + ck) * 2 >= n and vf + cv == 0 and mis > 0
print("RESULT: %s knob-first %d/%d fail, variable-first %d/%d, floor measured at half lag %d/%d fail" % ("PASS" if ok else "FAIL", kf+ck, n, vf+cv, n, mis, len(cells)))
