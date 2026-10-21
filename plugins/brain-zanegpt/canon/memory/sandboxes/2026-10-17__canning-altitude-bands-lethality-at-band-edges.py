"""Sandbox: do stepped altitude time additions for boiling-water canning keep lethality >= sea level
at every altitude in a band? Lethality ratio vs sea level for time t at boiling point bp:
   L = t * 10**((bp - 100)/z)   (z = 10 C, the usual reference z for the target organism)
Boiling point drops BP_SLOPE C per metre (about 1 C per 300 m). Band table is an input (public
home-canning guidance for processes up to 20 min): feet band -> minutes added.
Deterministic: altitudes enumerated every 50 ft."""
BANDS = [(0, 1000, 0), (1001, 3000, 5), (3001, 6000, 10), (6001, 8000, 15), (8001, 10000, 20)]
Z = 10.0
BP_SLOPE = 1.0 / 300.0   # C per metre
FT = 0.3048

def bp(alt_ft):
    return 100.0 - BP_SLOPE * alt_ft * FT

def add(alt_ft):
    for lo, hi, m in BANDS:
        if lo <= alt_ft <= hi:
            return m
    raise ValueError(alt_ft)

def ratio(base, alt_ft, extra):
    return (base + extra) / base * 10 ** ((bp(alt_ft) - 100.0) / Z)

for base in (10, 20):
    worst = min((ratio(base, a, add(a)), a) for a in range(0, 10001, 50))
    print("base", base, "min lethality ratio %.3f at %d ft" % worst)
    for lo, hi, m in BANDS[1:]:
        print("   band", lo, hi, "+%d" % m, "ratio at low edge %.3f, high edge %.3f, no-add high edge %.3f" % (
            ratio(base, lo, m), ratio(base, hi, m), ratio(base, hi, 0)))
# Original prediction (pre-run): band additions keep ratio >= 1 everywhere. Run 1 REFUTED it (and exposed a bug: ratio
# was not divided by the sea-level time). Corrected claim tested below: the stepped additions do NOT hold equal
# lethality; they restore only part of it, and equal lethality needs time * 10**((100-bp)/z).
def need(base, alt_ft):
    return base * 10 ** ((100.0 - bp(alt_ft)) / Z)
w10 = min(ratio(10, a, add(a)) for a in range(0, 10001, 50))
top3000 = ratio(10, 3000, 5)
need3000 = need(10, 3000)
need10000 = need(10, 10000)
Z = 6.0
w10z6 = min(ratio(10, a, add(a)) for a in range(0, 10001, 50))
Z = 10.0
print("equal-lethality time for a 10 min process: %.1f min at 3000 ft (table says 15), %.1f min at 10000 ft (table says 30)" % (need3000, need10000))
below = [a for a in range(1001, 10001, 50) if ratio(10, a, add(a)) < 1.0]
print("altitudes (50 ft grid) with ratio < 1: %d of %d; first %d ft" % (len(below), len(range(1001, 10001, 50)), below[0]))
ok = (ratio(10, 1001, 5) > 1.0 and top3000 < 1.0 and w10 < 0.5 and need3000 > 15 and need10000 > 30 and w10z6 < w10)
print("RESULT: %s stepped additions leave lethality at %.2f of sea level at 3000 ft and %.2f at 10000 ft (10 min base, z 10 C); equal lethality needs %.1f and %.1f min; z 6 C worsens worst case to %.2f" % ("PASS" if ok else "FAIL", top3000, w10, need3000, need10000, w10z6))
