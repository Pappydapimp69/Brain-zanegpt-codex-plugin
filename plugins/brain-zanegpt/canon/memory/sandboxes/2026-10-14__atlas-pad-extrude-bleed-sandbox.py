"""1D texture-atlas bleed sandbox. Sprite A (value 0, alpha 1) at texels [0,S);
sprite B (value 1, alpha 1) starts at S+pad. Bilinear/nearest sampling of A's
UV rect [0,S] at sub-pixel shifts; measures wrong-color bleed from B and the
alpha hole left by an undefined (transparent) pad. Deterministic, stdlib only."""
S = 8
W = 64

def build(pad, extrude):
    val = [0.0] * W; alpha = [0.0] * W
    for i in range(S): val[i] = 0.0; alpha[i] = 1.0
    b0 = S + pad
    for i in range(b0, min(W, b0 + S)): val[i] = 1.0; alpha[i] = 1.0
    for i in range(b0 + S, W): val[i] = 1.0; alpha[i] = 1.0   # rest of atlas = B-like filler
    if extrude:
        for i in range(S, b0): val[i] = 0.0; alpha[i] = 1.0
        # left side of A is atlas border: clamp handles it
    return val, alpha

def mip(val, alpha):
    # premultiplied box filter
    n = len(val) // 2
    pv = [val[i] * alpha[i] for i in range(len(val))]
    v2 = []; a2 = []
    for i in range(n):
        a = (alpha[2*i] + alpha[2*i+1]) / 2
        p = (pv[2*i] + pv[2*i+1]) / 2
        a2.append(a); v2.append(p / a if a > 0 else 0.0)
    return v2, a2

def sample(val, alpha, x, bilinear):
    # x in texel units of this level; texel i has center i+0.5
    n = len(val)
    if not bilinear:
        i = min(n-1, max(0, int(x))); return val[i], alpha[i]
    f = x - 0.5; i0 = int(f // 1); t = f - i0
    i0c = min(n-1, max(0, i0)); i1c = min(n-1, max(0, i0 + 1))
    a = alpha[i0c]*(1-t) + alpha[i1c]*t
    p = val[i0c]*alpha[i0c]*(1-t) + val[i1c]*alpha[i1c]*t
    return (p / a if a > 0 else 0.0), a

def run(pad, extrude, bilinear, shifts, level=0):
    val, alpha = build(pad, extrude)
    for _ in range(level): val, alpha = mip(val, alpha)
    sc = 2 ** level
    lo, hi = 0.0, S / sc            # A's UV rect in this level's texels
    n = max(1, int(S / sc * 4))     # 4 sample points per A texel at this level
    wrong = 0.0; hole = 0.0
    for sh in shifts:
        for k in range(n):
            u = (k + 0.5) * (hi - lo) / n + sh
            u = min(hi, max(lo, u))  # quad UV clamp
            v, a = sample(val, alpha, u, bilinear)
            wrong = max(wrong, v if a > 0 else 0.0)   # color error vs A's value 0
            hole = max(hole, 1 - a)
    return round(wrong, 3), round(hole, 3)

results = {}
aligned = [0.0]; subpx = [0.0, 0.25, 0.5, 0.75]
print("== S1 nearest, pad0, integer-aligned:", run(0, False, False, aligned))
results['s1'] = run(0, False, False, aligned)
print("== S2 nearest, pad0, sub-pixel shifts:", run(0, False, False, subpx))
results['s2'] = run(0, False, False, subpx)
print("== S3 bilinear, pad0:", run(0, False, True, subpx)); results['s3'] = run(0, False, True, subpx)
print("== S4 bilinear, pad1 transparent:", run(1, False, True, subpx)); results['s4'] = run(1, False, True, subpx)
print("== S5 bilinear, pad1 extruded:", run(1, True, True, subpx)); results['s5'] = run(1, True, True, subpx)
print("== S6 (BREAK) mip level sweep, pad x extruded, bilinear: (wrong,hole)")
need = {}
for L in range(0, 4):
    row = []
    for pad in (1, 2, 4, 8):
        r = run(pad, True, True, subpx, L); row.append((pad, r))
    ok = [p for p, r in row if r[0] < 0.01]
    need[L] = ok[0] if ok else None
    print("  level", L, row, "-> min clean pad", need[L])
# nearest minification aliasing: point-sample A (alternating texels) at stride 2
alt = [float(i % 2) for i in range(S)]
print("== S7 point-sample stride-2 on alternating texels sees", sorted(set(alt[::2])), "vs true mean", sum(alt)/S)
# cost of padding and mip overhead
for pad in (0, 1, 2, 4, 8):
    used = S * S; cell = (S + pad) ** 2
    print("  pad", pad, "area waste %.1f%%" % (100 * (1 - used / cell)))
mipt = sum(W >> l for l in range(7)) / W
print("  mip chain texel total / base = %.3f" % mipt)
ok = (results['s1'][0] == 0 and results['s2'][0] > 0.4 and results['s3'][0] > 0.4
      and results['s4'][0] == 0 and results['s4'][1] > 0.4
      and results['s5'] == (0.0, 0.0) and need[0] == 1 and need[2] and need[2] > 1)
print("RESULT: %s s1=%s s2=%s s3=%s s4=%s s5=%s min-clean-pad-by-mip-level=%s" %
      ("PASS" if ok else "FAIL", results['s1'], results['s2'], results['s3'], results['s4'], results['s5'], need))
