# Sandbox (COLOR-SCIENCE seed): sRGB transfer function per IEC 61966-2-1 (the standard's piecewise curve).
# Prediction (written before running): averaging black (0) and white (255) as bytes gives 128, whose linear
# luminance is about 0.216, not 0.5; the linear-light mean encodes to byte 188 (+-1); round-tripping all 256
# sRGB codes through an 8-bit LINEAR buffer merges at least 20 distinct codes (dark end); a 16-bit linear
# buffer merges none; a smooth-ramp downscale by 2x2 averaging differs between the two methods by up to >=40 codes.
def to_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def to_srgb(l):
    v = 12.92 * l if l <= 0.0031308 else 1.055 * l ** (1 / 2.4) - 0.055
    return v * 255.0
mid_bytes = (0 + 255) // 2 + 1                      # 128
lin_of_mid = to_lin(mid_bytes)
correct = round(to_srgb((to_lin(0) + to_lin(255)) / 2))
print("naive midpoint byte", mid_bytes, "= linear", round(lin_of_mid, 4), "; linear-light mean encodes to byte", correct)
def roundtrip(bits):
    top = (1 << bits) - 1
    seen = {}
    for c in range(256):
        q = round(to_lin(c) * top)
        back = round(to_srgb(q / top))
        seen[c] = back
    return 256 - len(set(seen.values()))
m8, m16 = roundtrip(8), roundtrip(16)
print("codes merged by 8-bit linear round trip", m8, "; by 16-bit", m16)
# checker-pattern downscale: alternating a,b pixels; compare naive vs linear average over many (a,b) pairs
worst = 0
for a in range(0, 256, 5):
    for b in range(0, 256, 5):
        naive = (a + b) / 2
        lin = to_srgb((to_lin(a) + to_lin(b)) / 2)
        worst = max(worst, abs(lin - naive))
print("worst naive-vs-linear downscale error in codes", round(worst, 1))
ok = abs(lin_of_mid - 0.216) < 0.005 and abs(correct - 188) <= 1 and m8 >= 20 and m16 == 0 and worst >= 40
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"naive mid 128 = {lin_of_mid:.3f} linear, linear mean = byte {correct}, 8-bit linear merges {m8} codes, 16-bit {m16}, worst downscale error {worst:.0f} codes")
