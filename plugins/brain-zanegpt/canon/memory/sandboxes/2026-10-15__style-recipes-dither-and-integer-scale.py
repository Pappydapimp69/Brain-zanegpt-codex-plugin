"""Sandbox: two visual-style recipes, checked numerically (stdlib only, deterministic).
1) Bayer 4x4 ordered dither renders 17 distinct tones from two colours.
2) Integer nearest-neighbour upscale keeps every art pixel the same size (no mixels);
   a non-integer scale (2.5x) does not. A third case BREAKS the claim on purpose: integer scale
   plus a half-pixel offset (sub-pixel position) also produces mixed sizes."""
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

def dither_coverage(lum):
    on = sum(1 for y in range(4) for x in range(4) if lum > (BAYER[y][x] + .5) / 16)
    return on

levels = sorted({dither_coverage(i / 1000) for i in range(1001)})
print('distinct dither coverages over a 4x4 tile:', len(levels), levels)

def run_widths(n_art, scale, offset=0.0):
    # nearest-neighbour: screen pixel s samples art pixel floor((s - offset) / scale)
    width = int(n_art * scale)
    owner = [int((s - offset) // scale) for s in range(width)]
    sizes = {}
    for o in owner:
        if 0 <= o < n_art: sizes[o] = sizes.get(o, 0) + 1
    inner = [sizes[o] for o in range(1, n_art - 1)]   # ignore edge pixels clipped by the offset
    return sorted(set(inner))

s_int = run_widths(16, 3)
s_frac = run_widths(16, 2.5)
s_off = run_widths(16, 3, offset=1.5)
print('integer x3 sizes:', s_int, '| x2.5 sizes:', s_frac, '| x3 with 1.5px offset:', s_off)
ok = len(levels) == 17 and s_int == [3] and len(s_frac) > 1
print('break case (offset) stays uniform:', s_off == [3])
print(f"RESULT: {'PASS' if ok else 'FAIL'} bayer 17 levels={len(levels) == 17}; integer scale uniform {s_int}; 2.5x mixed {s_frac}; offset x3 {s_off}")
