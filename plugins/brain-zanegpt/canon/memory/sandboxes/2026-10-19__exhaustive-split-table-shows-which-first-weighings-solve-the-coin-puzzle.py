# Prediction (written before the run): with 12 coins and 3 weighings (one odd coin, direction unknown) exactly ONE
# first pan size works: 4 v 4. The obvious half split 6 v 6 fails, as do 1,2,3,5. With 13 coins and no spare nothing
# works; one spare genuine coin makes a first weighing possible for 13 (the existing lesson says it buys exactly one more).
from functools import lru_cache
@lru_cache(None)
def solve(u, l, h, g, k):
    """Can the odd coin be identified in k weighings? u unknown, l maybe-light, h maybe-heavy, g known genuine."""
    c = u + l + h
    if c <= 1: return True
    if k == 0 or 2 * u + l + h > 3 ** k: return False
    for ul in range(u + 1):
     for ur in range(u - ul + 1):
      for ll in range(l + 1):
       for lr in range(l - ll + 1):
        for hl in range(h + 1):
         for hr in range(h - hl + 1):
            L = ul + ll + hl; R = ur + lr + hr
            if L + R == 0 or abs(L - R) > g: continue
            tl = (0, ur + lr, ul + hl)           # left heavy: right-light or left-heavy candidates
            tr = (0, ul + ll, ur + hr)           # left light
            bal = (u - ul - ur, l - ll - lr, h - hl - hr)
            if all(solve(x[0], x[1], x[2], g + c - sum(x), k - 1) for x in (tl, tr, bal)):
                return True
    return False
def first_moves(n, spare, k=3):
    out = []
    for m in range(1, n // 2 + 1):          # m v m
        if solve(0, m, m, n - 2 * m + spare, k - 1) and solve(n - 2 * m, 0, 0, 2 * m + spare, k - 1): out.append(f"{m}v{m}")
    if spare:
        for m in range(1, (n + 1) // 2):    # m+1 v m using the spare coin on the short pan
            if solve(0, m, m + 1, n - 2 * m - 1 + 0, k - 1) and solve(0, m, m + 1, n - (2 * m + 1) + 1, k - 1) and solve(n - 2 * m - 1, 0, 0, 2 * m + 1 + 1, k - 1):
                out.append(f"{m+1}v{m}+spare")
    return out
res = {}
for n, spare in ((12, 0), (13, 0), (13, 1)):
    res[(n, spare)] = first_moves(n, spare); print("n", n, "spare", spare, "working first weighings", res[(n, spare)])
ok = res[(12, 0)] == ["4v4"] and res[(13, 0)] == [] and len(res[(13, 1)]) > 0
print("RESULT:", "PASS" if ok else "FAIL",
      f"12 coins/3 weighings: first splits that work {res[(12,0)]} (6v6 fails); 13 coins no spare {res[(13,0)]}; 13 with one spare {res[(13,1)]}")
