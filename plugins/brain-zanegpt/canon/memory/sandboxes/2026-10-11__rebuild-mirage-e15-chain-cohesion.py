"""Rebuild of mirage E15 (own fixture). Claims: under chain cohesion (with the
group if within R of ANY member, connected component), (A) a connected member
can be up to (N-1)*R from the leader; (B) losses are positional: losing the
member next to the leader can cut off everyone behind it; (C) a perceived-but-
nonexistent member is a valid link that holds the group together.
Model: points on a plane, exhaustive over a lattice of chain shapes; R = 1.
"""
import itertools
import math

R = 1.0


def component(points, root=0):
    seen, st = {root}, [root]
    while st:
        u = st.pop()
        for v, p in enumerate(points):
            if v not in seen and math.dist(points[u], p) <= R + 1e-9:
                seen.add(v)
                st.append(v)
    return seen


def max_reach(n):
    # all placements on a 0.5 lattice in a strip, exhaustive for small n
    grid = [(x * 0.5, y * 0.5) for x in range(0, 2 * n + 1) for y in range(0, 2)]
    best = 0.0
    for pts in itertools.product(grid, repeat=n - 1):
        points = [(0.0, 0.0)] + list(pts)
        comp = component(points)
        best = max(best, max(math.dist(points[0], points[i]) for i in comp))
    return best


def main():
    reach = {n: max_reach(n) for n in (2, 3, 4)}
    for n, r in reach.items():
        print(f"N={n}: furthest connected member {r:.2f} (claim (N-1)R = {(n - 1) * R:.2f})")
    line = [(0, 0), (1, 0), (2, 0), (3, 0)]
    cut = component([p for i, p in enumerate(line) if i != 1])
    # others (excluding the removed member) no longer connected to the leader
    tail_lost = 2 - (len(cut) - 1)
    end_cut = component(line[:3])
    with_phantom = component([(0, 0), (1, 0), (2, 0)])
    without = component([(0, 0), (2, 0)])
    print(f"lose the member next to the leader: {tail_lost} of 3 others cut off; lose the end: "
          f"{2 - (len(end_cut) - 1)} others cut off")
    print(f"phantom at (1,0): group size {len(with_phantom)}; without it: {len(without)}")
    checks = [
        ("(A) furthest connected member equals (N-1)R for N=2..4",
         all(abs(reach[n] - (n - 1) * R) < 1e-9 for n in reach)),
        ("(B) losing the member next to the leader cuts off everyone behind it", tail_lost == 2),
        ("(B) losing the end member cuts off no one else", 2 - (len(end_cut) - 1) == 0),
        ("(C) a phantom link holds a member who is 2R away", len(with_phantom) == 3 and len(without) == 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; reach "
          + ", ".join(f"N{n}={r:.2f}" for n, r in reach.items()) + f"; near-loss cuts {tail_lost}; phantom holds")


if __name__ == "__main__":
    main()
