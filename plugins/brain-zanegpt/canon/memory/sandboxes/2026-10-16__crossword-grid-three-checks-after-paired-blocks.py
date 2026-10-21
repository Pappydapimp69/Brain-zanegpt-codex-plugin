# American-style crossword grid rules on a 5x5: 180-degree symmetry, all white squares connected,
# every across/down entry at least 3 letters long. Exhaustive over all 2^13 symmetric block patterns.
from collections import deque
n = 5
cells = [(r, c) for r in range(n) for c in range(n)]
half = [(r, c) for (r, c) in cells if (r, c) <= (n - 1 - r, n - 1 - c)]  # one representative per symmetric pair (+ centre)
def symmetric(b): return all(((r, c) in b) == ((n - 1 - r, n - 1 - c) in b) for r, c in cells)
def connected(b):
    whites = [x for x in cells if x not in b]
    if not whites: return False
    seen, q = {whites[0]}, deque([whites[0]])
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x = (r + dr, c + dc)
            if 0 <= x[0] < n and 0 <= x[1] < n and x not in b and x not in seen: seen.add(x); q.append(x)
    return len(seen) == len(whites)
def min_len_ok(b):
    for line in range(n):
        for get in (lambda i: (line, i), lambda i: (i, line)):
            run = 0
            for i in range(n + 1):
                if i < n and get(i) not in b: run += 1
                else:
                    if 0 < run < 3: return False
                    run = 0
    return True
pats = []
for m in range(1 << len(half)):
    b = set()
    for i, (r, c) in enumerate(half):
        if m >> i & 1: b.add((r, c)); b.add((n - 1 - r, n - 1 - c))
    pats.append(b)
total = len(pats)
sym_ok = sum(symmetric(b) for b in pats)
all3 = sum(symmetric(b) and connected(b) and min_len_ok(b) for b in pats)
fail_conn_only = sum(not connected(b) and min_len_ok(b) for b in pats)
fail_len_only = sum(connected(b) and not min_len_ok(b) for b in pats)
# single-cell toggling (not paired) on an empty grid breaks symmetry for every non-centre cell
single_breaks = sum(not symmetric({x}) for x in cells)
print(total, sym_ok, all3, fail_conn_only, fail_len_only, single_breaks)
ok = sym_ok == total == 8192 and single_breaks == 24 and 0 < all3 < total // 2 and fail_conn_only > 0 and fail_len_only > 0
print("RESULT: %s paired placement kept symmetry in %d/%d patterns but only %d (%.1f%%) pass connectivity and min length; "
      "connectivity-only failures %d, length-only failures %d; unpaired single block broke symmetry in %d/25 cells" % (
      "PASS" if ok else "FAIL", sym_ok, total, all3, 100 * all3 / total, fail_conn_only, fail_len_only, single_breaks))
