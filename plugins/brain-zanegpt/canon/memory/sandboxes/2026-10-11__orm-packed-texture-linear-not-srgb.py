"""Sandbox (train kernel, 3D-MODELING): glTF metallicRoughnessTexture packs
roughness in GREEN and metalness in BLUE (8-bit, LINEAR data). Tests what the
packing preserves and where it breaks: (1) correct linear decode round trip,
(2) texture wrongly flagged sRGB (colour) so the sampler gamma-decodes it,
(3) G/B swapped, (4) bilinear filter between texels, linear vs sRGB-decoded.
Deterministic, stdlib only."""

def to_byte(x): return round(x * 255)
def srgb_to_lin(b):
    c = b / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lin_to_srgb_byte(l):
    c = 12.92 * l if l <= 0.0031308 else 1.055 * l ** (1 / 2.4) - 0.055
    return round(c * 255)

def pack(rough, metal, ao=1.0): return (to_byte(ao), to_byte(rough), to_byte(metal))
def unpack_linear(t): return (t[1] / 255, t[2] / 255)          # (rough, metal)
def unpack_as_srgb(t): return (srgb_to_lin(t[1]), srgb_to_lin(t[2]))
def unpack_swapped(t): return (t[2] / 255, t[1] / 255)

# material values: smooth metal, rough dielectric, and mid-range values
mats = [(0.0, 1.0), (1.0, 0.0), (0.2, 1.0), (0.8, 0.0), (0.5, 0.5), (0.35, 0.65)]
res = {}

# 1) correct linear decode
e1 = max(max(abs(r - ur), abs(m - um)) for r, m in mats for ur, um in [unpack_linear(pack(r, m))])
res['linear'] = e1
# 2) sRGB mis-flag (BREAK: endpoints 0/1 are immune, mid values are not)
errs = {(r, m): max(abs(r - a), abs(m - b)) for r, m in mats for a, b in [unpack_as_srgb(pack(r, m))]}
e2 = max(errs.values()); endpoints_ok = errs[(0.0, 1.0)] < 1e-9 and errs[(1.0, 0.0)] < 1e-9
res['srgb_mid'] = errs[(0.5, 0.5)]
# 3) swapped G/B: error on every non-symmetric material
e3 = sum(1 for r, m in mats if max(abs(r - unpack_swapped(pack(r, m))[0]), abs(m - unpack_swapped(pack(r, m))[1])) > 0.01)
# 4) bilinear midpoint between texel A(0.2 rough) and B(0.8 rough), t=0.5
a, b = pack(0.2, 1.0), pack(0.8, 0.0)
lin_mid = (a[1] + b[1]) / 2 / 255                      # filter raw linear data: 0.5
srgb_mid = srgb_to_lin(a[1]) / 2 + srgb_to_lin(b[1]) / 2   # filter after gamma decode
print(f"1 linear round-trip max err {e1:.5f} (limit 1/510={1/510:.5f})")
print(f"2 sRGB misflag: max err {e2:.3f}; at 0.5 rough/metal -> {unpack_as_srgb(pack(.5,.5))[0]:.3f}; endpoints immune={endpoints_ok}")
print(f"3 swapped G/B wrong for {e3}/{len(mats)} materials")
print(f"4 bilinear mid rough: linear {lin_mid:.3f} vs sRGB-decoded {srgb_mid:.3f}")
ok = e1 <= 1/510 + 1e-9 and e2 > 0.25 and endpoints_ok and e3 == 5 and abs(lin_mid - 0.5) < 0.01 and abs(srgb_mid - 0.5) > 0.1
print(f"RESULT: {'PASS' if ok else 'FAIL'} linear err {e1:.4f}; sRGB misflag err {e2:.3f} (endpoints immune); swap wrong {e3}/6; bilinear {lin_mid:.2f} vs {srgb_mid:.2f}")
