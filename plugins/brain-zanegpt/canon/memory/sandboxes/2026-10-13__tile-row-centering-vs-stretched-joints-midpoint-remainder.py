"""Sandbox: dry-lay centering (flooring kernel) vs spreading the remainder over joints
with the knitting midpoint rule. Integer units of 0.5 mm, no RNG."""
U = 2  # units per mm

def piece(x, t, p):
    """visible width of the tile at a wall where the grid line offset is x (0<=x<p)."""
    return t - x if x < t else t

def cuts(W, t, g, mode):
    p = t + g
    if mode == "wall":
        o = 0
    elif mode == "tile":      # a tile centred on the room centre line
        o = (W - t) // 2 % p
    else:                     # a joint centred
        o = (W - g) // 2 % p - p + t  # tile ends at centre-g/2
        o %= p
    left = piece((-o) % p, t, p)
    right = piece((o - W) % p, t, p)
    return left, right

def best_of_two(W, t, g):
    a = min(cuts(W, t, g, "tile")); b = min(cuts(W, t, g, "joint"))
    return max(a, b)

def sweep(t, g, lo, hi):
    n = 0; wall_bad = tile_bad = joint_bad = best_bad = 0; mn = 10**9
    thr = t // 4
    for W in range(lo, hi + 1):
        n += 1
        if min(cuts(W, t, g, "wall")) < thr: wall_bad += 1
        if min(cuts(W, t, g, "tile")) < thr: tile_bad += 1
        if min(cuts(W, t, g, "joint")) < thr: joint_bad += 1
        b = best_of_two(W, t, g)
        if b < thr: best_bad += 1
        mn = min(mn, b)
    return n, wall_bad / n, tile_bad / n, joint_bad / n, best_bad, mn

def midpoint_positions(n, k):
    return [(2 * i + 1) * n // (2 * k) for i in range(k)]

def stretched(W, t, g):
    """full tiles only, remainder R spread over n-1 joints by the knitting midpoint rule."""
    p = t + g
    n = (W + g) // p
    if n < 2: return None
    R = W - (n * t + (n - 1) * g)
    k = n - 1
    pos = midpoint_positions(k, min(R, k)) if R <= k else None
    # joint extra: base R//k each, plus 1 on midpoint-chosen joints for R%k
    base, rem = divmod(R, k)
    extra = [base] * k
    for i in midpoint_positions(k, rem) if rem else []:
        extra[i] += 1
    joints = [g + e for e in extra]
    return n, joints

def main():
    res = []
    # S1 reproduce kernel numbers: t300 g3 mm -> units
    t, g = 300 * U, 3 * U
    n, wb, tb, jb, bb, mn = sweep(t, g, 1500 * U, 4500 * U)
    print(f"S1 t300 g3 W1500..4500 (0.5mm steps, n={n}): wall<quarter={wb:.3f} tile={tb:.3f} joint={jb:.3f} best_bad={bb} min_best={mn/U:.1f}mm")
    res.append(wb > 0.15 and bb == 0 and mn >= t // 4)
    # S2 other tile sizes: does best-of-two keep >= ~half-tile minus pitch share?
    for tt in (150, 600):
        n, wb2, tb2, jb2, bb2, mn2 = sweep(tt * U, 3 * U, 5 * tt * U, 15 * tt * U)
        print(f"S2 t{tt}: wall_bad={wb2:.3f} best_bad={bb2} min_best/t={mn2/(tt*U):.3f}")
        res.append(bb2 == 0 and mn2 / (tt * U) > 0.45)
    # S3 BREAK: row pinned at one wall (doorway) -> only wall start allowed
    n, wb3, *_ = sweep(t, g, 1500 * U, 4500 * U)
    print(f"S3 pinned wall start: thin-cut rate={wb3:.3f} (best-of-two guarantee unavailable)")
    res.append(wb3 > 0.15)
    # S4 knitting midpoint kernel applied to joints: spread <= 1 unit, vs dump-all-in-last-joint
    worst_mid = worst_naive = 0; wide = 0; cnt = 0
    for W in range(1500 * U, 4500 * U + 1):
        s = stretched(W, t, g)
        if not s: continue
        cnt += 1
        n_, joints = s
        worst_mid = max(worst_mid, max(joints) - min(joints))
        R = W - (n_ * t + (n_ - 1) * g)
        worst_naive = max(worst_naive, R)
        if max(joints) > 2 * g: wide += 1
    print(f"S4 stretched joints: midpoint joint spread max={worst_mid} unit, naive last-joint extra max={worst_naive/U:.1f}mm, widths with joint>2*grout={wide}/{cnt} ({wide/cnt:.2f})")
    res.append(worst_mid <= 1 and worst_naive > 10)
    # S5 break for stretch alternative: needs visible joint tolerance; compare with centring which has no joint change
    print(f"S5 stretched joints are only usable when joint<=2*grout: usable in {1-wide/cnt:.2f} of widths; centring is usable in 1.00 at same edge-cut quality?")
    res.append(wide / cnt > 0.5)
    ok = all(res)
    print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" checks={res}")

main()
