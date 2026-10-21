"""Seed sandbox for a new domain, HERALDRY: the rule of tincture (never place metal on metal or colour on colour).
Does the rule behave like a legibility (WCAG contrast) rule? Swatches are the standard values from the Wikipedia
'Tincture (heraldry)' page AS I RECALL THEM (not re-fetched this run): or FCDD09, argent FFFFFF, gules DA121A,
azure 0F47AF, sable 000000, vert 009200, purpure 9116A1. CVD matrices are Machado et al. 2009 severity 1.0 as I recall.
Adjacent entries exercised: dog/E104 (name tokens by role-against-background; measure rendered pairs),
seven/E96 (hue-only distinctions lose contrast for colour-blind viewers; check protan/deutan), and the contrast ratio
formula itself (WCAG 2.x relative luminance).
PREDICTION (before run): (1) 9 of the 10 allowed (metal x colour) pairs reach >= 3:1 and the weakest allowed pair is or/vert
(about 3.1); (2) a single contrast threshold CANNOT separate allowed from forbidden: at least one forbidden colour-colour
pair (sable with vert or gules) has HIGHER contrast than the weakest allowed pair (AUC < 1.0, expected 0.85-0.97);
(3) BREAK/CVD: under protan and deutan simulation the weakest allowed pair stays >= 2.0 but at least 1 allowed pair
falls under 3:1 (the metal/colour split is a lightness-class convention, not a guarantee). Assumption: the rule exists
because it protects contrast. Wrong if the threshold separates the classes perfectly (AUC = 1.0)."""
import itertools
T = {"or": "FCDD09", "argent": "FFFFFF", "gules": "DA121A", "azure": "0F47AF", "sable": "000000", "vert": "009200", "purpure": "9116A1"}
METAL = {"or", "argent"}
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def rgb(h): return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
def lum(l): return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2]
def cr(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb); return (hi + 0.05) / (lo + 0.05)
M = {"none": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
     "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
     "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]}
def sim(h, m):
    l = [lin(x) for x in rgb(h)]
    o = [sum(M[m][i][j] * l[j] for j in range(3)) for i in range(3)]
    return [min(1, max(0, v)) for v in o]
pairs = list(itertools.combinations(T, 2))
allowed = [p for p in pairs if (p[0] in METAL) != (p[1] in METAL)]
forbid = [p for p in pairs if (p[0] in METAL) == (p[1] in METAL)]
res = {}
for m in M:
    c = {p: cr(sim(T[p[0]], m), sim(T[p[1]], m)) if m != "none" else cr([lin(x) for x in rgb(T[p[0]])], [lin(x) for x in rgb(T[p[1]])]) for p in pairs}
    wa = min(allowed, key=lambda p: c[p]); fh = max(forbid, key=lambda p: c[p])
    auc = sum((c[a] > c[f]) + 0.5 * (c[a] == c[f]) for a in allowed for f in forbid) / (len(allowed) * len(forbid))
    n3 = sum(c[p] >= 3 for p in allowed)
    res[m] = (c, wa, fh, auc, n3)
    print("%-6s allowed>=3:1 %d/%d weakest allowed %s %.2f | strongest forbidden %s %.2f | AUC %.3f" % (m, n3, len(allowed), "/".join(wa), c[wa], "/".join(fh), c[fh], auc))
c0, wa0, fh0, auc0, n30 = res["none"]
cvd_under3 = [(m, "/".join(p)) for m in ("protan", "deutan") for p in allowed if res[m][0][p] < 3]
cvd_min = min(res[m][0][res[m][1]] for m in ("protan", "deutan"))
print("allowed pairs under 3:1 with CVD:", cvd_under3, "weakest allowed under CVD %.2f" % cvd_min)
ok = (n30 >= 9 and wa0 == ("or", "vert") and auc0 < 1.0 and c0[fh0] > c0[wa0] and len(cvd_under3) >= 1 and cvd_min >= 2.0)
print("RESULT: %s rule-of-tincture: %d/10 allowed pairs >=3:1, weakest allowed %s %.2f, strongest forbidden %s %.2f (AUC %.3f, no single threshold); CVD allowed pairs under 3:1: %d, weakest under CVD %.2f"
      % ("PASS" if ok else "FAIL", n30, "/".join(wa0), c0[wa0], "/".join(fh0), c0[fh0], auc0, len(cvd_under3), cvd_min))
