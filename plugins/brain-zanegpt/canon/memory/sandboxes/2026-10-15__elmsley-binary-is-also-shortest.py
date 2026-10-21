"""Elmsley's rule sends the top card to position p (0-indexed) by reading p in binary: 1 = in-faro, 0 = out-faro.
Is that also the FEWEST faros? Breadth-first search over the card's position, for every p, at several deck sizes.
Deterministic, stdlib only."""
from collections import deque
def where(p, n, k): return 2 * p + (k == 'in') if p < n // 2 else 2 * (p - n // 2) + (k == 'out')
def bfs(a, b, n):
    seen = {a: 0}; q = deque([a])
    while q:
        p = q.popleft()
        if p == b: return seen[p]
        for k in ('out', 'in'):
            np = where(p, n, k)
            if np not in seen: seen[np] = seen[p] + 1; q.append(np)
def elmsley(p, n):
    pos = 0
    for bit in bin(p)[2:]: pos = where(pos, n, 'in' if bit == '1' else 'out')
    return pos
res = {}
for n in (8, 16, 32, 52, 54):
    wrong = sum(elmsley(p, n) != p for p in range(1, n)); longer = sum(bfs(0, p, n) < len(bin(p)) - 2 for p in range(1, n))
    to_top = max(bfs(p, 0, n) for p in range(n))
    res[n] = (wrong, longer, to_top); print(f"n={n}: binary rule wrong for {wrong}, a shorter route exists for {longer}, worst case back to the top {to_top} faros")
ok = all(res[n][0] == 0 and res[n][1] == 0 for n in res)
print(f"RESULT: {'PASS' if ok else 'FAIL'} the binary rule is correct and shortest for every position at n=8,16,32,52,54; bringing any card back to the top takes at most {res[52][2]} faros at 52")
