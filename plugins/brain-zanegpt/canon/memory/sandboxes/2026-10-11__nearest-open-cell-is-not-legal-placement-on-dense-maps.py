"""Sandbox (follow-up to seven E12): nearest OPEN cell is not legal placement on a dense map.
Original rebuild header follows. Claim: a behaviour test that places an
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


def nearest_connected(rock, p, goal):
    seen, q = {goal}, deque([goal])
    while q:
        x, y = q.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= n[0] < N and 0 <= n[1] < N and n not in rock and n not in seen:
                seen.add(n)
                q.append(n)
    seen.discard(goal)
    return min(seen, key=lambda c: (abs(c[0] - p[0]) + abs(c[1] - p[1]), c))


def rate(d, legal):
    rock = make_map(d, 7)
    goal = nearest_open(rock, (N - 1, N - 1))
    r, ok = Lcg(99), 0
    for _ in range(EP):
        p = (int(r.u() * N), int(r.u() * N))
        if legal == "open":
            p = nearest_open(rock, p)
        elif legal == "connected":
            p = nearest_connected(rock, p, goal)
        ok += moves(rock, p, goal)
    return ok / EP, len(rock) / N ** 2


def main():
    rows = []
    for d in (0.05, 0.15, 0.25, 0.35, 0.40):
        naive, frac = rate(d, None)
        op, _ = rate(d, "open")
        con, _ = rate(d, "connected")
        rows.append((d, naive, op, con))
        print(f"density {d:.2f}: naive {naive:.3f}  nearest-open {op:.3f}  nearest-connected {con:.3f}")
    checks = [
        ("nearest-open drops below 0.90 at density 0.35 or more", min(r[2] for r in rows if r[0] >= 0.35) < 0.90),
        ("nearest-connected placement passes every episode at every density", all(r[3] == 1.0 for r in rows)),
        ("break case: at low density nearest-open and nearest-connected agree", rows[0][2] == rows[0][3]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"d{d:.2f} open {o:.3f} connected {c:.3f}" for d, n, o, c in rows))


if __name__ == "__main__":
    main()
