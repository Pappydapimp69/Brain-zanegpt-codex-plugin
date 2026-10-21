"""Pass 1 sandbox: hue-shift shading x selective outlining x cel-shading E5.
Deterministic, stdlib only. Disc sprite lit from the upper left, banded
(cel-style) ramp, selective outline: black where the rim faces away from the
light, a light tint of the body colour where it faces the light.
Metric: WCAG contrast between each outline pixel and the body pixel it borders.
"""
import colorsys, math

def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb):
    r, g, b = (lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
    return (r, g, b)

def toward(h, target, deg):
    d = ((target - h + 540) % 360) - 180
    step = math.copysign(min(abs(d), deg), d)
    return (h + step) % 360

def match_lum(h, s, target_lum):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if lum(hsl(h, s, mid)) < target_lum:
            lo = mid
        else:
            hi = mid
    return hsl(h, s, (lo + hi) / 2)

COOL, WARM, STEP = 270.0, 60.0, 15.0
S = 0.6

def ramp(base_h, size, mode):
    """Returns list of tones darkest..lightest and the threshold list on N.L."""
    if size == 16:
        levels = [(-1, 0.35), (0, 0.55)]          # shadow, base (+highlight below)
        levels.append((1, 0.75))
        cuts = [0.0, 0.75]
    else:
        levels = [(-2, 0.20), (-1, 0.35), (0, 0.55), (1, 0.75)]
        cuts = [-0.35, 0.15, 0.75]
    tones = []
    for k, L in levels:
        same = hsl(base_h, S, L)
        if mode == 'same':
            tones.append(same); continue
        if k < 0:
            h = toward(base_h, COOL, STEP * -k); s = max(0.0, S - 0.08 * -k)
        elif k > 0:
            h = toward(base_h, WARM, STEP * k); s = min(1.0, S + 0.08 * k)
        else:
            h, s = base_h, S
        if mode == 'shift':
            tones.append(hsl(h, s, L))
        elif mode == 'floor':  # hue-shifted, darkest tone lifted to contrast 2.0 vs black
            t = hsl(h, s, L)
            if lum(t) < 0.05:
                t = match_lum(h, s, 0.05 + 1e-6)
            tones.append(t)
        else:  # 'shiftlum': hue shift at the same relative luminance as same-hue tone
            tones.append(match_lum(h, s, lum(same)))
    return tones, cuts

LIGHT = (-1 / math.sqrt(3), -1 / math.sqrt(3), 1 / math.sqrt(3))  # upper-left-front

def render(base_h, size, mode):
    tones, cuts = ramp(base_h, size, mode)
    r = size / 2 - 1.5
    c = (size - 1) / 2
    body = {}
    for y in range(size):
        for x in range(size):
            dx, dy = (x - c) / r, (y - c) / r
            d2 = dx * dx + dy * dy
            if d2 <= 1.0:
                nz = math.sqrt(max(0.0, 1 - d2))
                ndl = dx * LIGHT[0] + dy * LIGHT[1] + nz * LIGHT[2]
                idx = sum(1 for t in cuts if ndl > t)
                body[(x, y)] = tones[idx]
    outline = {}
    for y in range(size):
        for x in range(size):
            if (x, y) in body:
                continue
            nb = [(x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + a, y + b) in body]
            if not nb:
                continue
            dx, dy = (x - c), (y - c)
            facing = dx * LIGHT[0] + dy * LIGHT[1] > 0
            outline[(x, y)] = (facing, nb)
    return body, outline, tones

def evaluate(base_h, size, mode, thresh=2.0):
    body, outline, tones = render(base_h, size, mode)
    dark = (0.0, 0.0, 0.0)
    shadow_pairs = lost = 0
    for (p, (facing, nb)) in outline.items():
        if facing:
            continue
        for q in nb:
            shadow_pairs += 1
            if contrast(dark, body[q]) < thresh:
                lost += 1
    return lost / shadow_pairs, contrast(dark, tones[0]), tones

BASES = [('red', 0), ('skin', 20), ('orange', 30), ('green', 120), ('blue', 210)]

def main():
    print('base   size  darkest-tone contrast vs black (same / shift / shiftlum)   lost-line share (same / shift / shiftlum)')
    drops = {}
    res = {}
    for name, h in BASES:
        for size in (16, 32):
            row = {}
            for mode in ('same', 'shift', 'shiftlum'):
                row[mode] = evaluate(h, size, mode)
            res[(name, size)] = row
            print(f"{name:6s} {size:3d}   {row['same'][1]:5.2f} / {row['shift'][1]:5.2f} / {row['shiftlum'][1]:5.2f}"
                  f"            {row['same'][0]*100:5.1f}% / {row['shift'][0]*100:5.1f}% / {row['shiftlum'][0]*100:5.1f}%")
        a, b = res[(name, 32)]['same'][1], res[(name, 32)]['shift'][1]
        drops[name] = (a - b) / a
    # hue retained by the lum-matched fix
    hues = []
    for name, h in BASES:
        tones, _ = ramp(h, 32, 'shiftlum')
        hh = colorsys.rgb_to_hls(*tones[0])[0] * 360
        hues.append(abs(((hh - h + 540) % 360) - 180))
    print('32px darkest-tone contrast drop from hue shift:', {k: round(v * 100, 1) for k, v in drops.items()})
    print('lum-matched deep-shadow hue offset from base (deg):', [round(x, 1) for x in hues])
    nonblue = [k for k in drops if k != 'blue']
    lowered = sum(1 for k in drops if drops[k] > 0)
    mean_drop = sum(drops[k] for k in nonblue) / len(nonblue)
    lost32_shift = sum(res[(n, 32)]['shift'][0] for n, _ in BASES) / len(BASES)
    lost32_same = sum(res[(n, 32)]['same'][0] for n, _ in BASES) / len(BASES)
    lost16_shift = sum(res[(n, 16)]['shift'][0] for n, _ in BASES) / len(BASES)
    lost16_same = sum(res[(n, 16)]['same'][0] for n, _ in BASES) / len(BASES)
    fix_ok = all(abs(res[(n, s)]['shiftlum'][0] - res[(n, s)]['same'][0]) < 1e-9 for n, _ in BASES for s in (16, 32))
    print(f'mean lost share 32px same {lost32_same*100:.1f}% shift {lost32_shift*100:.1f}%; 16px same {lost16_same*100:.1f}% shift {lost16_shift*100:.1f}%')
    t15 = {}
    for name, h in BASES:
        t15[name] = (evaluate(h, 32, 'same', 1.5)[0], evaluate(h, 32, 'shift', 1.5)[0])
    print('32px lost share at threshold 1.5 (same, shift):', {k: (round(a*100,1), round(b*100,1)) for k, (a, b) in t15.items()})
    flips15 = sum(1 for a, b in t15.values() if b > a)
    floor32 = [evaluate(h, 32, 'floor')[0] for _, h in BASES]
    distinct = all(len(set(tuple(round(c, 4) for c in t) for t in ramp(h, 32, 'floor')[0])) == 4 for _, h in BASES)
    print('32px floor-fix lost share:', [round(x*100,1) for x in floor32], 'distinct tones 4:', distinct)
    deep_bases = sum(1 for n, _ in BASES if res[(n, 32)]['same'][0] >= 0.40 and res[(n, 32)]['shift'][0] >= 0.40)
    rev = (deep_bases >= 4 and lost16_shift == 0 and lost16_same == 0 and max(floor32) == 0 and distinct and flips15 >= 2)
    print(f"original prediction holds: {lowered >= 4 and mean_drop >= 0.15 and lost32_shift >= 0.5 and lost32_same <= 0.25 and drops['blue'] <= 0}")
    print(f"RESULT: {'PASS' if rev else 'FAIL'} 32px deep-shadow step loses >=40% of shadow-side black-outline pairs on {deep_bases}/5 bases "
          f"for same-hue AND hue-shifted ramps (16px: 0%); hue shift drops darkest-tone contrast {mean_drop*100:.1f}% mean on non-blue "
          f"(blue drop {drops["blue"]*100:.1f}%, red drop {drops["red"]*100:.1f}% i.e. rose) and loses extra lines at threshold 1.5 on {flips15}/5; "
          f"luminance floor 2.0 -> {max(floor32)*100:.1f}% lost with 4 distinct tones")

if __name__ == '__main__':
    main()
