"""Pixel-art kernels in one sandbox: selective outlining (dark outline where the form
meets the background/shadow, a lighter body tint on the lit side), the silhouette
squint test, and hue-shift shading at 16x16 (base + 1 shadow + 1 highlight).
A 16x16 character silhouette is shaded with a hue-shifted 3-step ramp (light from top
left), outlined three ways (none, uniform black, selective) and placed on three
backgrounds (night, grass, sky). Metrics, all computed:
  separation = share of outline-ring/boundary pixels whose relative-luminance contrast
               ratio with the adjacent background pixel is >= 1.5
  squint IoU = shrink 4x by box average, mark cells that differ from the background by
               more than 0.08 in luminance, IoU against the shrunk silhouette
Deterministic, no RNG.
PREDICTION (written before running): on grass and sky, selective >= uniform black >
none for separation; on night, both dark outlines separate under 50% of the boundary
(dark against dark), so 'dark against the background' is only right when the
background is lighter than the outline."""
MASK = """
......XXXX......
.....XXXXXX.....
.....XXXXXX.....
......XXXX......
....XXXXXXXX....
...XXXXXXXXXX...
...XX.XXXX.XX...
...XX.XXXX.XX...
......XXXX......
......XXXX......
.....XX..XX.....
.....XX..XX.....
.....XX..XX.....
....XXX..XXX....
................
................""".split()
H, W = 16, 16
inside = lambda y, x: 0 <= y < H and 0 <= x < W and MASK[y][x] == "X"
def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
RAMP = {"shadow": (70, 60, 120), "base": (190, 70, 60), "hi": (245, 160, 90)}   # cool shadow, warm highlight
BG = {"night": (20, 22, 40), "grass": (90, 140, 60), "sky": (170, 210, 240)}
def shade(y, x):
    # lit from top-left: a pixel whose up-left neighbour is outside is highlight, down-right outside is shadow
    if not inside(y - 1, x) or not inside(y, x - 1): return RAMP["hi"]
    if not inside(y + 1, x) or not inside(y, x + 1): return RAMP["shadow"]
    return RAMP["base"]
def render(outline, bg):
    img = [[BG[bg]] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if inside(y, x): img[y][x] = shade(y, x)
    ring = []
    for y in range(H):
        for x in range(W):
            if inside(y, x): continue
            nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if any(inside(*p) for p in nb):
                ring.append((y, x))
                if outline == "black": img[y][x] = (10, 10, 14)
                elif outline == "selective":
                    lit = inside(y + 1, x) or inside(y, x + 1)          # body below/right of this ring pixel = lit side
                    img[y][x] = (230, 120, 80) if lit else (16, 12, 30)
    return img, ring
def separation(img, ring, bg, outline):
    ok = tot = 0
    for y, x in ring:
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and not inside(yy, xx) and (yy, xx) not in ring:
                ref = img[y][x] if outline != "none" else None
                if outline == "none":   # boundary is the body pixel next to this ring cell vs background
                    body = [img[y + a][x + b] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if inside(y + a, x + b)][0]
                    ref = body
                tot += 1; ok += ratio(ref, BG[bg]) >= 1.5
                break
    return ok / tot
def squint(img, bg):
    inter = union = 0
    for by in range(0, H, 4):
        for bx in range(0, W, 4):
            cells = [(y, x) for y in range(by, by + 4) for x in range(bx, bx + 4)]
            avg = sum(lum(img[y][x]) for y, x in cells) / 16
            seen = abs(avg - lum(BG[bg])) > 0.08
            truth = sum(inside(y, x) for y, x in cells) >= 6
            inter += seen and truth; union += seen or truth
    return inter / union
R = {}
for bg in BG:
    for ol in ("none", "black", "selective"):
        img, ring = render(ol, bg)
        R[(bg, ol)] = (separation(img, ring, bg, ol), squint(img, bg))
    print(bg.ljust(6), "  ".join(f"{ol}: sep {R[(bg, ol)][0]:4.0%} squint {R[(bg, ol)][1]:.2f}" for ol in ("none", "black", "selective")))
p1 = all(R[(b, "selective")][0] >= R[(b, "black")][0] > R[(b, "none")][0] for b in ("grass", "sky"))
p2 = R[("night", "black")][0] < 0.5 and R[("night", "selective")][0] < 0.5
print(f"RESULT: {'PASS' if p1 and p2 else 'FAIL'} grass/sky selective>=black>none: {p1}; night both dark outlines <50%: {p2} "
      f"(night black {R[('night','black')][0]:.0%}, selective {R[('night','selective')][0]:.0%}, none {R[('night','none')][0]:.0%})")
