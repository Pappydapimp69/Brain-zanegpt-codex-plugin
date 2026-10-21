# Extension-ladder placement per the common 4:1 rule (OSHA 1926.1053: 1 horizontal per 4 vertical to the support point;
# side rails extend at least 3 ft above the landing). Lengths are along the ladder.
import math
LENGTHS = [16, 20, 24, 28, 32]
def plan(L):
    k = math.sqrt(1 + 1 / 16)            # ladder length to the support point per unit of support height
    h = (L - 3) / k                       # support height when 3 ft must stick out above it
    return h, h / 4
def angle_deg(h, b): return math.degrees(math.atan2(h, b))
rows = []
for L in LENGTHS:
    h, b = plan(L)
    naive_b = L / 4                       # common shortcut: a quarter of the whole ladder length
    rows.append((L, round(h, 2), round(b, 2), round(angle_deg(h, b), 2), round(naive_b, 2), round(naive_b - b, 2)))
    print(rows[-1])
ang = {r[3] for r in rows}
ok = all(abs(a - math.degrees(math.atan(4))) < 0.01 for a in ang) and all(r[5] > 0.7 for r in rows)
# the shortcut offset is too wide for every length and the surplus grows with length
grows = all(rows[i][5] < rows[i + 1][5] for i in range(len(rows) - 1))
ok = ok and grows
print("RESULT: %s every length sets at 75.96 deg with base offset = support height / 4; the L/4 shortcut over-offsets by %.2f to %.2f ft (+0.44 deg flatter), growing with length" % (
    "PASS" if ok else "FAIL", rows[0][5], rows[-1][5]))
