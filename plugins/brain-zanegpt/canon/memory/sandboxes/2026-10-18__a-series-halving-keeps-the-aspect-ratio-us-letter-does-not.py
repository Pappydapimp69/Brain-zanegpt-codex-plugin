"""Sandbox: a sheet whose sides are in ratio 1:sqrt(2) keeps its shape when cut in half across the long side.
Checks (1) the halving rule reproduces the ISO 216 A0..A8 millimetre table, (2) US Letter does not keep its shape,
(3) the copier scale that fits A4 onto A3 and back. Prediction (before run): rule reproduces all 9 ISO sizes exactly
with floor rounding; Letter's ratio drifts by >15% after one halving while A-series drifts <1% through A8;
A4->A3 scale is 141% (sqrt2) and A3->A4 71%."""
import math
ISO = {0: (841, 1189), 1: (594, 841), 2: (420, 594), 3: (297, 420), 4: (210, 297), 5: (148, 210), 6: (105, 148), 7: (74, 105), 8: (52, 74)}
def halve(w, h): return (h // 2, w) if h // 2 < w else (w, h // 2)    # cut across the long side, floor to the mm
sizes = {0: ISO[0]}
for n in range(1, 9): sizes[n] = halve(*sizes[n - 1])
match = [n for n in sizes if sizes[n] == ISO[n]]
print("A-series from A0 by floor-halving:", sizes, "matches ISO:", match)
ratio = lambda w, h: max(w, h) / min(w, h)
drift = {n: abs(ratio(*sizes[n]) - math.sqrt(2)) / math.sqrt(2) * 100 for n in sizes}
print("A-series ratio drift % by n:", {n: round(v, 2) for n, v in drift.items()})
L = (8.5, 11.0); L1 = (5.5, 8.5); L2 = (4.25, 5.5)                          # Letter, half-letter, quarter by folding
letter_drift = [abs(ratio(*s) - ratio(*L)) / ratio(*L) * 100 for s in (L, L1, L2)]
print("Letter ratio", [round(ratio(*s), 3) for s in (L, L1, L2)], "drift % vs original", [round(v, 1) for v in letter_drift])
scale_up = sizes[3][1] / sizes[4][1]; scale_down = sizes[4][1] / sizes[3][1]
print(f"A4->A3 scale {scale_up*100:.1f}%  A3->A4 {scale_down*100:.1f}%  (sqrt2 = {math.sqrt(2)*100:.1f}%)")
# BREAK: area check - halving 1 m^2 A0 gives A4 area 1/16 m^2 within rounding
a4_area = sizes[4][0] * sizes[4][1] / 1e6
print(f"A4 area {a4_area:.5f} m^2 vs 1/16 = {1/16:.5f}")
ok = len(match) == 9 and max(drift.values()) < 1.0 and letter_drift[1] > 15 and abs(scale_up * 100 - 141.4) < 0.5 and abs(scale_down * 100 - 70.7) < 0.5 and abs(a4_area - 1 / 16) < 0.002
print(f"RESULT: {'PASS' if ok else 'FAIL'} floor-halving reproduces ISO A0-A8 ({len(match)}/9); A-series ratio drift max {max(drift.values()):.2f}% ; Letter half-fold drift {letter_drift[1]:.1f}% ; A4->A3 {scale_up*100:.1f}%, A3->A4 {scale_down*100:.1f}%; A4 area {a4_area:.5f} vs 0.06250")
