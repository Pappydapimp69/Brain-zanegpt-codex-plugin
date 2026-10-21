"""Sandbox: can an n x n board with two squares removed be tiled by dominoes? Real scenario: a puzzle/level generator that
must only emit tileable boards. PREDICTION (before first run): the checkerboard colour count decides it: removing two
squares of the SAME colour (the opposite-corner 'mutilated board') leaves 0 tilings for n = 4, 6, 8; removing one black and
one white square leaves at least 1 tiling for EVERY such pair on 4x4 (64 pairs) and 6x6 (324 pairs) (Gomory's theorem, which
I reproduce by exhaustive search, not by citing); full-board counts are 36 (4x4), 6728 (6x6), 12988816 (8x8). BREAK: an
odd side (n = 5, 7) has an odd area so one removed square can never be tileable whatever its colour: 0 of 25 and 0 of 49 single
removals tile. Assumption: colour balance is necessary but maybe not sufficient. Wrong if any opposite-colour pair on 4x4 or
6x6 has 0 tilings, or any same-colour pair has more than 0."""
from functools import lru_cache
def count(n, holes):
    holes = frozenset(holes)
    @lru_cache(maxsize=None)
    def go(filled_mask, pos):
        while pos < n * n and (filled_mask >> pos) & 1: pos += 1
        if pos == n * n: return 1
        r, c = divmod(pos, n); tot = 0
        if c + 1 < n and not (filled_mask >> (pos + 1)) & 1:
            tot += go(filled_mask | (1 << pos) | (1 << (pos + 1)), pos + 1)
        if r + 1 < n and not (filled_mask >> (pos + n)) & 1:
            tot += go(filled_mask | (1 << pos) | (1 << (pos + n)), pos + 1)
        return tot
    mask = 0
    for r, c in holes: mask |= 1 << (r * n + c)
    return go(mask, 0)
res = {}
res["full"] = {n: count(n, []) for n in (4, 6, 8)}
corner = {n: count(n, [(0, 0), (n - 1, n - 1)]) for n in (4, 6, 8)}
res["corners"] = corner
def pairs(n):
    sq = [(r, c) for r in range(n) for c in range(n)]
    same = diff = 0; zero_diff = 0; nonzero_same = 0
    for i, a in enumerate(sq):
        for b in sq[i + 1:]:
            same_col = (a[0] + a[1]) % 2 == (b[0] + b[1]) % 2
            k = count(n, [a, b])
            if same_col:
                same += 1; nonzero_same += k > 0
            else:
                diff += 1; zero_diff += k == 0
    return same, diff, nonzero_same, zero_diff
res["pairs4"] = pairs(4); res["pairs6"] = pairs(6)
res["odd"] = {n: sum(count(n, [(r, c)]) > 0 for r in range(n) for c in range(n)) for n in (5, 7)}
# the odd-side prediction above was wrong (n*n - 1 is even); corrected check: tileable exactly when the hole is on the majority colour
res["odd_exact"] = {n: all((count(n, [(r, c)]) > 0) == ((r + c) % 2 == 0) for r in range(n) for c in range(n)) for n in (5, 7)}
for k, v in res.items(): print(k, v)
res["pairs_ok"] = res["pairs4"][3] == 0 and res["pairs6"][3] == 0 and res["pairs4"][2] == 0 and res["pairs6"][2] == 0
ok = (res["full"] == {4: 36, 6: 6728, 8: 12988816} and all(v == 0 for v in corner.values())
      and res["pairs4"][3] == 0 and res["pairs6"][3] == 0 and res["pairs4"][2] == 0 and res["pairs6"][2] == 0
      and res["pairs4"][1] == 64 and res["pairs6"][1] == 324 and res["odd"] == {5: 13, 7: 25} and all(res["odd_exact"].values()))
print("RESULT: %s full %s, opposite corners %s, 4x4 mixed-colour pairs untileable %d/%d and same-colour tileable %d, 6x6 untileable %d/%d and same-colour tileable %d, odd sides tileable single removals %s (all and only the majority-colour squares: %s; my prediction of 0 was wrong, n*n-1 is even)"
      % ("PASS" if ok else "FAIL", list(res["full"].values()), list(corner.values()), res["pairs4"][3], res["pairs4"][1], res["pairs4"][2],
         res["pairs6"][3], res["pairs6"][1], res["pairs6"][2], list(res["odd"].values()), all(res["odd_exact"].values())))
