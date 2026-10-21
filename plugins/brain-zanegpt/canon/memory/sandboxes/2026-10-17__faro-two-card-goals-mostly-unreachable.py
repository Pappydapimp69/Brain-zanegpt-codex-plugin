# Faro shuffles move every card at once, so a goal for TWO cards is a goal for one joint state.
# Exhaustive BFS over (pos of card a, pos of card b) under IN/OUT faros. No RNG.
# PREDICTION (before first run): in a 16-card deck most of the 240 ordered position pairs are reachable
# for a given card pair (over half), and only the top/bottom pair is special.
from collections import deque
def where(p, n, k): h = n // 2; return 2 * p + (k == 'in') if p < h else 2 * (p - h) + (k != 'in')
def reach(n, a, b):
    s = (a, b); seen = {s}; q = deque([s])
    while q:
        x = q.popleft()
        for k in ('in', 'out'):
            y = tuple(where(p, n, k) for p in x)
            if y not in seen: seen.add(y); q.append(y)
    return seen
for n in (8, 16, 52):
    pairs = n * (n - 1)
    r_tb = reach(n, 0, n - 1); r_05 = reach(n, 0, 5 % n)
    mirror = all(x + y == n - 1 for x, y in r_tb)
    print(f'n={n}: top+bottom reach {len(r_tb)}/{pairs} (always mirrored: {mirror}); cards 0 and 5 reach {len(r_05)}/{pairs}')
r16 = len(reach(16, 0, 5)); r52 = len(reach(52, 0, 5))
# restated claim after the run (the prediction above was refuted for power-of-two decks):
ok = r16 == 32 and r52 >= 2600 and all(x + y == 15 for x, y in reach(16, 0, 15))
print(f'RESULT: {"PASS" if ok else "FAIL"} two-card faro goals: 16 cards reach only {r16}/240 joint positions, 52 cards {r52}/2652; top and bottom always mirror (sum n-1); check reachability before setting a multi-card goal')
