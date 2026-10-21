"""Rebuild of seven E12 (own fixture). Claim: a behaviour test that places an
agent at a computed position without checking it is legal measures the agent's
inability to exist, and its failure rate tracks terrain density, so it reads
as a consistent behavioural finding.
Model: 30x30 grid, rock fraction d (own LCG). The behaviour under test: an
agent heads for a goal and must take >= 1 step. In rock it has no start cell
and never moves. Naive placement = a computed point (LCG). Legal placement =
nearest open cell to that point. 200 episodes per density.
"""
from collections import deque

N, EP = 30, 200


class Lcg:
    def __init__(self, s):
        self.s = s

    def u(self):
        self.s = (1103515245 * self.s + 12345) % 2 ** 31
        return self.s / 2 ** 31


def make_map(d, seed):
    r = Lcg(seed)
    return {(x, y) for x in range(N) for y in range(N) if r.u() < d}


def moves(rock, start, goal):
    if start in rock:
        return False
    seen, q = {start}, deque([start])
    while q:
        c = q.popleft()
        if c == goal:
            return c != start
        x, y = c
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= n[0] < N and 0 <= n[1] < N and n not in rock and n not in seen:
                seen.add(n)
                q.append(n)
    return False


def nearest_open(rock, p):
    for r in range(N):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                c = (p[0] + dx, p[1] + dy)
                if 0 <= c[0] < N and 0 <= c[1] < N and c not in rock:
                    return c
    raise ValueError("no open cell")


def rate(d, legal):
    rock = make_map(d, 7)
    goal = nearest_open(rock, (N - 1, N - 1))
    r, ok = Lcg(99), 0
    for _ in range(EP):
        p = (int(r.u() * N), int(r.u() * N))
        if legal:
            p = nearest_open(rock, p)
        ok += moves(rock, p, goal)
    return ok / EP, len(rock) / N ** 2


def main():
    rows = []
    for d in (0.05, 0.15, 0.25, 0.35):
        naive, frac = rate(d, False)
        legal, _ = rate(d, True)
        rows.append((d, frac, naive, legal))
        print(f"density {d:.2f} (rock {frac:.3f}): naive pass {naive:.3f}  legal pass {legal:.3f}")
    gap = max(abs((1 - f) - n) for _, f, n, l in rows if l >= 0.99)
    checks = [
        ("naive pass rate falls as density rises", all(a[2] > b[2] for a, b in zip(rows, rows[1:]))),
        ("naive failures track the rock fraction within 0.08 wherever legal placement is clean", gap <= 0.08),
        ("legal placement keeps the pass rate >= 0.90 at every density", all(r[3] >= 0.90 for r in rows)),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"d{d:.2f} naive {n:.3f} legal {l:.3f}" for d, f, n, l in rows))


if __name__ == "__main__":
    main()
