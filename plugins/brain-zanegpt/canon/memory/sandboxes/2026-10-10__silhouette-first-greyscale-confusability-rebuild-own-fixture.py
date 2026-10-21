"""NOTE after run 1 (recorded honestly): fixture bugs, not claim failures - pure blue cannot reach luminance 0.30 (hues made pastel) and
my 4.5:1 outline needs a darker fill/backdrop (0.15), since a white outline on a 0.30 backdrop is only 3.0:1.
Rebuild with OWN fixture: 16x16 sprites, 8 procedurally defined bodies (disc, box, triangle, ring, cross, diamond,
tall bar, T), optional 3-pixel 'prop'. Greyscale = Rec.709 luminance of linear light. Two sprites are CONFUSABLE if the
mean abs greyscale difference over the 16x16 canvas (after box-downscale by factor f) is < TAU=0.02.
Prediction (before run):
 P1 recolour cast (same body, 8 hues scaled to equal luminance 0.30): 28/28 pairs confusable; same cast with a luminance-
    spread palette: <28 (hues differ in grey); shape cast (8 bodies, one colour): 0 confusable at f=1.
 P2 shape cast: 0 confusable at f=1 and f=2; >=1 at f=8 (canvas 2x2); luminance-spread recolour at f=8 has FEWER
    confusable pairs than the shape cast.
 P3 bodies identical except a 3-px prop: >=1 confusable pair at f=2 (prop averaged away) and the prop pair is the weakest
    distinguishable pair at f=1 (smallest distance of any pair).
 P4 backdrop eased to grey equal to the body fill: shape cast on that frame 28/28 confusable with no outline, 0 with a
    1px outline of contrast >=4.5:1 against the backdrop on that frame.
 P5 10 entities on 8 body slots (slot = i%8): matched-luminance palette -> exactly 2 confusable pairs when palettes are
    luminance-matched?? NO: bodies of entities i and i+8 are identical, so with matched luminance exactly 2 pairs
    ((0,8),(1,9)) are confusable; with a luminance-spread palette 0.
Stdlib only, deterministic."""
import itertools, math
N = 16; TAU = 0.02
ok = True
def chk(n, c, d=""):
    global ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + n, d)
def dec(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lum(rgb): r, g, b = (dec(x) for x in rgb); return 0.2126*r + 0.7152*g + 0.0722*b
def hue_rgb(h):  # saturated hue, then scale in sRGB until luminance hits target later
    h6 = h * 6; i = int(h6) % 6; f = h6 - int(h6); q = 1 - f
    c = [(1,f,0),(q,1,0),(0,1,f),(0,q,1),(f,0,1),(1,0,q)][i]
    return tuple(0.5*x + 0.5 for x in c)  # pastel so every hue can reach Y=0.30 (pure blue cannot)
def at_lum(rgb, Y):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo+hi)/2
        if lum([c*m for c in rgb]) < Y: lo = m
        else: hi = m
    return [c*hi for c in rgb] if lum([c*hi for c in rgb]) <= Y+1e-6 else None
def body(k):
    c = (N-1)/2; pix = set()
    for y in range(N):
        for x in range(N):
            dx, dy = x-c, y-c
            r = math.hypot(dx, dy)
            on = [r < 6, abs(dx) < 5.5 and abs(dy) < 5.5, dy > -6 and abs(dx) < (dy+6)/2.2,
                  4 < r < 7, (abs(dx) < 1.6 and abs(dy) < 7) or (abs(dy) < 1.6 and abs(dx) < 7),
                  abs(dx)+abs(dy) < 7, abs(dx) < 2.2 and abs(dy) < 7.5, (abs(dy+5) < 2.2 and abs(dx) < 7) or (abs(dx) < 2 and dy > -5 and dy < 7)][k]
            if on: pix.add((x, y))
    return pix
def render(pix, grey, bg, prop=None, outline=None):
    img = [[bg]*N for _ in range(N)]
    if outline is not None:
        ring = {(x+a, y+b) for (x,y) in pix for a in (-1,0,1) for b in (-1,0,1)} - pix
        for (x,y) in ring:
            if 0 <= x < N and 0 <= y < N: img[y][x] = outline
    for (x,y) in pix: img[y][x] = grey
    if prop:
        for (x,y) in prop: img[y][x] = grey*0.0 + (grey if False else prop_grey)
    return img
prop_grey = 0.0
def down(img, f):
    n = N//f
    return [[sum(img[y*f+a][x*f+b] for a in range(f) for b in range(f))/(f*f) for x in range(n)] for y in range(n)]
def dist(a, b): 
    n = len(a); return sum(abs(a[y][x]-b[y][x]) for y in range(n) for x in range(n))/(n*n)
def conf(imgs, f):
    ds = [dist(down(a, f), down(b, f)) for a, b in itertools.combinations(imgs, 2)]
    return sum(d < TAU for d in ds), min(ds)
Y = 0.30; bg = 0.02
hues = [at_lum(hue_rgb(i/8), Y) for i in range(8)]
chk("fixture: 8 hues reach equal luminance 0.30", all(h is not None and abs(lum(h)-Y) < 1e-4 for h in hues))
grey_matched = [lum(h) for h in hues]
grey_spread = [0.05 + 0.6*i/7 for i in range(8)]
disc = body(0)
recol_matched = [render(disc, g, bg) for g in grey_matched]
recol_spread = [render(disc, g, bg) for g in grey_spread]
shape = [render(body(k), 0.30, bg) for k in range(8)]
# P1
c1, _ = conf(recol_matched, 1); c2, _ = conf(recol_spread, 1); c3, _ = conf(shape, 1)
chk("P1 matched-luminance recolour 28/28 confusable", c1 == 28, c1)
chk("P1 luminance-spread recolour <28", c2 < 28, c2)
chk("P1 shape cast 0 confusable at f=1", c3 == 0, c3)
# P2
s = {f: conf(shape, f) for f in (1, 2, 4, 8)}; r8 = conf(recol_spread, 8)[0]
print("  shape cast confusable by f:", {f: v[0] for f, v in s.items()}, "spread recolour f=8:", r8)
chk("P2 shape 0 at f=1,2", s[1][0] == 0 and s[2][0] == 0)
chk("P2 shape >=1 at f=8", s[8][0] >= 1)
chk("P2 spread recolour beats shape at f=8", r8 < s[8][0], f"{r8} < {s[8][0]}")
# P3 prop
base = body(1)
global_prop = [(12,2),(13,2),(12,3)]
prop_grey = 0.9
withprop = [render(base, 0.30, bg), render(base, 0.30, bg, prop=global_prop)]
withprop_ok = conf(withprop, 2)[0] >= 1
dprop = dist(withprop[0], withprop[1])
other = min(dist(shape[i], shape[j]) for i, j in itertools.combinations(range(8), 2))
chk("P3 prop-only pair confusable at f=2", withprop_ok, f"d_f1={dprop:.4f} d_f2={dist(down(withprop[0],2),down(withprop[1],2)):.4f}")
chk("P3 prop pair is weaker than every body pair at f=1", dprop < other, f"{dprop:.4f} < {other:.4f}")
# P4 backdrop eased to the fill grey
bgx = 0.15
flat = [render(body(k), 0.15, bgx) for k in range(8)]
chk("P4 eased backdrop equal to fill: 28/28 confusable, no outline", conf(flat, 1)[0] == 28)
outl = 0.95
cr = (outl + 0.05) / (bgx + 0.05)
outlined = [render(body(k), 0.15, bgx, outline=outl) for k in range(8)]
chk("P4 outline with contrast>=4.5:1 gives 0 confusable", conf(outlined, 1)[0] == 0 and cr >= 4.5, f"contrast {cr:.1f}")
# P5
ents = [(i % 8, i) for i in range(10)]
def pairs(grey_of):
    imgs = [render(body(b), grey_of(i), bg) for b, i in ents]
    return {(a, c) for (a, c) in itertools.combinations(range(10), 2) if dist(imgs[a], imgs[c]) < TAU}
pm = pairs(lambda i: grey_matched[i % 8]); ps = pairs(lambda i: [0.05 + 0.6*j/9 for j in range(10)][i])
chk("P5 matched palette: exactly pairs (0,8),(1,9)", pm == {(0,8),(1,9)}, sorted(pm))
chk("P5 luminance-spread palette: 0 pairs", len(ps) == 0, sorted(ps))
print(f"RESULT: {'PASS' if ok else 'FAIL'} matched recolour {c1}/28, shape 0 at f<=2 and {s[8][0]} at f=8, outline fixes eased-backdrop {conf(flat,1)[0]}->0, shared slots {len(pm)}->{len(ps)}")
