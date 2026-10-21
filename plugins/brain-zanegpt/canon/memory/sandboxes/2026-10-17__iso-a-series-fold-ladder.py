# ISO 216 A-series: A0 is 841 x 1189 mm (~1 m^2, ratio sqrt2); each next size halves the longer side, rounded DOWN to whole mm.
# Prediction (before run): halving+floor from A0 reproduces the published A1..A8 exactly (594x841, 420x594, 297x420, 210x297,
# 148x210, 105x148, 74x105, 52x74); areas halve to within 1%; the aspect ratio drifts from sqrt2 by <1% at every size; and the break
# case, rounding to NEAREST mm, must produce at least one size that differs from the published list.
import math
PUB = [(841,1189),(594,841),(420,594),(297,420),(210,297),(148,210),(105,148),(74,105),(52,74)]
def ladder(rnd):
    w, h = 841, 1189; out = [(w, h)]
    for _ in range(8):
        w, h = rnd(h / 2), w          # new long side = old short side, new short side = old long / 2
        out.append((w, h))
    return out
floor = ladder(math.floor); near = ladder(lambda x: int(x + 0.5))
print("floor matches published:", floor == PUB)
print("nearest rounding differs at sizes:", [i for i, (a, b) in enumerate(zip(near, PUB)) if a != b])
area_err = max(abs(floor[i + 1][0] * floor[i + 1][1] / (floor[i][0] * floor[i][1]) - 0.5) / 0.5 for i in range(8))
ratio_err = max(abs(h / w - math.sqrt(2)) / math.sqrt(2) for w, h in floor)
a0 = floor[0][0] * floor[0][1] / 1e6
print("A0 area %.4f m2; max area-halving error %.3f%%; max ratio error %.3f%%" % (a0, 100 * area_err, 100 * ratio_err))
# imposition: a folded A3 sheet gives 4 A4 pages per sheet; 20-page booklet needs 5 sheets, A4 booklet folded from A3
sheets = -(-20 // 4)
ok = floor == PUB and near != PUB and area_err < 0.01 and ratio_err < 0.01 and sheets == 5
print("RESULT:", "PASS" if ok else "FAIL", "floor halving reproduces A0..A8; nearest rounding differs at %s; area error %.2f%%, ratio error %.2f%%, A0 %.3f m2, 20-page A4 booklet = %d A3 sheets" % ([i for i, (a, b) in enumerate(zip(near, PUB)) if a != b], 100 * area_err, 100 * ratio_err, a0, sheets))
