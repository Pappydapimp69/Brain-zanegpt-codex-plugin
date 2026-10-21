"""Calligraphy: broad-nib stroke width = nib width * |sin(stroke angle - nib angle)|.
Checks thick/thin contrast by pen angle. Deterministic, stdlib only."""
import math
def w(stroke, nib): return abs(math.sin(math.radians(stroke - nib)))
ok = True
for nib in (0, 30, 45):   # nib 45 is the BREAK case: claim says contrast between V and H vanishes
    v, h = w(90, nib), w(0, nib)
    thickest = max(range(0, 180), key=lambda a: w(a, nib))
    ratio = v / h if h > 1e-12 else float("inf")
    print(f"nib {nib:>2}deg: vertical {v:.3f} horizontal {h:.3f} V/H {ratio:.2f} thickest at {thickest}deg")
    ok &= thickest == (nib + 90) % 180
ok &= abs(w(90, 30) / w(0, 30) - math.sqrt(3)) < 1e-9 and abs(w(90, 45) - w(0, 45)) < 1e-12 and w(0, 0) < 1e-12
print("RESULT: PASS thickest stroke = nib+90; 30deg nib gives V/H 1.73, 45deg gives 1.00, 0deg makes horizontals hairlines" if ok
      else "RESULT: FAIL")
