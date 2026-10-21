"""Gap (no lessons yet): colour-blind-safe hallucination cues. SEVEN's visual
hallucinations could tint the woods 'wrong'. Does a hue-only cue survive
colour-vision deficiency?
Fixture: foliage base colour sRGB (62,118,48). Cues (each a 'wrong' version of
the base): HUE  = red-brown at matched relative luminance (solved by bisection);
LUM  = the base 35% darker; BY   = blue-shifted, matched luminance;
BOTH = hue shift + 35% darker (redundant). Simulated with Machado, Oliveira &
Fernandes 2009 full-severity matrices in linear RGB (protanopia, deuteranopia,
tritanopia; values entered FROM MEMORY - assumed), compared by CIE76 delta-E in
Lab (D65). Visible = delta-E >= 10 (ASSUMED threshold for a glanceable cue;
~2.3 is a just-noticeable difference).
PREDICTION (written before running): HUE: dE >= 30 normal, < 10 under protan and
deutan; LUM: >= 10 under all four; BY: >= 10 under protan/deutan, < 10 under
tritan (the break case for a blue-yellow 'fix'); BOTH: >= 10 under all four.
"""
import sys
print("python", sys.version.split()[0])
M = {"normal": [[1,0,0],[0,1,0],[0,0,1]],
     "protan": [[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
     "deutan": [[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
     "tritan": [[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]}
lin = lambda c: (c/255/12.92) if c/255 <= 0.04045 else ((c/255+0.055)/1.055)**2.4
def lab(rgb_lin):
    r, g, b = [min(1.0, max(0.0, v)) for v in rgb_lin]
    X = 0.4124*r+0.3576*g+0.1805*b; Y = 0.2126*r+0.7152*g+0.0722*b; Z = 0.0193*r+0.1192*g+0.9505*b
    f = lambda t: t**(1/3) if t > 0.008856 else 7.787*t+16/116
    fx, fy, fz = f(X/0.95047), f(Y), f(Z/1.08883)
    return (116*fy-16, 500*(fx-fy), 200*(fy-fz))
def sim(rgb, k):
    L = [lin(c) for c in rgb]; m = M[k]
    return [sum(m[i][j]*L[j] for j in range(3)) for i in range(3)]
def dE(a, b, k):
    A, B = lab(sim(a, k)), lab(sim(b, k)); return sum((x-y)**2 for x, y in zip(A, B))**0.5
Y = lambda rgb: sum(w*lin(c) for w, c in zip((0.2126, 0.7152, 0.0722), rgb))
def match(direction, base):
    lo, hi = 0.0, 3.0
    for _ in range(60):
        s = (lo+hi)/2; c = [min(255, max(0, round(v*s))) for v in direction]
        (lo, hi) = (s, hi) if Y(c) < Y(base) else (lo, s)
    return [min(255, max(0, round(v*lo))) for v in direction]
base = (62, 118, 48)
cues = {"HUE": match((150, 80, 40), base), "LUM": [round(v*0.65) for v in base],
        "BY": match((40, 110, 140), base)}
cues["BOTH"] = [round(v*0.65) for v in cues["HUE"]]
res = {}
for n, c in cues.items():
    res[n] = {k: dE(base, c, k) for k in M}
    print(f"{n:4s} {c} Y {Y(c):.4f} (base {Y(base):.4f}): " + "  ".join(f"{k} {v:5.1f}" for k, v in res[n].items()))
p = [res["HUE"]["normal"] >= 30, res["HUE"]["protan"] < 10, res["HUE"]["deutan"] < 10,
     all(v >= 10 for v in res["LUM"].values()), res["BY"]["protan"] >= 10 and res["BY"]["deutan"] >= 10,
     res["BY"]["tritan"] < 10, all(v >= 10 for v in res["BOTH"].values())]
print("prediction checks:", p)
print(f"RESULT: {'PASS' if all(p) else 'FAIL'} {sum(p)}/7; HUE dE normal {res['HUE']['normal']:.1f} protan {res['HUE']['protan']:.1f} deutan {res['HUE']['deutan']:.1f}; LUM min {min(res['LUM'].values()):.1f}; BY tritan {res['BY']['tritan']:.1f}; BOTH min {min(res['BOTH'].values()):.1f}")
