"""Sandbox: is the silhouette-first size floor an artefact of the distance metric?

Target tension: 'Does silhouette-first lose to luminance-separated colour below a size floor,
or is that floor an artefact of the distance metric?'  Re-uses the cast, masks, palettes and
colour-vision matrices of memory entry sandbox-silhouette-first-cue-audit/E1 (copied below,
not imported) and adds a family of metrics:
  area-mean (raw), peak (raw), and a VIEWER MODEL: box-resample to the physical display size
  (16/f px), opponent colour space (A = linear luminance, C1 = R-G, C2 = (R+G)/2-B), a Gaussian
  low-pass in PHYSICAL pixels (eye optics + neural contrast-sensitivity roll-off; the chromatic
  channels get a 2.5x wider blur because chromatic acuity is roughly 2-3x worse than luminance),
  then Minkowski pooling (beta=inf peak, beta=4 probability summation, beta=1 mean).
  V1 = sigma_L 0.5 px / sigma_C 1.25 px (normal viewing), V2 = 1.0 / 2.5 (far or low acuity).
  The sigmas, the chromatic gain 0.5 and the Weber-style nominal threshold 0.014 (5% of the
  0.28 foreground luminance) are ASSUMED stand-ins, not calibrated to observers; every verdict
  is therefore also swept over a 0.25x..4x threshold grid.

A metric is called DEFENSIBLE only if it passes two sanity tests that do not depend on any
threshold story: (T1) a prop that is plainly visible at full size must not be called
confusable; (T4) padding the sprite with empty background (a larger canvas, same sprite)
must not change the distance by more than ~5%, because an observer does not care about empty
surround.  Models that fail are still reported.

PREDICTION (written BEFORE the first run; cast of 8 'slots' = 4 bodies x 2 props, matched
linear luminance 0.28; 28 pairs; count = worst of normal/deutan/protan/grey):
 P1 replication of E1: raw area-mean shape-cast count is flat (max-min <= 1 over f=1,2,4,8)
    and 4 at f=1; raw peak (T=0.05) is 0 at f=1 and >= 8 at f=8.
 P2 sanity: area-mean FAILS T1 (calls the prop-only pair confusable at f=1) and FAILS T4
    (distance ratio at 4x canvas area <= 0.3); raw-peak and viewer-peak (beta=inf) PASS both
    (ratio >= 0.95); viewer beta=4 FAILS T4 with ratio in [0.6, 0.9].
 P3 floor survives across the DEFENSIBLE models (raw-peak, V1-peak, V2-peak, nominal T=0.014):
    the shape cast's own count rises by >= 7 pairs from f=1 to f=8 in all three, and under
    V2-peak the onset (first f with count >= count(f=1)+7) is f<=4 (blur moves it earlier).
 P4 threshold robustness: for each defensible model, 'count(f=8) - count(f=1) >= 7' holds at
    >= 6 of the 9 grid thresholds (0.25x..4x nominal).
 P5 versus colour: at f=8, under each defensible model, the luminance-spread recolour cast
    (R8) has >= 3 fewer confusable pairs than the shape cast (S8), and the hybrid (shapes AND
    luminance-spread colours, H8) has <= R8's count.
 P6 BREAK (information floor): 4 area-matched, doubly-symmetric bodies (all 64 px ink, equal
    quadrant ink): 0/6 confusable at f=1 and 6/6 at f=8 under EVERY model including
    area-mean; at f=4 raw peak keeps >= 1 pair distinct (count < 6) while V2-peak has >= 4.

RUN 1 (recorded): P1 and P2 held; P3, P4, P5, P6 FAILED (2/6 held). Causes: nominal T=0.014 is a
free parameter and moves every count (raw-peak at T=0.014 shows 0 confusable at 2 px where E1's
T=0.05 showed 10), and area-matched bodies at f=4 stayed distinct under V2-peak (0, not >= 4).
The P1-P6 text above is UNEDITED. After seeing that, I added the models 'V1-W' and 'V2-W'
(Weber-normalised viewer: each blurred pixel difference divided by mean luminance of the two
pixels plus a glare floor 0.02; nominal threshold 0.05, an assumed 5% Weber fraction) and an
ANCHORED threshold window per model, and pre-registered P7-P9 BEFORE running that code:
  window = [T_lo, T_hi]: T_lo = model distance of a pair at f=1 that differs only by a 2% whole-body
  luminance change (standard luminance JND, taken as 'cannot tell apart'); T_hi = model distance
  of the full-size prop-only pair (plainly visible). Any defensible threshold lies inside.
 P7 area-mean shows no floor anywhere in its window (count(f=8)-count(f=1) <= 1 at T_lo, mid, T_hi/2);
    every peak-type model has a non-empty window (T_lo < T_hi).
 P8 for each peak-type model the floor (count(f=8)-count(f=1) >= 7 of 28) is ABSENT at T_lo and
    PRESENT at T_hi/2: i.e. even the defensible metrics only place the floor once the threshold is
    chosen, so the metric family does not settle it; the threshold calibration does.
 P9 the Weber models V1-W and V2-W show the floor at the window's geometric mid (sqrt(T_lo*T_hi)).
"""
import itertools, math

N = 16
BG = (0.02, 0.02, 0.02)

# ---- colour (copied from the E1 sandbox) --------------------------------------
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lum(rgb): return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
DEUTAN = ((0.29275, 0.70725, 0.0), (0.29275, 0.70725, 0.0), (-0.02234, 0.02234, 1.0))
PROTAN = ((0.11238, 0.88762, 0.0), (0.11238, 0.88762, 0.0), (0.00401, -0.00401, 1.0))
def mat(m, rgb): return tuple(sum(m[i][j] * rgb[j] for j in range(3)) for i in range(3))
def scale_to_lum(base, y):
    k = y / lum(base)
    out = tuple(min(1.0, c * k) for c in base)
    if lum(out) < y - 1e-9:
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
def srgb(l): return tuple(gam(c) for c in l)
BASES = [(1, .1, .1), (.1, 1, .1), (.3, .3, 1), (1, 1, .05), (1, .35, .05), (.05, .7, .5), (1, .1, .8), (.6, .7, .05)]
MATCHED = [srgb(scale_to_lum(b, 0.28)) for b in BASES]
SPREAD = [srgb(scale_to_lum(b, y)) for b, y in zip(BASES, (0.04, 0.08, 0.14, 0.22, 0.33, 0.48, 0.68, 0.9))]

# ---- masks --------------------------------------------------------------------
def mask_fn(f, n=N): return {(x, y) for y in range(n) for x in range(n) if f(x, y)}
def circle(x, y): return (x - 7.5) ** 2 + (y - 8.5) ** 2 <= 6.2 ** 2
def square(x, y): return 3 <= x <= 12 and 4 <= y <= 13
def tri(x, y): return 4 <= y <= 13 and abs(x - 7.5) <= (y - 3) * 0.55
def bar(x, y): return 6 <= x <= 9 and 2 <= y <= 14
BODIES = [mask_fn(f) for f in (circle, square, tri, bar)]
PROPS = [mask_fn(lambda x, y: x == 14 and 1 <= y <= 6), mask_fn(lambda x, y: 1 <= x <= 3 and 1 <= y <= 2)]
SLOTS = [(b, p) for b in range(4) for p in range(2)]
# area-matched, doubly symmetric about (7.5, 7.5): every body is 64 px, 16 px per quadrant
AM = [mask_fn(lambda x, y: 4 <= x <= 11 and 4 <= y <= 11),                                  # 8x8 square
      mask_fn(lambda x, y: (3 <= x <= 12 and 3 <= y <= 12) and not (5 <= x <= 10 and 5 <= y <= 10)),  # ring 10x10-6x6
      mask_fn(lambda x, y: (3 <= x <= 12 and 6 <= y <= 9) or (6 <= x <= 9 and 3 <= y <= 12)),          # cross L10 t4
      mask_fn(lambda x, y: (x in (1, 2, 3, 4) or x in (11, 12, 13, 14)) and (y in (1, 2, 3, 4) or y in (11, 12, 13, 14)))]  # 4 corner blocks

def render(mask, fg, bg=BG, n=N, off=0):
    return [[fg if (x - off, y - off) in mask else bg for x in range(n)] for y in range(n)]

# ---- degradation: gamma -> linear -> condition -> (3-vector always) ----------------
def to_cond(img, cond):
    out = []
    for row in img:
        r = []
        for p in row:
            q = tuple(lin(c) for c in p)
            if cond == "deutan": q = mat(DEUTAN, q)
            elif cond == "protan": q = mat(PROTAN, q)
            elif cond == "grey": y = lum(q); q = (y, y, y)
            r.append(q)
        out.append(r)
    return out

def box(px, f):
    if f == 1: return px
    n = len(px); M = n // f
    return [[tuple(sum(px[by * f + dy][bx * f + dx][i] for dy in range(f) for dx in range(f)) / (f * f) for i in range(3))
             for bx in range(M)] for by in range(M)]

def opp(p): return (lum(p), p[0] - p[1], 0.5 * (p[0] + p[1]) - p[2])

def kernel(sig):
    r = max(1, math.ceil(3 * sig)); w = [math.exp(-(i * i) / (2 * sig * sig)) for i in range(-r, r + 1)]
    s = sum(w); return [v / s for v in w], r

def blur_channel(ch, sig, padv):
    k, r = kernel(sig); n = len(ch)
    P = [[padv] * (n + 2 * r) for _ in range(n + 2 * r)]
    for y in range(n):
        for x in range(n): P[y + r][x + r] = ch[y][x]
    W = n + 2 * r
    H = [[sum(k[i] * P[y][min(W - 1, max(0, x + i - r))] for i in range(2 * r + 1)) for x in range(W)] for y in range(W)]
    return [[sum(k[i] * H[y + i][x + r] for i in range(2 * r + 1)) for x in range(n)] for y in range(n)]

WC = 0.5  # chromatic gain (assumed)
def viewer(px, sigL, sigC, bgp):
    o = [[opp(p) for p in row] for row in px]; ob = opp(bgp)
    chans = []
    for c in range(3):
        ch = [[o[y][x][c] for x in range(len(o))] for y in range(len(o))]
        chans.append(blur_channel(ch, sigL if c == 0 else sigC, ob[c]))
    return [[(chans[0][y][x], WC * chans[1][y][x], WC * chans[2][y][x]) for x in range(len(o))] for y in range(len(o))]

def viewer_grey(px, sigL, bgp):
    ch = [[p[0] for p in row] for row in px]
    b = blur_channel(ch, sigL, bgp[0])
    return [[(v, 0.0, 0.0) for v in row] for row in b]

def pix_opp_raw(px): return [[(p[0], p[1], p[2]) for p in row] for row in px]

A0 = 0.02  # glare / veiling-luminance floor for Weber normalisation (assumed)
def pool(a, b, beta, weber=False):
    ds = []
    for ra, rb in zip(a, b):
        for pa, pb in zip(ra, rb):
            d = sum((u - v) ** 2 for u, v in zip(pa, pb)) ** 0.5
            if weber: d /= 0.5 * (pa[0] + pb[0]) + A0
            ds.append(d)
    if beta == "inf": return max(ds)
    if beta == 1: return sum(ds) / len(ds)
    return (sum(d ** beta for d in ds) / len(ds)) ** (1.0 / beta)

# model = (name, blur sigmas or None, pooling beta, nominal threshold)
MODELS = [("area-mean", None, 1, 0.02), ("raw-peak", None, "inf", 0.014),
          ("V1-peak", (0.5, 1.25), "inf", 0.014), ("V2-peak", (1.0, 2.5), "inf", 0.014),
          ("V1-b4", (0.5, 1.25), 4, 0.014), ("V1-mean", (0.5, 1.25), 1, 0.014),
          ("V1-W", (0.5, 1.25), "inf", 0.05, True), ("V2-W", (1.0, 2.5), "inf", 0.05, True)]
CONDS = ("normal", "deutan", "protan", "grey")

def prep(img, cond, f, model):
    px = box(to_cond(img, cond), f)
    name, sig = model[0], model[1]
    if sig is None:
        if cond == "grey":  # E1 used a single channel; (y,y,y) would inflate Euclid distance by sqrt(3)
            return [[(p[0], 0.0, 0.0) for p in row] for row in px]
        return px
    bgp = box(to_cond([[BG]], cond) * 1, 1)[0][0] if False else to_cond([[BG]], cond)[0][0]
    if cond == "grey":   # opponent of a grey pixel is (Y,0,0); build it directly
        return viewer_grey(px, sig[0], bgp)
    return viewer(px, sig[0], sig[1], bgp)

def dists(imgs, f, model):
    """{condition: {pair: distance}}; the cast count is the WORST condition, as in E1."""
    res = {}
    for c in CONDS:
        d = [prep(i, c, f, model) for i in imgs]
        res[c] = {(i, j): pool(d[i], d[j], model[2], len(model) > 4) for i, j in itertools.combinations(range(len(imgs)), 2)}
    return res

def count(dd, t): return max(sum(1 for v in per.values() if v < t) for per in dd.values())
def mind(dd, pr): return min(per[pr] for per in dd.values())

def shape_imgs(pal, slots=SLOTS): return [render(BODIES[b] | PROPS[p], pal[i % len(pal)]) for i, (b, p) in enumerate(slots)]
S8 = shape_imgs(MATCHED)
R8 = [render(BODIES[1], c) for c in SPREAD]
H8 = shape_imgs(SPREAD)
B4 = [render(b, MATCHED[i]) for i, b in enumerate(BODIES)]
A4 = [render(m, MATCHED[i]) for i, m in enumerate(AM)]
FS = (1, 2, 4, 8)
GRID = [0.25, 0.35, 0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0]

out = []
def log(s): out.append(s); print(s)

D = {}   # (cast, model, f) -> pair-distance dict
def getd(cast, imgs, m, f):
    k = (cast, m[0], f)
    if k not in D: D[k] = dists(imgs, f, m)
    return D[k]
CASTS = {"S8": S8, "R8": R8, "H8": H8, "B4": B4, "A4": A4}

# ---------------- P1 replication ----------------------------------------------------
am = MODELS[0]; rp = MODELS[1]
c_am = {f: count(getd("S8", S8, am, f), 0.02) for f in FS}
c_rp5 = {f: count(getd("S8", S8, rp, f), 0.05) for f in FS}
log(f"S1 replication of E1: shape cast S8 confusable of 28 by factor: area-mean(T.02)={list(c_am.values())} raw-peak(T.05)={list(c_rp5.values())}")
p1 = (max(c_am.values()) - min(c_am.values()) <= 1) and c_am[1] == 4 and c_rp5[1] == 0 and c_rp5[8] >= 8
log(f"  P1 {'holds' if p1 else 'FAILS'}")

# ---------------- P2 sanity tests ----------------------------------------------------
# T1: prop-only pair (circle body vs circle+staff), same colour; visible to any observer at 16px
pair = [render(BODIES[0], MATCHED[0]), render(BODIES[0] | PROPS[0], MATCHED[0])]
def pad2(img, n2=32, off=8): # embed 16x16 render into 32x32 background
    big = [[BG] * n2 for _ in range(n2)]
    for y in range(N):
        for x in range(N): big[y + off][x + off] = img[y][x]
    return big
pairP = [pad2(i) for i in pair]
log("S2 sanity: T1 prop-only pair distance at f=1 vs nominal threshold; T4 distance ratio when the same pair sits on a 32px canvas (4x area)")
t1, t4 = {}, {}
for m in MODELS:
    d1 = mind(dists(pair, 1, m), (0, 1))
    # for T4 compare at the same physical sprite size: 32px canvas at factor 1 vs 16px canvas at factor 1
    d4 = mind(dists(pairP, 1, m), (0, 1))
    t1[m[0]] = d1 >= m[3]; t4[m[0]] = d4 / d1 if d1 > 0 else 0.0
    log(f"  {m[0]:9s} d16={d1:.4f} (T={m[3]}) T1 prop-visible={'pass' if t1[m[0]] else 'FAIL'}  d32/d16={t4[m[0]]:.3f}")
inv = lambda r: r >= 0.95
DEF = [m for m in MODELS if t1[m[0]] and inv(t4[m[0]])]
p2 = (not t1["area-mean"]) and t4["area-mean"] <= 0.3 and all(t1[n] and inv(t4[n]) for n in ("raw-peak", "V1-peak", "V2-peak")) \
     and 0.6 <= t4["V1-b4"] <= 0.9 and (not t1["V1-b4"] or not inv(t4["V1-b4"]))
log(f"  defensible set (T1 pass and T4 ratio>=0.95): {[m[0] for m in DEF]}   P2 {'holds' if p2 else 'FAILS'}")

# ---------------- P3 floor across defensible models -------------------------------------
log("S3 shape cast S8 confusable of 28 at nominal threshold, by physical size (16/8/4/2 px):")
rows = {}
for m in MODELS:
    cs = {f: count(getd("S8", S8, m, f), m[3]) for f in FS}
    rows[m[0]] = cs
    onset = next((f for f in FS if cs[f] >= cs[1] + 7), None)
    mono = all(cs[FS[i]] <= cs[FS[i + 1]] for i in range(3))
    log(f"  {m[0]:9s} {[cs[f] for f in FS]} onset_f={onset} monotone={mono}{'  [not defensible]' if m not in DEF else ''}")
dn = [m for m in DEF if m[0] in ("raw-peak", "V1-peak", "V2-peak")]
DEFALL = DEF
p3 = all(rows[m[0]][8] - rows[m[0]][1] >= 7 for m in dn) and len(dn) == 3
on_v2 = next((f for f in FS if rows["V2-peak"][f] >= rows["V2-peak"][1] + 7), None)
p3 = p3 and on_v2 is not None and on_v2 <= 4
log(f"  V2-peak onset f={on_v2}   P3 {'holds' if p3 else 'FAILS'}")

# ---------------- P4 threshold robustness ------------------------------------------------
log("S4 threshold sweep (0.25x..4x nominal): grid points where count(f=8)-count(f=1) >= 7, of 9")
p4 = True
rob = {}
for m in MODELS:
    hits = sum(1 for g in GRID if count(getd("S8", S8, m, 8), m[3] * g) - count(getd("S8", S8, m, 1), m[3] * g) >= 7)
    rob[m[0]] = hits
    log(f"  {m[0]:9s} {hits}/9")
    if m in dn and hits < 6: p4 = False
log(f"  P4 {'holds' if p4 else 'FAILS'}")

# ---------------- P5 vs colour -------------------------------------------------------------
log("S5 at f=8 (2 px), nominal threshold, confusable of 28: shape S8 / luminance-spread recolour R8 / hybrid H8; and the same at f=4")
p5 = True
for m in MODELS:
    s, r, h = (count(getd(k, CASTS[k], m, 8), m[3]) for k in ("S8", "R8", "H8"))
    s4, r4, h4 = (count(getd(k, CASTS[k], m, 4), m[3]) for k in ("S8", "R8", "H8"))
    log(f"  {m[0]:9s} f8 S8={s:2d} R8={r:2d} H8={h:2d} | f4 S8={s4:2d} R8={r4:2d} H8={h4:2d}")
    if m in dn and not (s - r >= 3 and h <= r): p5 = False
log(f"  P5 {'holds' if p5 else 'FAILS'}")

# ---------------- P6 BREAK: information floor --------------------------------------------------
log("S6 BREAK area-matched symmetric bodies A4 (6 pairs), nominal threshold, by f=1/2/4/8; and body-only B4 for contrast")
res6 = {}
for m in MODELS:
    a = [count(getd("A4", A4, m, f), m[3]) for f in FS]
    b = [count(getd("B4", B4, m, f), m[3]) for f in FS]
    res6[m[0]] = a
    log(f"  {m[0]:9s} A4={a}  B4={b}")
p6 = all(res6[m[0]][0] == 0 and res6[m[0]][3] == 6 for m in MODELS) and res6["raw-peak"][2] < 6 and res6["V2-peak"][2] >= 4
log(f"  P6 {'holds' if p6 else 'FAILS'}")

# ---------------- post-hoc (NOT pre-registered) ----------------------------------------------------
log("X1 (post-hoc) body-only B4 vs 4-way luminance-spread recolour R4 (indices 1,3,5,7) at nominal, f=8/4, defensible peak models")
R4 = [render(BODIES[1], SPREAD[i]) for i in (1, 3, 5, 7)]
for m in dn:
    b8, b4 = count(getd("B4", B4, m, 8), m[3]), count(getd("B4", B4, m, 4), m[3])
    r8, r4c = count(dists(R4, 8, m), m[3]), count(dists(R4, 4, m), m[3])
    log(f"  {m[0]:9s} B4 f8={b8} f4={b4} (of 6)  R4 f8={r8} f4={r4c} (of 6)")

# ---------------- P7-P9: anchored threshold window -------------------------------------------------
log("S7 anchored window per model: T_lo = distance of 2%-luminance whole-body pair, T_hi = distance of visible prop pair (both f=1)")
jnd = [render(BODIES[0], MATCHED[0]), render(BODIES[0], srgb(tuple(1.02 * lin(c) for c in MATCHED[0])))]
win = {}
for m in MODELS:
    lo = mind(dists(jnd, 1, m), (0, 1)); hi = mind(dists(pair, 1, m), (0, 1))
    win[m[0]] = (lo, hi)
    mid = (lo * hi) ** 0.5
    ts = {"T_lo": lo, "mid": mid, "T_hi/2": hi / 2}
    cnt = {k: (count(getd("S8", S8, m, 1), t), count(getd("S8", S8, m, 2), t), count(getd("S8", S8, m, 4), t), count(getd("S8", S8, m, 8), t)) for k, t in ts.items()}
    log(f"  {m[0]:9s} window=[{lo:.4f},{hi:.4f}]{' EMPTY' if lo >= hi else ''}  S8 counts f1/2/4/8: " + "  ".join(f"{k}={v}" for k, v in cnt.items()))
    win[m[0]] = (lo, hi, cnt)
gap = lambda c: c[3] - c[0]
p7 = all(gap(win["area-mean"][2][k]) <= 1 for k in ("T_lo", "mid", "T_hi/2")) and all(win[n][0] < win[n][1] for n in ("raw-peak", "V1-peak", "V2-peak", "V1-W", "V2-W"))
peaks = ("raw-peak", "V1-peak", "V2-peak", "V1-W", "V2-W")
p8 = all(gap(win[n][2]["T_lo"]) < 7 and gap(win[n][2]["T_hi/2"]) >= 7 for n in peaks)
p9 = all(gap(win[n][2]["mid"]) >= 7 for n in ("V1-W", "V2-W"))
log(f"  P7 {'holds' if p7 else 'FAILS'}  P8 {'holds' if p8 else 'FAILS'}  P9 {'holds' if p9 else 'FAILS'}")
# colour vs shape inside the window, at T_hi/2 and mid, f=8 and f=4
log("S8 inside the window (mid threshold): confusable of 28, S8 shape / R8 lum-spread recolour / H8 hybrid at f=4 and f=8")
for n in peaks:
    m = [x for x in MODELS if x[0] == n][0]; t = (win[n][0] * win[n][1]) ** 0.5
    v = {k: (count(getd(k, CASTS[k], m, 4), t), count(getd(k, CASTS[k], m, 8), t)) for k in ("S8", "R8", "H8")}
    log(f"  {n:9s} T={t:.4f} " + "  ".join(f"{k}(f4,f8)={v[k]}" for k in v))

log("X2 (post-hoc, not pre-registered) fraction of 25 log-spaced thresholds in each window where shape S8 is strictly MORE confusable than lum-spread recolour R8, by size f=1/2/4/8; and where S8 has any floor-gap>=7")
for n in peaks + ("area-mean",):
    m = [x for x in MODELS if x[0] == n][0]; lo, hi = win[n][0], win[n][1]
    ts = [lo * (hi / lo) ** (i / 24) for i in range(25)]
    fr = [sum(1 for t in ts if count(getd("S8", S8, m, f), t) > count(getd("R8", R8, m, f), t)) / 25 for f in FS]
    gp = sum(1 for t in ts if count(getd("S8", S8, m, 8), t) - count(getd("S8", S8, m, 1), t) >= 7) / 25
    log(f"  {n:9s} P(S8>R8) at f1/2/4/8 = {fr}  floor-gap>=7 at {gp:.2f} of window")

ok = p1 and p2 and p3 and p4 and p5 and p6 and p7 and p8 and p9
flags = [n for n, v in zip(("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"), (p1, p2, p3, p4, p5, p6, p7, p8, p9)) if not v]
print(f"RESULT: {'PASS' if ok else 'FAIL'} held={9-len(flags)}/9" + (f" failed={','.join(flags)}" if flags else "") +
      f"; defensible={[m[0] for m in DEF]}; S8 counts f1/f8 " + " ".join(f"{k}={v[1]}/{v[8]}" for k, v in rows.items()) +
      f"; grid-robust " + " ".join(f"{k}={v}/9" for k, v in rob.items()))
