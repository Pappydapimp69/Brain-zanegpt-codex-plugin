"""LATIN-SQUARES/sudoku clue-placement kernel measured uniqueness on ONE fixed 4x4 solution
(4 clues: 12 of 1820 unique, 0.7%; 5 clues: 400 of 4368, 9.2%). Do those rates hold across
all 288 4x4 Sudoku grids? Exhaustive: enumerate all grids, and for every grid every 4-clue
subset, count solutions up to 2 (precomputed: a clue set is unique iff exactly one of the
288 grids agrees with it). Deterministic.
PREDICTION (written before running): the 288 grids split into two classes with DIFFERENT
4-clue uniqueness counts, so the kernel's 12/1820 is true only for its grid's class; the
2-distinct-digit rule (never unique) holds on every grid."""
import itertools
cells = [(r, c) for r in range(4) for c in range(4)]
def grids():
    out = []
    def rec(g, k):
        if k == 16: out.append(tuple(g)); return
        r, c = divmod(k, 4)
        for v in range(1, 5):
            if all(g[r * 4 + j] != v for j in range(c)) and all(g[i * 4 + c] != v for i in range(r)):
                br, bc = r // 2 * 2, c // 2 * 2
                if all(g[i * 4 + j] != v for i in range(br, br + 2) for j in range(bc, bc + 2) if i * 4 + j < k):
                    g[k] = v; rec(g, k + 1); g[k] = 0
    rec([0] * 16, 0); return out
G = grids(); print("grids:", len(G))
subsets = list(itertools.combinations(range(16), 4))
# index: for each (cell, value) the set of grid ids having it
has = {(i, v): {gi for gi, g in enumerate(G) if g[i] == v} for i in range(16) for v in range(1, 5)}
counts = []; two_digit_unique = 0
for gi, g in enumerate(G):
    u = 0
    for sub in subsets:
        agree = set.intersection(*(has[(i, g[i])] for i in sub))
        if len(agree) == 1:
            u += 1
            if len({g[i] for i in sub}) <= 2: two_digit_unique += 1
    counts.append(u)
classes = sorted(set(counts))
print("distinct 4-clue unique counts across grids:", {c: counts.count(c) for c in classes}, "(per grid, of 1820)")
ok = len(classes) == 2 and 12 in classes and two_digit_unique == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} 4-clue unique sets per grid take values {classes} over 288 grids "
      f"({ {c: counts.count(c) for c in classes} } grids each); unique sets with <=2 distinct digits: {two_digit_unique}")
