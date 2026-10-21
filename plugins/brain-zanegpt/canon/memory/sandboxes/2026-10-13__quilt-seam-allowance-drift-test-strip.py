# Prediction (before run): a quilt row of n blocks cut at finished+0.5 in (nominal 1/4 in seam) sews to 6n+0.5 in
# when the sewn seam is exactly 1/4 in. If the real seam is 1/16 in too wide on every seam, the row comes up short
# by 2*(1/16)*(n-1) = 0.125*(n-1) in: 1.375 in for n=12 (about 1/4 block). A test strip of 4 pieces measured
# once recovers the real seam to within 0.01 in, so cutting to the corrected size removes the drift. BREAK: with
# per-seam errors that alternate +1/16, -1/16 (a wandering seam), the drift cancels and a test-strip correction
# would add error rather than remove it.
FIN = 6.0; NOM = 0.25
def row_width(n, cut, sa): return n * cut - 2 * sa * (n - 1)
def drift(n, sa): return row_width(n, FIN + 2 * NOM, sa) - (n * FIN + 2 * NOM)
for n in (4, 8, 12):
    print("S1 n=%2d seam 0.3125: drift %.4f in; seam 0.1875: drift %.4f in; exact: %.4f" % (n, drift(n, 0.3125), drift(n, 0.1875), drift(n, 0.25)))
# S2 test strip: sew 4 pieces cut 6.5, measure, infer seam
strip = row_width(4, 6.5, 0.3125)
inferred = (4 * 6.5 - strip) / (2 * 3)
cut2 = FIN + 2 * inferred
fixed_row = row_width(12, cut2, 0.3125)
print("S2 strip width %.4f inferred seam %.4f corrected cut %.4f 12-row width %.4f target %.4f" % (strip, inferred, cut2, fixed_row, 12 * FIN + 2 * inferred))
# S3 BREAK: wandering seam alternating +/- 1/16; per-seam loss sums
def wander_row(n, cut):
    w = n * cut
    for i in range(n - 1): w -= 2 * (0.25 + (0.0625 if i % 2 == 0 else -0.0625))
    return w
wand = wander_row(12, 6.5) - (12 * 6.0 + 0.5)
# strip of 4 sees seams 0,1,2 -> +,-,+ : net bias +1/16 over 3 seams, so inferred seam is high by 1/48
strip_w = 4 * 6.5 - sum(2 * (0.25 + (0.0625 if i % 2 == 0 else -0.0625)) for i in range(3))
inf_w = (4 * 6.5 - strip_w) / 6
cut_w = FIN + 2 * inf_w
wand_fixed = wander_row(12, cut_w) - (12 * FIN + 2 * inf_w)
print("S3 wandering seam drift uncorrected %.4f; after strip correction (inferred %.4f) drift %.4f" % (wand, inf_w, wand_fixed))
ok1 = abs(drift(12, 0.3125) + 1.375) < 1e-9 and abs(drift(12, 0.25)) < 1e-9
ok2 = abs(inferred - 0.3125) < 0.01 and abs(fixed_row - (12 * FIN + 2 * inferred)) < 0.01
ok3 = abs(wand_fixed) > abs(wand) or abs(wand_fixed) > 0.05
print("RESULT: %s 12-block row short by %.3f in at seam 5/16, test strip infers %.4f and removes it (residual %.4f); wandering seam drift %.3f before and %.3f after correction"
      % ("PASS" if (ok1 and ok2 and ok3) else "FAIL", -drift(12, 0.3125), inferred, fixed_row - (12 * FIN + 2 * inferred), wand, wand_fixed))
