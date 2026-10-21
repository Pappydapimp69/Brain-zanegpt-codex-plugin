"""Sandbox (train kernel): REGRET/intensity -- regret scales with how easily the
better outcome can be imagined (near misses hurt more) -- applied to seven
E22/E31's spatial rescue search for a missing member.
Exact, no RNG. Ring of 24 sectors, person at sector 0, heard bearing offset is a
discretised normal (sigma). A skilled search covers the H sectors nearest the
heard bearing. For every FAILED search, the miss distance is how many sectors
the person lay beyond the searched block. A NEAR MISS is distance 1 (the next
sector over). Uses E31's tuned settings per depth:
  d0 sigma 1.50 h4; d1 1.50 h2; d2 2.25 h2; d3 3.25 h2.
"""
import math

S = 24
TUNED = [(1.50, 4), (1.50, 2), (2.25, 2), (3.25, 2)]


def offset_probs(sigma):
    def cdf(x):
        return 0.5 * (1 + math.erf(x / (sigma * math.sqrt(2))))
    raw = {k: cdf(k + 0.5) - cdf(k - 0.5) for k in range(-12, 12)}
    t = sum(raw.values())
    return {k: v / t for k, v in raw.items()}


def sdist(a, b):
    d = abs(a - b) % S
    return min(d, S - d)


def miss_profile(sigma, h):
    fail = near = 0.0
    for off, w in offset_probs(sigma).items():
        order = sorted(range(S), key=lambda s: (sdist(s, off), s))
        block = set(order[:h])
        if 0 in block:
            continue
        dist = min(sdist(0, s) for s in block)
        fail += w
        near += w * (dist == 1)
    return fail, near / fail if fail else 0.0


def main():
    rows = []
    for d, (sg, h) in enumerate(TUNED):
        fail, share = miss_profile(sg, h)
        rows.append((d, fail, share))
        print(f"depth {d}: sigma {sg} hours {h}: fail {fail:.3f}, near-miss share of failures {share:.3f}, "
              f"near misses per search {fail * share:.3f}")
    shares = [r[2] for r in rows]
    checks = [
        (f"shallow (d0) failures are mostly near misses, share >= 0.50 (got {shares[0]:.3f})", shares[0] >= 0.50),
        (f"deep (d3) failures are mostly clear misses, share <= 0.35 (got {shares[3]:.3f})", shares[3] <= 0.35),
        ("near-miss share falls monotonically with depth", all(a > b for a, b in zip(shares, shares[1:]))),
        ("break case: near misses per search (not share) also fall with depth",
         rows[0][1] * shares[0] > rows[3][1] * shares[3]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; near-miss share "
          + "/".join(f"{s:.3f}" for s in shares) + "; per search " + "/".join(f"{r[1]*r[2]:.3f}" for r in rows))


if __name__ == "__main__":
    main()
