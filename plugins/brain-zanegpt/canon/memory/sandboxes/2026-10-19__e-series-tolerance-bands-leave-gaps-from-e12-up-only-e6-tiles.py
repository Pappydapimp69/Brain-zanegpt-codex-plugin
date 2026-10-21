"""E-series resistor values (IEC 60063): do the +/- tolerance bands of adjacent preferred
values overlap, so any resistance in a decade is within tolerance of some preferred value?
E6/E12/E24 use the published rounded tables, E48/E96/E192 the 3-digit rounding of 10^(k/N).
Stdlib only, deterministic."""
E24 = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91]
E12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]
E6 = [10, 15, 22, 33, 47, 68]
def gen(n):
    return [round(10 ** (k / n) * 100) / 10 for k in range(n)]      # 3 significant digits, 100..999 -> /10
SERIES = {"E6": (E6, 0.20), "E12": (E12, 0.10), "E24": (E24, 0.05),
          "E48": (gen(48), 0.02), "E96": (gen(96), 0.01), "E192": (gen(192), 0.005)}

def uncovered(vals, tol, steps=200000):
    vals = sorted(vals) + [vals[0] * 10]                               # wrap to next decade
    bad = 0
    lo, hi = vals[0], vals[-1]
    for i in range(steps):
        r = lo * (hi / lo) ** (i / steps)
        if not any(abs(r - v) <= tol * v + 1e-9 for v in vals):
            bad += 1
    return bad / steps

rows = {}
for name, (vals, tol) in SERIES.items():
    v = sorted(vals) + [sorted(vals)[0] * 10]
    worst_step = max(v[i + 1] / v[i] for i in range(len(v) - 1))
    gap = uncovered(vals, tol)
    # bands touch iff v_i(1+t) >= v_{i+1}(1-t)
    touch = all(v[i] * (1 + tol) >= v[i + 1] * (1 - tol) - 1e-9 for i in range(len(v) - 1))
    rows[name] = (worst_step, touch, gap)
    print(f"{name}: tol +/-{tol*100:g}%, worst adjacent step {100*(worst_step-1):.1f}%, every adjacent pair of bands touches {touch}, uncovered share of decade {100*gap:.2f}%")

tiled = [n for n, r in rows.items() if r[1] and r[2] == 0]
untiled = [n for n, r in rows.items() if not r[1] and r[2] > 0]
ok = tiled == ["E6", "E12", "E24"] and untiled == ["E48", "E96", "E192"]
print(f"RESULT: {'PASS' if ok else 'FAIL'} bands tile the decade for {tiled} but leave gaps for {untiled} "
      f"(uncovered {', '.join(f'{n} {100*rows[n][2]:.1f}%' for n in untiled)})")
