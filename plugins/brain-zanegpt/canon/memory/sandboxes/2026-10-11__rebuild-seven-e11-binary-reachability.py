"""Rebuild of seven E11 (own fixture). Claim: a boolean reachability contract
enforced by a repair pass gives a terrain pass no stopping rule; a distance
budget does; and unreachable must be reported as INFINITE, or a caller testing
dist <= budget passes it.
Model: 21x21 grid, start at centre, 6 markers. Each round adds walls at
pseudo-random open cells (own LCG). BOOLEAN: after each round, any unreachable
marker gets an L-shaped corridor carved to it. BUDGET: same walls, but a round
is rolled back whole if the worst marker distance would exceed the budget.
"""
from collections import deque

N, START = 21, (10, 10)
MARKERS = [(1, 1), (1, 19), (19, 1), (19, 19), (10, 1), (1, 10)]


class Lcg:
    def __init__(self, s):
        self.s = s

    def next(self, n):
        self.s = (1103515245 * self.s + 12345) % 2 ** 31
        return self.s % n


def bfs(walls):
    d = {START: 0}
    q = deque([START])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in walls and (nx, ny) not in d:
                d[(nx, ny)] = d[(x, y)] + 1
                q.append((nx, ny))
    return d


def worst(walls, sentinel):
    d = bfs(walls)
    return max(d.get(m, sentinel) for m in MARKERS)


def carve(walls, m):
    x, y = START
    while x != m[0]:
        x += 1 if m[0] > x else -1
        walls.discard((x, y))
    while y != m[1]:
        y += 1 if m[1] > y else -1
        walls.discard((x, y))


def add_round(walls, rng, k=25):
    new = set(walls)
    for _ in range(k):
        c = (rng.next(N), rng.next(N))
        if c != START and c not in MARKERS:
            new.add(c)
    return new


def run(mode, rounds, budget):
    rng, walls = Lcg(42), set()
    for _ in range(rounds):
        cand = add_round(walls, rng)
        if mode == "boolean":
            d = bfs(cand)
            for m in MARKERS:
                if m not in d:
                    carve(cand, m)
            walls = cand
        else:
            if worst(cand, float("inf")) <= budget:
                walls = cand
    return worst(walls, float("inf")), len(walls)


def main():
    budget = 2 * N  # 42
    base = worst(set(), float("inf"))
    rows = {}
    for r in (0, 10, 20, 40):
        rows[r] = (run("boolean", r, budget), run("budget", r, budget))
        print(f"rounds {r:2d}: boolean worst walk {rows[r][0][0]} walls {rows[r][0][1]} | "
              f"budget worst walk {rows[r][1][0]} walls {rows[r][1][1]}")
    # sentinel check: a caller testing dist <= budget
    walled = {(x, y) for x in range(N) for y in range(N) if abs(x - 10) + abs(y - 10) == 3}
    neg = worst(walled, -1)
    inf = worst(walled, float("inf"))
    print(f"sealed-start check: sentinel -1 -> worst {neg} (passes <= budget: {neg <= budget}); inf -> {inf}")
    checks = [
        (f"boolean worst walk at 40 rounds exceeds the budget ({rows[40][0][0]} > {budget})", rows[40][0][0] > budget),
        ("boolean contract stays satisfied (all reachable) while walks grow", rows[40][0][0] < float("inf")),
        ("budget version never exceeds the budget", all(rows[r][1][0] <= budget for r in rows)),
        ("a -1 'unreachable' sentinel passes the naive budget check", neg <= budget),
        ("an infinite sentinel fails it", not (inf <= budget)),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; base walk {base}; "
          f"boolean@40 {rows[40][0][0]}; budget@40 {rows[40][1][0]} (budget {budget})")


if __name__ == "__main__":
    main()
