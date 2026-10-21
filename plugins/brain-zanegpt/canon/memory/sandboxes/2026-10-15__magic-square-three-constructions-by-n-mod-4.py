"""Sandbox: which construction builds a magic square depends on n mod 4. Real scenario: a puzzle/print generator
that must emit a valid n x n magic square (rows, columns, both diagonals sum to n(n^2+1)/2, entries 1..n^2 once).
PREDICTION (before first run): Siamese (up-right, drop down on collision) is valid for 8 of 8 odd n in 3..17 and for
0 of 6 even n in 4..14 (it breaks the diagonals or the placement); the doubly-even complement method (fill 1..n^2 in
order, replace k by n^2+1-k on the diagonals of each 4x4 block) is valid for n=4,8,12 (3 of 3); Strachey's method
(four odd Siamese quadrants plus a left-column and middle swap) is valid for n=6,10,14 (3 of 3) while the same method
with the swap step left out is valid for 0 of 3 (BREAK: the swap is load-bearing). Assumption: one method fits all n.
Wrong if Siamese is valid for any even n, or if the no-swap Strachey is valid for any n."""
def is_magic(m):
    n = len(m); s = n * (n * n + 1) // 2
    if sorted(x for r in m for x in r) != list(range(1, n * n + 1)): return False
    return (all(sum(r) == s for r in m) and all(sum(m[i][j] for i in range(n)) == s for j in range(n))
            and sum(m[i][i] for i in range(n)) == s and sum(m[i][n - 1 - i] for i in range(n)) == s)
def siamese(n):
    m = [[0] * n for _ in range(n)]; i, j = 0, n // 2
    for k in range(1, n * n + 1):
        if m[i][j]:                      # occupied (or off-grid wrap landed on a filled cell): drop down from the previous cell
            i, j = (pi + 1) % n, pj
        m[i][j] = k; pi, pj = i, j
        i, j = (i - 1) % n, (j + 1) % n
    return m
def doubly_even(n):
    m = [[i * n + j + 1 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i % 4 == j % 4 or (i % 4) + (j % 4) == 3: m[i][j] = n * n + 1 - m[i][j]
    return m
def strachey(n, swap=True):
    h = n // 2; q = siamese(h); off = [0, 2, 3, 1]; m = [[0] * n for _ in range(n)]
    for i in range(h):
        for j in range(h):
            m[i][j] = q[i][j]; m[i + h][j + h] = q[i][j] + h * h
            m[i][j + h] = q[i][j] + 2 * h * h; m[i + h][j] = q[i][j] + 3 * h * h
    if swap:
        k = (n - 2) // 4
        for i in range(h):
            cols = list(range(k)) if i != h // 2 else list(range(1, k + 1))
            cols += list(range(n - k + 1, n))
            for j in cols: m[i][j], m[i + h][j] = m[i + h][j], m[i][j]
    return m
r = {}
r["siamese_odd"] = [is_magic(siamese(n)) for n in range(3, 18, 2)]
r["siamese_even"] = [is_magic(siamese(n)) for n in (4, 6, 8, 10, 12, 14)]
r["doubly_even"] = [is_magic(doubly_even(n)) for n in (4, 8, 12)]
r["strachey"] = [is_magic(strachey(n)) for n in (6, 10, 14)]
r["strachey_noswap"] = [is_magic(strachey(n, False)) for n in (6, 10, 14)]
for k, v in r.items(): print(k, v)
ok = all(r["siamese_odd"]) and not any(r["siamese_even"]) and all(r["doubly_even"]) and all(r["strachey"]) and not any(r["strachey_noswap"])
print("RESULT: %s siamese odd %d/%d, siamese even %d/6, doubly-even %d/3, strachey %d/3, strachey without swap %d/3"
      % ("PASS" if ok else "FAIL", sum(r["siamese_odd"]), len(r["siamese_odd"]), sum(r["siamese_even"]), sum(r["doubly_even"]), sum(r["strachey"]), sum(r["strachey_noswap"])))
