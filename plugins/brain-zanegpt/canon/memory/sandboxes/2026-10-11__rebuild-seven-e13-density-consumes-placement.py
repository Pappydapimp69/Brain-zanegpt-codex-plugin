"""Rebuild of seven E13 (own fixture). Claim: a generator knob that adds
terrain also destroys the raw material a later placement pass consumes, so
more density can buy FEWER obstacles; the effect is not monotonic.
Model: 25x25 grid. The density pass adds wall clusters (own LCG). The later
deadfall pass may place a deadfall on any open cell whose removal does NOT
disconnect the open region (a deadfall must not cut the map; that cell must
not be an articulation point). Legal deadfall sites are counted by Tarjan's
algorithm, computed, not assumed.
"""
import sys

sys.setrecursionlimit(10000)
N = 25


class Lcg:
    def __init__(self, s):
        self.s = s

    def next(self, n):
        self.s = (1103515245 * self.s + 12345) % 2 ** 31
        return self.s % n


def walls_after(rounds):
    r, walls = Lcg(5), set()
    for _ in range(rounds):
        for _ in range(12):
            x, y = r.next(N), r.next(N)
            for dx in (0, 1):
                for dy in (0, 1):
                    if x + dx < N and y + dy < N:
                        walls.add((x + dx, y + dy))
    return walls


def legal_sites(walls):
    open_ = {(x, y) for x in range(N) for y in range(N) if (x, y) not in walls}
    start = (0, 0) if (0, 0) in open_ else next(iter(open_))
    # restrict to the start's component
    comp, st = {start}, [start]
    while st:
        x, y = st.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in open_ and n not in comp:
                comp.add(n)
                st.append(n)
    disc, low, art, t = {}, {}, set(), [0]

    def dfs(u, parent):
        disc[u] = low[u] = t[0]
        t[0] += 1
        kids = 0
        x, y = u
        for v in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if v not in comp:
                continue
            if v not in disc:
                kids += 1
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if parent is not None and low[v] >= disc[u]:
                    art.add(u)
            elif v != parent:
                low[u] = min(low[u], disc[v])
        if parent is None and kids > 1:
            art.add(u)

    dfs(start, None)
    return len(comp) - len(art), len(comp)


def main():
    rows = []
    for rounds in (0, 4, 8, 12, 16, 20, 24):
        sites, comp = legal_sites(walls_after(rounds))
        rows.append((rounds, sites, comp))
        print(f"density rounds {rounds:2d}: reachable open {comp:3d}, legal deadfall sites {sites:3d}, "
              f"share {sites / comp:.3f}")
    shares = [s / c for _, s, c in rows]
    checks = [
        ("more density -> fewer legal deadfall sites at the top end than at 0", rows[-1][1] < rows[0][1]),
        ("the SHARE of open ground usable for deadfalls falls with density", shares[-1] < shares[0]),
        ("break case: the loss is faster than the open ground's own loss (share drops >= 0.10)",
         shares[0] - shares[-1] >= 0.10),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; sites "
          + "/".join(str(s) for _, s, _ in rows) + "; share " + f"{shares[0]:.3f}->{shares[-1]:.3f}")


if __name__ == "__main__":
    main()
