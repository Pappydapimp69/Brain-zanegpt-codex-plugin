"""Pixel-art kernel: shade cooler (hue toward blue) instead of just darker. Cel lesson E5: cool shadow tones lose
contrast against a dark outline. Companion: selective outlining (outline dark against the background, lighter
against the sprite itself). Run them together: for a set of base colours, make a cel shadow tone three ways at the
same 'darkness' (HSV value x 0.65): plain darken, hue-shift 20 deg toward blue, hue-shift with the shadow's
luminance held to plain darken's. Measure WCAG contrast shadow-vs-outline (#1a1a2a) and shadow-vs-lit.
Deterministic, stdlib only."""
import colorsys
def lum(rgb):
    def ch(c): c = c / 255; return c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb); return .2126 * r + .7152 * g + .0722 * b
def contrast(a, b): la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + .05) / (lb + .05)
def hsv(rgb): return colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
def rgb(h, s, v): return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h % 1, min(1, s), min(1, v)))
def toward_blue(h, deg):   # rotate the hue toward 240 deg by up to `deg` degrees
    target = 240 / 360; d = ((target - h + .5) % 1) - .5; step = max(-deg / 360, min(deg / 360, d)); return h + step
OUTLINE = (0x1a, 0x1a, 0x2a)
BASES = {'skin': (240, 190, 150), 'grass': (90, 180, 70), 'red cape': (210, 50, 50), 'gold': (230, 190, 60), 'sky': (110, 170, 240), 'purple': (150, 90, 200)}
rows = []
for name, base in BASES.items():
    h, s, v = hsv(base)
    plain = rgb(h, s, v * .65)
    cool = rgb(toward_blue(h, 20), min(1, s * 1.1), v * .65)
    # luminance floor: raise the cool tone's value until its luminance matches plain darkening
    vv = v * .65; comp = cool
    while lum(comp) < lum(plain) and vv < 1: vv += .005; comp = rgb(toward_blue(h, 20), min(1, s * 1.1), vv)
    rows.append((name, contrast(plain, OUTLINE), contrast(cool, OUTLINE), contrast(comp, OUTLINE), contrast(base, cool), contrast(base, plain)))
    print(f"{name:9s} vs outline: plain {rows[-1][1]:.2f}, cool {rows[-1][2]:.2f}, cool+floor {rows[-1][3]:.2f} | lit vs shadow: plain {rows[-1][5]:.2f}, cool {rows[-1][4]:.2f}")
lost = [r for r in rows if r[2] < r[1] - .05]
avg_drop = sum((r[1] - r[2]) / r[1] for r in rows) / len(rows)
restored = all(r[3] >= r[1] - .02 for r in rows)
ok = len(lost) >= 4 and restored
print(f"RESULT: {'PASS' if ok else 'FAIL'} a 20-degree cool shift at equal HSV value lost outline contrast in {len(lost)}/{len(rows)} base colours (mean {avg_drop:.0%}); holding the shadow's luminance to plain darkening restored it in all; cool hue and contrast are independent once luminance is fixed")
