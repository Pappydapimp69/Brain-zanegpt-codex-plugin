"""Sandbox: three-point lighting back/rim light (separates subject from background by an edge) x sRGB-vs-linear
averaging (gamma E1, pipeline E1: error grows with colour distance) x 'ratio not brightness controls contrast'.

Question: a rim is set on set to a rim:background ratio r. After a delivery downscale (box filter, factor F) that
makes the rim thinner than one output pixel, does the separation ratio survive, and is it controlled by the ratio
(scale-invariant under exposure) or by the rim's pixel footprint?

PREDICTION (written before the first run):
 P1 linear-light downscale: rim contrast = (k/F)*r + (1-k/F) exactly (phase-aligned), so it depends only on ratio r
    and footprint k/F, never on exposure.
 P2 sRGB-space downscale of a 1-px rim (F=4, r=16, bg 0.02) keeps less than half the linear contrast.
 P3 'ratio not brightness' survives sRGB averaging: an unclipped exposure sweep of +-2 stops changes the
    sRGB-downscaled rim contrast by under 10% (the sRGB curve is close to a power law, which is homogeneous).
 P4 BREAK (hidden assumption = the on-set ratio is a property of the light, not of the pixel footprint): a rim at
    least one output pixel wide (k=F) shows zero sRGB error; and when exposure clips the rim (+2 stops at r=16
    from 0.08) the ratio collapses for both pipelines, so brightness DOES control contrast once the rim clips.
"""
def enc(x):
    x = min(max(x, 0.0), 1.0)
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
def dec(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

def row(bg, r, k, phase, n=64, subj=None):
    """high-res 1-D row: subject shadow side | rim of k px | background. All linear, clipped at 1."""
    subj = bg if subj is None else subj
    edge = 32 + phase
    out = []
    for i in range(n):
        if i < edge: v = subj
        elif i < edge + k: v = r * bg
        else: v = bg
        out.append(min(v, 1.0))
    return out

def down(px, F, srgb):
    out = []
    for j in range(0, len(px), F):
        blk = px[j:j + F]
        if srgb: out.append(dec(sum(enc(p) for p in blk) / F))
        else: out.append(sum(blk) / F)
    return out

def rim_contrast(bg, r, k, F, srgb, phase, subj=None):
    px = row(bg, r, k, phase, subj=subj)
    o = down(px, F, srgb)
    return max(o) / max(min(px), 1e-12) if subj is None else max(o) / max(subj, bg)

def worst(bg, r, k, F, srgb, subj=None):
    """min over sub-pixel phases of the peak contrast (rim straddling two output pixels)"""
    return min(rim_contrast(bg, r, k, F, srgb, ph, subj) for ph in range(F))

ok = True
F = 4
print("== S1 linear vs sRGB downscale, F=4, bg 0.02 (low key), phase-aligned and worst phase")
tab = {}
for r in (4, 8, 16):
    for k in (1, 2, 4):
        lin_a = rim_contrast(0.02, r, k, F, False, 0)
        srg_a = rim_contrast(0.02, r, k, F, True, 0)
        lin_w, srg_w = worst(0.02, r, k, F, False), worst(0.02, r, k, F, True)
        tab[(r, k)] = (lin_a, srg_a, lin_w, srg_w)
        pred = (k / F) * r + (1 - k / F)
        print("r=%2d k=%d  linear %.3f (formula %.3f) sRGB %.3f kept %.0f%% | worst phase linear %.3f sRGB %.3f"
              % (r, k, lin_a, pred, srg_a, 100 * (srg_a - 1) / (lin_a - 1), lin_w, srg_w))
        ok &= abs(lin_a - pred) < 1e-9                           # P1
lin, srg = tab[(16, 1)][0], tab[(16, 1)][1]
p2 = (srg - 1) / (lin - 1)
print("P2 1-px rim r=16: linear %.3f sRGB %.3f -> sRGB keeps %.1f%% of the rim's excess over background" % (lin, srg, 100 * p2))
ok_p2 = p2 < 0.5
k4 = tab[(16, 4)]
print("P4a rim one output pixel wide (k=F): linear %.3f sRGB %.3f diff %.2e" % (k4[0], k4[1], abs(k4[0] - k4[1])))
ok &= abs(k4[0] - k4[1]) < 1e-9

print("== S2 exposure sweep (scale every light by 2^s, clip at 1), r=8 and r=16, k=1, base bg 0.02")
p3_spread = {}
for r in (8, 16):
    vals = []
    for s in (-2, -1, 0, 1, 2):
        bg = 0.02 * 2 ** s
        clipped = r * bg > 1.0
        c_l, c_s = rim_contrast(bg, r, 1, F, False, 0), rim_contrast(bg, r, 1, F, True, 0)
        vals.append((s, c_l, c_s, clipped))
        print("r=%2d stops %+d bg %.3f rim %.3f%s  linear %.3f sRGB %.3f" % (r, s, bg, min(r * bg, 1), " CLIPPED" if clipped else "", c_l, c_s))
    unc = [v[2] for v in vals if not v[3]]
    p3_spread[r] = (max(unc) - min(unc)) / min(unc)
    print("   unclipped sRGB contrast spread over exposure: %.2e (relative)" % p3_spread[r])
ok_p3 = p3_spread[8] < 0.10
# P4b clip: r=16 base rim 0.32; +2 stops -> 1.28 clipped
c_l0, c_lc = rim_contrast(0.02, 16, 1, F, False, 0), rim_contrast(0.08, 16, 1, F, False, 0)
print("P4b r=16 rim clipped at +2 stops: linear contrast %.3f -> %.3f" % (c_l0, c_lc))
ok &= c_lc < c_l0 * 0.85

print("== S2b (added after run 1) exposure pushed into the sRGB linear toe (bg below 0.0031308), r=8, k=1")
toe = []
for bg in (0.004, 0.002, 0.001, 0.0005):
    c = rim_contrast(bg, 8, 1, F, True, 0)
    toe.append(c)
    print("bg %.4f rim %.4f sRGB contrast %.4f (power-segment value %.4f)" % (bg, 8 * bg, c, tab[(8, 1)][1]))
toe_dev = max(abs(c - tab[(8, 1)][1]) for c in toe) / tab[(8, 1)][1]
print("   max deviation once the background enters the toe: %.1f%%" % (100 * toe_dev))

print("== S3 high key: bg 0.5, r=1.5 (rim barely above a bright background), k=1")
hk_l, hk_s = rim_contrast(0.5, 1.5, 1, F, False, 0), rim_contrast(0.5, 1.5, 1, F, True, 0)
hk_keep = (hk_s - 1) / (hk_l - 1)
print("linear %.4f sRGB %.4f keeps %.1f%%" % (hk_l, hk_s, 100 * hk_keep))

print("== S4 compensation: how much must the rim ratio rise for the sRGB-downscaled 1-px rim to match the linear r=8 result?")
target = tab[(8, 1)][0]
need = None
for r10 in range(80, 2001):
    r = r10 / 10
    if r * 0.02 > 1: break
    if rim_contrast(0.02, r, 1, F, True, 0) >= target:
        need = r; break
print("linear r=8 gives %.3f; sRGB pipeline needs r=%s (bg 0.02, clip at r=50)" % (target, need))

print("== S5 worst phase: rim straddles two output pixels (k=2, F=4, phase 3)")
print("r=16 k=2 aligned sRGB %.3f vs worst phase sRGB %.3f (linear %.3f vs %.3f)" % (tab[(16, 2)][1], tab[(16, 2)][3], tab[(16, 2)][0], tab[(16, 2)][2]))

print("P2 %s  P3 %s (spread r=8 %.1f%%, r=16 %.1f%%)" % (ok_p2, ok_p3, 100 * p3_spread[8], 100 * p3_spread[16]))
allok = ok and ok_p2 and ok_p3
print("RESULT: %s 1-px rim F=4 r=16 bg .02: linear %.2f sRGB %.2f (keeps %.0f%% of excess); exposure +-2 st unclipped spread r=8 %.1f%%; k=F diff 0; clip +2 st linear %.2f->%.2f; high-key r1.5 keeps %.0f%%; sRGB needs r=%s to match linear r=8; toe dev %.0f%%"
      % ("PASS" if allok else "FAIL", lin, srg, 100 * p2, 100 * p3_spread[8], c_l0, c_lc, 100 * hk_keep, need, 100 * toe_dev))
