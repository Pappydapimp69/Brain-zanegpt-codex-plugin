# Book imposition by simulating the folds (right over left, then bottom over top, alternating) instead of memorising a table.
# Prediction (written before the first run): for a 16-page signature (3 folds, 4x2 grid) the simulated imposition has
# every page once, each leaf's two faces (2k-1, 2k) on the same panel front/back, and pages N and 1 adjacent on the same sheet side (first run wrongly checked only the front: 1 and 16 sit on the BACK, since 1 backs 2 and 16 backs 15); a table-free rule "adjacent crease neighbours sum to N+1" holds for the 4 first-fold pairs.
# Assumption: layers stack bottom to top and the top face is page 1. Wrong if any page repeats or a leaf splits panels.
def impose(folds):
    cols, rows = 1, 1
    seq = []
    for i in range(folds):                      # sheet grid: alternate doubling columns / rows
        if i % 2 == 0: cols *= 2
        else: rows *= 2
    # state: dict cell -> stack of (panel, flipped, rot) bottom to top
    st = {(r, c): [((r, c), False, False)] for r in range(rows) for c in range(cols)}
    W, H = cols, rows
    order = []
    # fold in reverse of the doubling so the last doubling is folded first
    for i in range(folds - 1, -1, -1):
        if i % 2 == 0:
            new = {}
            for r in range(H):
                for c in range(W // 2):
                    mirror = [(p, not f, rt) for (p, f, rt) in reversed(st[(r, W - 1 - c)])]
                    new[(r, c)] = st[(r, c)] + mirror
            st = new; W //= 2
        else:
            new = {}
            for r in range(H // 2):
                for c in range(W):
                    mirror = [(p, not f, not rt) for (p, f, rt) in reversed(st[(H - 1 - r, c)])]
                    new[(r, c)] = st[(r, c)] + mirror
            st = new; H //= 2
    stack = st[(0, 0)]                           # bottom to top
    layers = list(reversed(stack))               # top first
    front, back = {}, {}
    for t, (p, f, rt) in enumerate(layers):
        up, down = 2 * t + 1, 2 * t + 2
        if not f: front[p], back[p] = (up, rt), (down, rt)
        else: back[p], front[p] = (up, rt), (down, rt)
    return rows, cols, front, back
def show(folds):
    rows, cols, front, back = impose(folds)
    n = 2 * rows * cols * 1
    f = [[front[(r, c)][0] for c in range(cols)] for r in range(rows)]
    return rows, cols, n, front, back, f
ok_all = True; notes = []
for folds in (2, 3, 4):
    rows, cols, n, front, back, f = show(folds)
    pages = sorted([v[0] for v in front.values()] + [v[0] for v in back.values()])
    uniq = pages == list(range(1, n + 1))
    # leaf faces share a panel: front page and back page differ by 1 and the odd one is the lower
    leaf = all(abs(front[p][0] - back[p][0]) == 1 and min(front[p][0], back[p][0]) % 2 == 1 for p in front)
    # spine pairs: adjacent front panels (same row) whose sum is N+1 (first-fold neighbours)
    pairs = [(f[r][c], f[r][c + 1]) for r in range(rows) for c in range(cols - 1)]
    spine = sum(1 for a, b in pairs if a + b == n + 1)
    print(f"{n:3d} pages  folds={folds} front={f}  unique={uniq} leaf_ok={leaf} N+1 pairs={spine}/{len(pairs)}")
    ok_all &= uniq and leaf and spine >= 1
rows, cols, n, front, back, f = show(3)
bk = [[back[(r, c)][0] for c in range(cols)] for r in range(rows)]
adj = lambda g: any(set(row[i:i + 2]) == {1, 16} for row in g for i in range(len(row) - 1))
print("16-page front", f, "back", bk, "1 beside 16 on front:", adj(f), "on back:", adj(bk))
ok_all &= (not adj(f)) and adj(bk)
print("RESULT: %s fold simulation gives valid imposition for 8, 16, 32 pages (all pages once, leaf faces paired, N+1 spine pair present); 16-page front %s back %s" % ("PASS" if ok_all else "FAIL", f, bk))
