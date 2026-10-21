"""Bookbinding: fold a flat sheet into a signature, track where every page lands
(imposition) and which way the grain runs relative to the spine (the last fold).
Pure stdlib, deterministic. Each fold halves the current LONGER side (standard
right-angle folding); ties fold across x.
"""

def fold_signature(width, height, nfolds):
    # cells of the flat sheet: grid of cols x rows; positions tracked through folds
    cols = rows = 1
    w, h = width, height
    axes = []  # which ORIGINAL axis each fold line runs parallel to
    for _ in range(nfolds):
        if w >= h:   # fold across x: halves width, fold line runs parallel to original y? track below
            axes.append("x"); w /= 2; cols *= 2
        else:
            axes.append("y"); h /= 2; rows *= 2
    # simulate stacking: state per cell = (x, y, depth, up) where up=True means front face is up
    cells = {(i, j): [i, j, 0, True] for i in range(cols) for j in range(rows)}
    cw, ch, layers = cols, rows, 1
    pre_last = None
    for k, ax in enumerate(axes):
        if k == len(axes) - 1:
            pre_last = {c: list(s) for c, s in cells.items()}
            last_dims = (cw, ch)
        for c, s in cells.items():
            if ax == "x" and s[0] >= cw // 2:
                s[0] = cw - 1 - s[0]; s[2] = 2 * layers - 1 - s[2]; s[3] = not s[3]
            elif ax == "y" and s[1] >= ch // 2:
                s[1] = ch - 1 - s[1]; s[2] = 2 * layers - 1 - s[2]; s[3] = not s[3]
        if ax == "x": cw //= 2
        else: ch //= 2
        layers *= 2
    # number pages: top layer (depth layers-1) is leaf 1; its up face is page 1
    npages = 2 * len(cells)
    page = {}  # (cell, side) -> page, side 'front'/'back' of the flat sheet
    for c, s in cells.items():
        leaf = layers - 1 - s[2]           # 0 = top
        up_page, down_page = 2 * leaf + 1, 2 * leaf + 2
        page[(c, "front")] = up_page if s[3] else down_page
        page[(c, "back")] = down_page if s[3] else up_page
    # conjugate cells: mirror partners across the last fold line
    last = axes[-1]
    conj = {}
    for c, s in pre_last.items():
        for d, t in pre_last.items():
            if d != c and t[2] == s[2] and ((last == "x" and t[1] == s[1] and t[0] == last_dims[0] - 1 - s[0]) or
                                            (last == "y" and t[0] == s[0] and t[1] == last_dims[1] - 1 - s[1])):
                conj[c] = d
    return page, npages, axes, conj

def spine_parallel_to(axes):
    # a fold across x (halving width) makes a fold LINE parallel to the original y edge
    return "y" if axes[-1] == "x" else "x"

NAMES = {1: "folio", 2: "quarto", 3: "octavo", 4: "16mo", 5: "32mo"}
results = {}
all_pages_ok = conj_ok = True
SQRT2 = 2 ** 0.5
for n in range(1, 6):
    page, N, axes, conj = fold_signature(SQRT2, 1.0, n)   # landscape A-series sheet: long side along x
    pages = sorted(page.values())
    all_pages_ok &= pages == list(range(1, N + 1))
    for c, d in conj.items():
        for side in ("front", "back"):
            conj_ok &= page[(c, side)] + page[(d, side)] == N + 1
    spine = spine_parallel_to(axes)
    results[n] = (N, axes, spine, sorted(v for (c, s), v in page.items() if s == "front"))
    long_grain_ok = spine == "x"  # long-grain sheet: grain parallel to the long (x) side
    print(f"{NAMES[n]:7s} {N:3d} pages, folds {''.join(axes)}, spine parallel to {spine} -> "
          f"{'LONG' if long_grain_ok else 'SHORT'}-grain sheet needed; one forme: {results[n][3] if N <= 16 else '...'}")

outer8 = results[3][3] if 1 in results[3][3] else sorted(set(range(1, 17)) - set(results[3][3]))
print("octavo outer forme (side holding page 1):", outer8)

# BREAK: a 4:1 strip. Long side stays long after one fold, so two folds run the same way
page, N, axes, conj = fold_signature(4.0, 1.0, 2)
strip_spine = spine_parallel_to(axes)
print(f"4:1 strip quarto: folds {''.join(axes)}, spine parallel to {strip_spine} (A-sheet quarto: {results[2][2]})")

# Practical: long-grain A4/A3 stock (grain along long side, an assumption about copier paper)
print("long-grain A4 folded once (A5 folio):", "grain OK" if results[1][2] == "x" else "CROSS grain")
print("long-grain A3 folded twice (A5 quarto):", "grain OK" if results[2][2] == "x" else "CROSS grain")

# Predictions written before the first run
checks = {
    "every page 1..N appears once (n=1..5)": all_pages_ok,
    "conjugate pages sum to N+1 on each face": conj_ok,
    "octavo outer forme is 1,4,5,8,9,12,13,16": outer8 == [1, 4, 5, 8, 9, 12, 13, 16],
    "odd folds need short grain, even folds long grain": all((results[n][2] == "x") == (n % 2 == 0) for n in range(1, 6)),
    "BREAK: 4:1 strip quarto keeps the folio parity (spine parallel to y)": strip_spine == "y",
}
for k, v in checks.items(): print(("ok  " if v else "MISS"), k)
s = sum(checks.values())
print(f"RESULT: {'PASS' if s == len(checks) else 'FAIL'} {s}/{len(checks)}; folio/octavo/32mo short grain, quarto/16mo long grain; "
      f"octavo outer forme {outer8}; 4:1 strip quarto spine parallel to {strip_spine}")
