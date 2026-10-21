"""RUN 1 (recorded, scale artefact): matched fg luminance was 0.12 linear, so every area-mean
distance was shrunk ~8x; shape cast read 28/28 confusable at every size, P1, P2 and P5 FAILED
(P3, P4 held). Cause: threshold T is absolute but fg was dark. RUN 2 below raises matched
luminance to 0.28 (and RUN 2a also fixed a bug: palettes were matched in gamma-space luma, then
linearised at render; now built in linear light and converted) (blue base moved to a lighter blue so the gamut allows it) and tints toward
white where a hue cannot reach the target luminance. The PREDICTIONS were not edited.

Sandbox: does 'silhouette first, then colour' hold, and where does it stop?

Kernel under test: ideas:visualdesign/accessibility/silhouette-first-then-colour
Re-verifies:  sandbox-combined-brain-viz-growth/E3  (hue-only collides after luminance projection)
              sandbox-cvd-transition-audit/E1       (VBM deutan model; trajectory, not endpoints)
              dog/E104                              (WCAG contrast of a fill against an eased backdrop)

PREDICTION (written BEFORE the first run; threshold T = 0.02 mean per-pixel distance):
 P1  16px, matched-luminance palette. Recolour-only cast (1 body, 8 hues): greyscale
     confusable pairs == 28 of 28, deutan >= 8. Shape cast (4 bodies x 2 props, same
     colours): 0 confusable pairs under normal, deutan, protan and greyscale.
 P2  Size sweep (box-downsample 1,2,4,8 of a 16px canvas). Shape cast has 0 confusable
     pairs at factors 1 and 2 but >= 1 at factor 8 (2x2 pixels). A luminance-spread
     recolour cast has fewer confusable pairs than the shape cast at factor 8.
     (I.e. a floor exists below which silhouette loses to luminance-separated colour.)
 P3  Near-identical bodies (differ by 2 pixels): >= 1 confusable pair at factor 1.
 P4  Eased backdrop dark->light, greyscale: the shape cast with no outline reaches
     28/28 confusable pairs on at least one frame; with a 1px black-or-white outline
     it never exceeds 0 and the minimum outline-vs-backdrop WCAG contrast >= 4.5.
 P5  Cast of 10 on 8 (body,prop) slots, greyscale, 16px: matched palette -> exactly 2
     confusable pairs (the two slots shared); luminance-spread palette -> 0.
"""
import itertools

N = 16
T = 0.02

# ---- colour models ------------------------------------------------------
def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

# Vienot-Brettel-Mollon 1999 dichromat matrices on linear RGB
DEUTAN = ((0.29275, 0.70725, 0.0), (0.29275, 0.70725, 0.0), (-0.02234, 0.02234, 1.0))
PROTAN = ((0.11238, 0.88762, 0.0), (0.11238, 0.88762, 0.0), (0.00401, -0.00401, 1.0))

def mat(m, rgb):
    return tuple(sum(m[i][j] * rgb[j] for j in range(3)) for i in range(3))

def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def scale_to_lum(base, y):
    k = y / lum(base)
    out = tuple(min(1.0, c * k) for c in base)
    if lum(out) < y - 1e-9:                       # gamut clip: tint toward white to reach y
        lo, hi = 0.0, 1.0
        for _ in range(40):
            m = (lo + hi) / 2
            c = tuple(o + (1 - o) * m for o in out)
            if lum(c) < y: lo = m
            else: hi = m
        out = tuple(o + (1 - o) * hi for o in out)
    return out

def gam(c):
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def srgb(linrgb):
    return tuple(gam(c) for c in linrgb)

BASES = [(1, .1, .1), (.1, 1, .1), (.3, .3, 1), (1, 1, .05),
         (1, .35, .05), (.05, .7, .5), (1, .1, .8), (.6, .7, .05)]
MATCHED = [srgb(scale_to_lum(b, 0.28)) for b in BASES]          # matched in LINEAR luminance                       # same luminance
SPREAD = [srgb(scale_to_lum(b, y)) for b, y in zip(BASES, (0.04, 0.08, 0.14, 0.22, 0.33, 0.48, 0.68, 0.9))]
BG = (0.02, 0.02, 0.02)

# ---- masks --------------------------------------------------------------
def mask_fn(f):
    return {(x, y) for y in range(N) for x in range(N) if f(x, y)}

def circle(x, y): return (x - 7.5) ** 2 + (y - 8.5) ** 2 <= 6.2 ** 2
def square(x, y): return 3 <= x <= 12 and 4 <= y <= 13
def tri(x, y): return 4 <= y <= 13 and abs(x - 7.5) <= (y - 3) * 0.55
def bar(x, y): return 6 <= x <= 9 and 2 <= y <= 14
def cross(x, y): return (6 <= x <= 9 and 3 <= y <= 13) or (3 <= x <= 12 and 7 <= y <= 9)
def wide(x, y): return 2 <= x <= 13 and 7 <= y <= 11

BODIES = [mask_fn(f) for f in (circle, square, tri, bar)]
PROPS = [mask_fn(lambda x, y: x == 14 and 1 <= y <= 6),                  # staff
         mask_fn(lambda x, y: 1 <= x <= 3 and 1 <= y <= 2)]              # flag (hat)

def render(mask, fg, bg=BG):
    return [[fg if (x, y) in mask else bg for x in range(N)] for y in range(N)]

def outline(mask):
    ring = set()
    for (x, y) in mask:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if 0 <= p[0] < N and 0 <= p[1] < N and p not in mask:
                    ring.add(p)
    return ring

def render_outlined(mask, fg, bg, ol):
    ring = outline(mask)
    return [[fg if (x, y) in mask else (ol if (x, y) in ring else bg) for x in range(N)] for y in range(N)]

# ---- degradation + distance --------------------------------------------
def degrade(img, cond, f):
    # img of gamma-space rgb -> linear -> condition -> box downsample by f
    px = [[tuple(lin(c) for c in p) for p in row] for row in img]
    if cond == "deutan": px = [[mat(DEUTAN, p) for p in row] for row in px]
    elif cond == "protan": px = [[mat(PROTAN, p) for p in row] for row in px]
    elif cond == "grey": px = [[(lum(p),) for p in row] for row in px]
    if f == 1: return px
    M = N // f
    k = len(px[0][0])
    out = []
    for by in range(M):
        row = []
        for bx in range(M):
            acc = [0.0] * k
            for dy in range(f):
                for dx in range(f):
                    p = px[by * f + dy][bx * f + dx]
                    for i in range(k): acc[i] += p[i]
            row.append(tuple(a / (f * f) for a in acc))
        out.append(row)
    return out

def dist(a, b):
    tot, n = 0.0, 0
    for ra, rb in zip(a, b):
        for pa, pb in zip(ra, rb):
            tot += sum((u - v) ** 2 for u, v in zip(pa, pb)) ** 0.5
            n += 1
    return tot / n

def conf_pairs(imgs, cond, f, t=T):
    d = [degrade(i, cond, f) for i in imgs]
    return [(i, j) for i, j in itertools.combinations(range(len(imgs)), 2) if dist(d[i], d[j]) < t]

CONDS = ("normal", "deutan", "protan", "grey")

# ---- casts --------------------------------------------------------------
SLOTS = [(b, p) for b in range(4) for p in range(2)]
def shape_cast(pal, slots=SLOTS):
    return [render(BODIES[b] | PROPS[p], pal[i % len(pal)]) for i, (b, p) in enumerate(slots)]
def recolour_cast(pal):
    return [render(BODIES[1], c) for c in pal]

results = {}
lines = []
def log(s): lines.append(s); print(s)

# S1 ------------------------------------------------------------------
A = recolour_cast(MATCHED); B = shape_cast(MATCHED)
log("S1 16px matched-luminance palette (pairs of 28 confusable)")
s1 = {}
for c in CONDS:
    a, b = len(conf_pairs(A, c, 1)), len(conf_pairs(B, c, 1))
    s1[c] = (a, b); log(f"  {c:7s} recolour={a:2d} shape={b:2d}")
p1 = s1["grey"][0] == 28 and s1["deutan"][0] >= 8 and all(v[1] == 0 for v in s1.values())
log(f"  P1 {'holds' if p1 else 'FAILS'}")

# S2 (size sweep) ---------------------------------------------------------
A2 = recolour_cast(SPREAD); B2 = shape_cast(MATCHED)
log("S2 size sweep, worst condition over normal/deutan/protan/grey (confusable pairs)")
sweep = {}
for f in (1, 2, 4, 8):
    wb = max(len(conf_pairs(B2, c, f)) for c in CONDS)
    wa = max(len(conf_pairs(A2, c, f)) for c in CONDS)
    sweep[f] = (wb, wa); log(f"  factor {f} ({N//f}px) shape={wb:2d} lum-spread-recolour={wa:2d}")
p2 = sweep[1][0] == 0 and sweep[2][0] == 0 and sweep[8][0] >= 1 and sweep[8][1] < sweep[8][0]
log(f"  P2 {'holds' if p2 else 'FAILS'}")
# threshold robustness for the crossover
for t in (0.01, 0.04):
    cb = max(len(conf_pairs(B2, c, 8, t)) for c in CONDS)
    ca = max(len(conf_pairs(A2, c, 8, t)) for c in CONDS)
    log(f"  robustness T={t}: factor8 shape={cb} lum-spread-recolour={ca}")

# S3 (break: near-identical bodies) -------------------------------------------
near = []
base = BODIES[1]
for k in range(4):
    m = set(base)
    edits = [(3, 4), (12, 13), (3, 13), (12, 4)][:k]
    for e in edits: m.discard(e)       # each body differs from the previous by 1 pixel
    near.append(render(m, MATCHED[0]))
n3 = len(conf_pairs(near, "grey", 1))
p3 = n3 >= 1
log(f"S3 near-identical bodies (<=3 px apart) grey 16px confusable pairs of 6 = {n3}  P3 {'holds' if p3 else 'FAILS'}")

# S4 (E104 composition: eased backdrop) ---------------------------------------
fg = MATCHED[0]
frames = []
for i in range(33):
    g = 0.02 + (0.98 - 0.02) * i / 32           # gamma-space backdrop ramp
    frames.append((g, g, g))
fg_shapes = [BODIES[b] | PROPS[p] for (b, p) in SLOTS]
fgs = [MATCHED[i] for i in range(8)]
worst_plain, worst_ol, min_c, min_c_plain = 0, 0, 99.0, 99.0
for bg in frames:
    imgs = [render(m, c, bg) for m, c in zip(fg_shapes, fgs)]
    worst_plain = max(worst_plain, len(conf_pairs(imgs, "grey", 1)))
    min_c_plain = min(min_c_plain, min(contrast(tuple(lin(x) for x in c), tuple(lin(x) for x in bg)) for c in fgs))
    black, white = (0, 0, 0), (1, 1, 1)
    lb = tuple(lin(x) for x in bg)
    ol = white if contrast((1, 1, 1), lb) >= contrast((0, 0, 0), lb) else black
    imgs2 = [render_outlined(m, c, bg, ol) for m, c in zip(fg_shapes, fgs)]
    worst_ol = max(worst_ol, len(conf_pairs(imgs2, "grey", 1)))
    min_c = min(min_c, contrast(tuple(lin(x) for x in ol), lb))
log(f"S4 eased backdrop 33 frames, grey: no-outline worst={worst_plain}/28 (min fg:bg {min_c_plain:.2f}:1); "
    f"outlined worst={worst_ol}/28 (min outline:bg {min_c:.2f}:1)")
p4 = worst_plain == 28 and worst_ol == 0 and min_c >= 4.5
log(f"  P4 {'holds' if p4 else 'FAILS'}")

# S5 (break: more entities than slots) ----------------------------------------
slots10 = SLOTS + [SLOTS[0], SLOTS[5]]
cm = shape_cast(MATCHED + MATCHED[:2], slots10)
cs = shape_cast(SPREAD + [SPREAD[7], SPREAD[0]], slots10)
# shared slots must carry a colour difference: give the duplicates a distant luminance
cm = [render(BODIES[b] | PROPS[p], (MATCHED + [MATCHED[1], MATCHED[6]])[i]) for i, (b, p) in enumerate(slots10)]
cs = [render(BODIES[b] | PROPS[p], (SPREAD + [SPREAD[7], SPREAD[0]])[i]) for i, (b, p) in enumerate(slots10)]
n_m = len(conf_pairs(cm, "grey", 1)); n_s = len(conf_pairs(cs, "grey", 1))
p5 = n_m == 2 and n_s == 0
log(f"S5 10 entities on 8 slots grey 16px: matched-palette confusable={n_m} luminance-spread={n_s}  P5 {'holds' if p5 else 'FAILS'}")

# E1 touch: trajectory of a recolour transition inside the shape cast (deutan) ---
def lerp(a, b, t): return tuple(x + (y - x) * t for x, y in zip(a, b))
third = MATCHED[0]
moving_from, moving_to = SPREAD[2], SPREAD[6]
mid_conf = 0
for k in range(0, 101):
    c = lerp(moving_from, moving_to, k / 100)
    img_m = render(BODIES[0] | PROPS[0], c)
    img_t = render(BODIES[0] | PROPS[0], third)       # same slot as the third entity
    if dist(degrade(img_m, "deutan", 1), degrade(img_t, "deutan", 1)) < T: mid_conf += 1
img_a = render(BODIES[0] | PROPS[0], moving_from); img_t = render(BODIES[0] | PROPS[0], third)
img_b = render(BODIES[0] | PROPS[0], moving_to)
ends_ok = dist(degrade(img_a, "deutan", 1), degrade(img_t, "deutan", 1)) >= T and \
          dist(degrade(img_b, "deutan", 1), degrade(img_t, "deutan", 1)) >= T
log(f"E1 touch: same-slot recolour transition vs third entity (deutan): endpoints distinct={ends_ok}, interior samples confusable={mid_conf}/101")
mid_cross_diff_slot = 0
for k in range(0, 101):
    c = lerp(moving_from, moving_to, k / 100)
    img_m = render(BODIES[0] | PROPS[0], c)
    img_t2 = render(BODIES[2] | PROPS[1], third)       # different slot
    if dist(degrade(img_m, "deutan", 1), degrade(img_t2, "deutan", 1)) < T: mid_cross_diff_slot += 1
log(f"  same transition vs a third entity in a DIFFERENT slot: confusable samples={mid_cross_diff_slot}/101")


# ---- POST-HOC probes (NOT pre-registered; added after run 2 showed where P1/P2/P5 broke) ----
def peak(a, b):
    return max(sum((u - v) ** 2 for u, v in zip(pa, pb)) ** 0.5 for ra, rb in zip(a, b) for pa, pb in zip(ra, rb))

def conf_peak(imgs, cond, f, t):
    d = [degrade(i, cond, f) for i in imgs]
    return [(i, j) for i, j in itertools.combinations(range(len(imgs)), 2) if peak(d[i], d[j]) < t]

log("X1 (post-hoc) which shape-cast pairs are confusable in greyscale at 16px?")
pairs = conf_pairs(B, "grey", 1)
prop_only = [pr for pr in pairs if SLOTS[pr[0]][0] == SLOTS[pr[1]][0]]
log(f"  {len(pairs)} confusable, {len(prop_only)} of them share a body and differ only by the 6-pixel prop")
bodies_only = [render(b, MATCHED[i]) for i, b in enumerate(BODIES)]
bo = {c: len(conf_pairs(bodies_only, c, 1)) for c in CONDS}
log(f"X2 (post-hoc) 4 body-only silhouettes, matched luminance, confusable pairs of 6: {bo}")
log("X3 (post-hoc) area-mean distance is nearly size-invariant under box downsampling (S2 flat);")
log("   a PEAK-pixel metric (T=0.05) is the size-sensitive one. confusable pairs, grey:")
xs = {}
for f in (1, 2, 4, 8):
    xs[f] = (len(conf_peak(B2, "grey", f, 0.05)), len(conf_peak(A2, "grey", f, 0.05)),
             len(conf_peak(bodies_only, "grey", f, 0.05)))
    log(f"  factor {f} ({N//f}px) shape cast={xs[f][0]:2d}/28 lum-spread recolour={xs[f][1]:2d}/28 body-only(4)={xs[f][2]}/6")

ok = p1 and p2 and p3 and p4 and p5
status = "PASS" if ok else "FAIL"
fails = [n for n, v in zip(("P1", "P2", "P3", "P4", "P5"), (p1, p2, p3, p4, p5)) if not v]
print(f"RESULT: {status} predictions held={5-len(fails)}/5" + (f" failed={','.join(fails)}" if fails else "") +
      f"; S1 grey recolour={s1['grey'][0]}/28 shape={s1['grey'][1]}; sweep shape/lumspread f8={sweep[8][0]}/{sweep[8][1]}; "
      f"eased-bg worst plain={worst_plain} outlined={worst_ol}; post-hoc: prop-only pairs={len(prop_only)}/{len(pairs)}, "
      f"body-only grey conf={bo['grey']}, peak-metric f8 shape={xs[8][0]} lumspread={xs[8][1]}")
