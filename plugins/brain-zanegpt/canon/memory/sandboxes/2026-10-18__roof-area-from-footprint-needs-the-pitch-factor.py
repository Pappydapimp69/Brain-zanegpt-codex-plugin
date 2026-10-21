"""Roofing: surface area = footprint area x sqrt(1 + (rise/12)^2) (slope factor, from the Pythagorean
rafter length per 12 in of run). Shingles are sold in squares (100 sq ft); order = area x (1 + waste), rounded up
to a third of a square (one bundle). Compare ordering from the plan footprint x 1.10 waste against ordering
from the sloped area x 1.10 waste. A roof is 'short' when the footprint order is below the sloped need.
Deterministic arithmetic; pitch list covers common residential pitches."""
import math
def sf(rise): return math.sqrt(1 + (rise/12)**2)
def bundles(sq): return math.ceil(sq*3 - 1e-9)   # 3 bundles per square
WASTE = 1.10
footprint_sqft = 1800
rows = []
for rise in (2, 4, 5, 6, 8, 10, 12):
    area = footprint_sqft * sf(rise)
    need = bundles(area/100*WASTE)
    naive = bundles(footprint_sqft/100*WASTE)
    short = naive < need
    rows.append((rise, sf(rise), need, naive, short))
    print(f"{rise}/12 pitch: slope factor {sf(rise):.3f} need {need} bundles, footprint order {naive} -> {'SHORT '+str(need-naive) if short else 'ok'}")
shorts = [r for r in rows if r[4]]
first_short = min(r[0] for r in shorts) if shorts else None
# BREAK: a low pitch should NOT be short (2/12 factor 1.014 is covered by the 10% waste)
low_ok = not [r for r in rows if r[0] == 2][0][4]
# the 6/12 factor must be 1.118 (known value) and 12/12 1.414
known = abs(sf(6)-1.118) < 0.001 and abs(sf(12)-1.414) < 0.001
ok = low_ok and known and first_short is not None and first_short <= 5 and len(shorts) >= 4
print(f"RESULT: {'PASS' if ok else 'FAIL'} footprint order short on {len(shorts)} of {len(rows)} pitches, first short at {first_short}/12; 2/12 ok={low_ok}; factors 6/12={sf(6):.3f} 12/12={sf(12):.3f}")
