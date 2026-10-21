"""Squint test on 16x16 sprites: does hue-shift / cel shading carry shape that the
silhouette does not?

Poses (same body, same head):
  A arm across the chest   - silhouette identical to B
  B arm hanging inside the body outline
  C arm raised outside the body - silhouette differs from A
Light from the upper left: body left half lit, right half in shadow (one cel
step); the arm is nearer the light and takes the highlight tone.

Ramps per base colour:
  flat        one tone everywhere
  value       same hue, shadow 0.6x, highlight 1.3x in HSV value
  hueshift    shadow hue rotated 25 deg toward blue (240), sat +0.1, value 0.6x;
              highlight rotated 25 deg toward yellow (60), sat -0.1, value 1.3x
  isolum      the hueshift hues, rescaled so each tone's luminance equals the base
  gooch       2-band Gooch cel (cel-shading E5): k_cool=(0,0,.4)+.2kd,
              k_warm=(.4,.4,0)+.6kd, shadow t=.25, lit t=.75, highlight t=1
Squint = WCAG relative luminance, then 4x4 average pooling (16x16 -> 4x4).
Readability of a pose pair = max |difference| of pooled luminance.
Threshold 0.02 (2% luminance) as the 'can tell apart' line.
"""
import colorsys

W = H = 16
BG = (0.45, 0.47, 0.50)
BASES = {
    "red": (0.80, 0.25, 0.20),
    "green": (0.30, 0.65, 0.30),
    "blue": (0.25, 0.35, 0.80),
    "tan": (0.80, 0.62, 0.42),
    "purple": (0.55, 0.30, 0.65),
}
THRESH = 0.02


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (lin(min(1.0, max(0.0, x))) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def rot_toward(h_deg, target, amt):
    d = (target - h_deg + 540) % 360 - 180
    step = max(-amt, min(amt, d))
    return (h_deg + step) % 360


def shift(rgb, target_hue, dsat, vscale):
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    h2 = rot_toward(h * 360, target_hue, 25) / 360
    s2 = min(1, max(0, s + dsat))
    v2 = min(1, v * vscale)
    return colorsys.hsv_to_rgb(h2, s2, v2)


def match_lum(rgb, target):
    # scale toward equal luminance by bisection on a uniform multiplier
    lo, hi = 0.0, 4.0
    for _ in range(60):
        m = (lo + hi) / 2
        if lum(tuple(min(1, x * m) for x in rgb)) < target:
            lo = m
        else:
            hi = m
    return tuple(min(1, x * lo) for x in rgb)


def ramps(base):
    h, s, v = colorsys.rgb_to_hsv(*base)
    out = {}
    out["flat"] = (base, base, base)
    out["value"] = (colorsys.hsv_to_rgb(h, s, v * 0.6), base, colorsys.hsv_to_rgb(h, s, min(1, v * 1.3)))
    sh = shift(base, 240, 0.1, 0.6)
    hi = shift(base, 60, -0.1, 1.3)
    out["hueshift"] = (sh, base, hi)
    L = lum(base)
    out["isolum"] = (match_lum(shift(base, 240, 0.1, 1.0), L), base, match_lum(shift(base, 60, -0.1, 1.0), L))

    def gooch(t):
        kc = (0.2 * base[0], 0.2 * base[1], 0.4 + 0.2 * base[2])
        kw = (0.4 + 0.6 * base[0], 0.4 + 0.6 * base[1], 0.6 * base[2])
        return tuple(min(1, (1 - t) * a + t * b) for a, b in zip(kc, kw))

    out["gooch"] = (gooch(0.25), gooch(0.75), gooch(1.0))
    return out


def masks(pose):
    body = set()
    for y in range(4, 16):
        for x in range(5, 11):
            body.add((x, y))
    for y in range(1, 4):
        for x in range(6, 10):
            body.add((x, y))
    arm = set()
    if pose == "A":  # across the chest, inside outline
        arm = {(x, y) for y in (7, 8) for x in range(5, 11)}
    elif pose == "B":  # hanging along the lit side, inside outline
        arm = {(x, y) for y in range(6, 13) for x in (5, 6)}
    elif pose == "C":  # raised, outside outline
        arm = {(x, y) for y in range(1, 8) for x in (11, 12)}
    return body, arm


def render(pose, ramp, bg=None):
    shadow, mid, high = ramp
    body, arm = masks(pose)
    bg = BG if bg is None else bg
    img = [[bg for _ in range(W)] for _ in range(H)]
    for (x, y) in body:
        img[y][x] = mid if x <= 7 else shadow
    for (x, y) in arm:
        img[y][x] = high
    return img


def squint(img, f=4):
    L = [[lum(p) for p in row] for row in img]
    out = []
    for by in range(0, H, f):
        row = []
        for bx in range(0, W, f):
            s = sum(L[y][x] for y in range(by, by + f) for x in range(bx, bx + f))
            row.append(s / (f * f))
        out.append(row)
    return out


def diff(a, b):
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def raw_rgb_diff(a, b):
    return max(max(abs(p - q) for p, q in zip(pa, pb)) for ra, rb in zip(a, b) for pa, pb in zip(ra, rb))


def main():
    names = ["flat", "value", "hueshift", "isolum", "gooch"]
    ab = {n: [] for n in names}
    ab_rgb = {n: [] for n in names}
    ac_flat = []
    for cname, base in BASES.items():
        rs = ramps(base)
        for n in names:
            ia, ib = render("A", rs[n]), render("B", rs[n])
            ab[n].append(diff(squint(ia), squint(ib)))
            ab_rgb[n].append(raw_rgb_diff(ia, ib))
        ac_flat.append(diff(squint(render("A", rs["flat"])), squint(render("C", rs["flat"]))))
        print(cname, " ".join(f"{n}={ab[n][-1]:.4f}" for n in names), f"silhouetteAC={ac_flat[-1]:.4f}")
    for n in names:
        print(f"A/B squint diff {n}: min {min(ab[n]):.4f} max {max(ab[n]):.4f}; "
              f"unsquinted max RGB diff {max(ab_rgb[n]):.3f}")
    print(f"A/C flat silhouette squint diff: min {min(ac_flat):.4f} max {max(ac_flat):.4f}")

    ok = True
    ok &= max(ab["flat"]) == 0.0
    ok &= max(ab["isolum"]) < 0.005
    ok &= min(ab["value"]) > THRESH and min(ab["hueshift"]) > THRESH
    hs_ge = sum(1 for a, b in zip(ab["hueshift"], ab["value"]) if a >= b)
    print(f"hueshift >= value on {hs_ge}/5 colours")
    ok &= hs_ge == 5
    ok &= min(ab["gooch"]) > THRESH
    best_shading = max(max(ab[n]) for n in names)
    print(f"largest shading-only A/B diff {best_shading:.4f} vs smallest silhouette A/C {min(ac_flat):.4f}")
    ok &= min(ac_flat) > 0.1 and min(ac_flat) > best_shading
    # Added after run 1 (criteria above unchanged): where does the silhouette read?
    black = ((0.0, 0.0, 0.0),) * 3
    sil_black = diff(squint(render("A", black)), squint(render("C", black)))
    print(f"standard black-fill silhouette check A/C on mid-grey bg: {sil_black:.4f}")
    fg = []
    dark_ac, dark_ab_val, dark_ab_hs = [], [], []
    for cname, base in BASES.items():
        rs = ramps(base)
        fg.append(abs(lum(base) - lum(BG)))
        dbg = (0.06, 0.06, 0.08)
        dark_ac.append(diff(squint(render("A", rs["flat"], dbg)), squint(render("C", rs["flat"], dbg))))
        dark_ab_hs.append(diff(squint(render("A", rs["hueshift"], dbg)), squint(render("B", rs["hueshift"], dbg))))
    print("figure-ground luminance gap per colour on mid-grey:", " ".join(f"{x:.3f}" for x in fg),
          f"(bg lum {lum(BG):.3f})")
    print("dark bg: silhouette A/C flat", " ".join(f"{x:.3f}" for x in dark_ac),
          "| hueshift A/B", " ".join(f"{x:.3f}" for x in dark_ab_hs))
    wins_dark = sum(1 for a, b in zip(dark_ac, dark_ab_hs) if a > b)
    wins_mid = sum(1 for a, n in zip(ac_flat, ab["hueshift"]) if a > n)
    print(f"silhouette A/C beats hueshift A/B: mid-grey bg {wins_mid}/5, dark bg {wins_dark}/5")
    print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
          f"A/B squint flat {max(ab['flat']):.3f}, isolum max {max(ab['isolum']):.4f} "
          f"(raw RGB diff {max(ab_rgb['isolum']):.2f}), value min {min(ab['value']):.3f}, "
          f"hueshift min {min(ab['hueshift']):.3f} (>= value {hs_ge}/5), gooch min {min(ab['gooch']):.3f}; "
          f"silhouette A/C min {min(ac_flat):.3f} vs best shading {best_shading:.3f}; "
          f"black-fill silhouette {sil_black:.3f}; silhouette beats hueshift mid-grey {wins_mid}/5, dark bg {wins_dark}/5")


if __name__ == "__main__":
    main()
