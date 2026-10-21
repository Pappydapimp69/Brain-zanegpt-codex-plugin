"""Sandbox: mip-mapping a glTF metallic-roughness material.

Question: the sRGB-lerp kernel says convert baseColor to linear before averaging.
Is that enough when a 2x2 footprint mixes a metal texel and a dielectric texel?
glTF packs metalness (blue) and roughness (green) as separate linear inputs, and the
shader derives  diffuse = base*(1-metal)  and  F0 = mix(0.04, base, metal).
Those derivations are products of two averaged inputs, so averaging the inputs
separately is not averaging the light.

Ground truth = average of the SHADED radiance of the texels (supersampling).
Methods (each averages its inputs, then shades once):
  A naive   : average baseColor in sRGB, average metal and rough (raw channel mip)
  B linear  : decode baseColor to linear, average; average metal and rough
  C derived : average linear diffuse albedo and F0 (precomputed per texel); average rough
Error = max relative error over RGB of output radiance vs truth.
Pure stdlib, deterministic.
"""
import math

def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def l2s(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def norm(v):
    m = math.sqrt(sum(x * x for x in v)); return [x / m for x in v]

def dot(a, b):
    return max(0.0, sum(x * y for x, y in zip(a, b)))

def shade(diff, f0, rough, L, V, N=(0, 0, 1)):
    """Cook-Torrance: Lambert + GGX D + Schlick F + Smith-Schlick G. Linear RGB out."""
    H = norm([l + v for l, v in zip(L, V)])
    nl, nv, nh, vh = dot(N, L), dot(N, V), dot(N, H), dot(V, H)
    a = max(rough * rough, 1e-4); a2 = a * a
    D = a2 / (math.pi * (nh * nh * (a2 - 1) + 1) ** 2)
    k = a / 2
    G = (nl / (nl * (1 - k) + k)) * (nv / (nv * (1 - k) + k))
    out = []
    for c in range(3):
        F = f0[c] + (1 - f0[c]) * (1 - vh) ** 5
        spec = D * F * G / max(4 * nl * nv, 1e-6)
        out.append((diff[c] / math.pi + spec) * nl)
    return out

def derive(base_lin, metal):
    diff = [b * (1 - metal) for b in base_lin]
    f0 = [0.04 * (1 - metal) + b * metal for b in base_lin]
    return diff, f0

def avg(vs):
    return [sum(v[i] for v in vs) / len(vs) for i in range(len(vs[0]))]

def rel_err(x, t):
    return max(abs(a - b) / max(b, 1e-9) for a, b in zip(x, t))

# view/light geometries
L = norm([0.0, -0.6, 1.0])
GEOS = {
    "diffuse-view": (L, norm([0.8, 0.5, 1.0])),      # far from mirror direction
    "specular-peak": (L, norm([0.0, 0.6, 1.0])),     # V = mirror of L about N
}

def run(name, texels):
    """texels: list of (base_srgb[3], metal, rough). Returns dict of errors."""
    res = {}
    for g, (Lv, Vv) in GEOS.items():
        truth = avg([shade(*derive([s2l(c) for c in b], m), r, Lv, Vv) for b, m, r in texels])
        mr = sum(t[1] for t in texels) / len(texels)
        rr = sum(t[2] for t in texels) / len(texels)
        # A: sRGB average of baseColor
        bA = [s2l(c) for c in avg([t[0] for t in texels])]
        A = shade(*derive(bA, mr), rr, Lv, Vv)
        # B: linear average of baseColor
        bB = avg([[s2l(c) for c in t[0]] for t in texels])
        B = shade(*derive(bB, mr), rr, Lv, Vv)
        # C: average derived diffuse albedo and F0
        ds, fs = zip(*[derive([s2l(c) for c in t[0]], t[1]) for t in texels])
        C = shade(avg(ds), avg(fs), rr, Lv, Vv)
        res[g] = {"A": rel_err(A, truth), "B": rel_err(B, truth), "C": rel_err(C, truth),
                  "truth": truth, "Bv": B}
        print(f"  {name:28s} {g:13s} A(sRGB)={res[g]['A']*100:8.2f}%  "
              f"B(linear base)={res[g]['B']*100:8.2f}%  C(derived)={res[g]['C']*100:9.5f}%")
    return res

GOLD = (1.000, 0.766, 0.336)        # gold-ish sRGB baseColor
PAINT = (0.050, 0.120, 0.400)       # dark blue paint

print("Scenarios (relative error of mipped texel's radiance vs averaged shaded truth):")
s1 = run("1 gold metal | blue paint, r=.5", [(GOLD, 1.0, 0.5), (PAINT, 0.0, 0.5)])
s2 = run("2 paint r=.2 | paint r=.8", [(PAINT, 0.0, 0.2), (PAINT, 0.0, 0.8)])
s3 = run("3 BREAK near dielectrics", [((0.50, 0.40, 0.30), 0.0, 0.5), ((0.52, 0.42, 0.32), 0.0, 0.5)])
s4 = run("4 two metals, far colours", [(GOLD, 1.0, 0.5), ((0.95, 0.95, 0.95), 1.0, 0.5)])

# colour leak detail for scenario 1: diffuse albedo of B vs truth
bB = avg([[s2l(c) for c in GOLD], [s2l(c) for c in PAINT]])
leak = derive(bB, 0.5)[0]
true_diff = avg([derive([s2l(c) for c in GOLD], 1.0)[0], derive([s2l(c) for c in PAINT], 0.0)[0]])
print(f"  S1 diffuse albedo  B={[round(x,4) for x in leak]}  truth={[round(x,4) for x in true_diff]}")
fB = derive(bB, 0.5)[1]
f_true = avg([derive([s2l(c) for c in GOLD], 1.0)[1], derive([s2l(c) for c in PAINT], 0.0)[1]])
print(f"  S1 F0              B={[round(x,4) for x in fB]}  truth={[round(x,4) for x in f_true]}")

checks = {
    "P1 S1 A worse than B at diffuse view": s1["diffuse-view"]["A"] > s1["diffuse-view"]["B"],
    "P1 S1 B error >10% at diffuse view": s1["diffuse-view"]["B"] > 0.10,
    "P1 S1 C exact (<1e-9) both views": max(s1[g]["C"] for g in GEOS) < 1e-9,
    "P2 S1 B F0 red low by >20%": (f_true[0] - fB[0]) / f_true[0] > 0.20,
    "P3 S2 C error >50% at specular peak": s2["specular-peak"]["C"] > 0.50,
    "P4 S3 all within 0.1%": max(s3[g][m] for g in GEOS for m in "ABC") < 0.001,
    "P5 S4 (equal metal) B == C": max(abs(s4[g]["B"] - s4[g]["C"]) for g in GEOS) < 1e-9,
}
for k, v in checks.items():
    print(f"  {'ok ' if v else 'MISS'} {k}")
ok = all(checks.values())
print(f"RESULT: {'PASS' if ok else 'FAIL'} metal|paint mip: sRGB-base err {s1['diffuse-view']['A']*100:.1f}%, "
      f"linear-base err {s1['diffuse-view']['B']*100:.1f}% (diffuse view), derived albedo+F0 err "
      f"{max(s1[g]['C'] for g in GEOS):.1e}; roughness 0.2|0.8 mip still {s2['specular-peak']['C']*100:.0f}% off at peak; "
      f"near dielectrics max {max(s3[g][m] for g in GEOS for m in 'ABC')*100:.3f}%")
