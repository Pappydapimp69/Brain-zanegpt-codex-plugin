"""Bisection with untestable (skipped) commits.

Claim under test: with commits untestable i.i.d. at rate s (git bisect skip),
bisection stops on a candidate range (lo, hi] whose ambiguity rate (size > 1)
is 2s - s^2 and whose mean size is 1 + 2s/(1-s), independent of n and of which
testable commit the skip policy picks; the extra tests over s=0 stay below 1.
Scenario built to break it: a random-testable skip policy (if the final set
depended on the path, sets would differ). Scope scenario: clustered skips
(broken-build runs of 10) at the same s, where the iid formula should fail.

Stdlib only, fixed seeds, deterministic.
"""
import random


def bisect(n, t, skipped, policy, rng):
    """commits 0..n; 0 good, n bad, first bad = t. returns (lo, hi, tests)."""
    lo, hi, tests = 0, n, 0
    while True:
        cand = [c for c in range(lo + 1, hi) if c not in skipped]
        if not cand:
            return lo, hi, tests
        if policy == "nearest-mid":
            mid = (lo + hi) / 2
            m = min(cand, key=lambda c: (abs(c - mid), c))
        elif policy == "random":
            m = rng.choice(cand)
        else:  # "lowest-above-mid": first testable at or after mid, else last
            mid = (lo + hi) // 2
            above = [c for c in cand if c >= mid]
            m = above[0] if above else cand[-1]
        tests += 1
        if m >= t:
            hi = m
        else:
            lo = m


def iid_skips(n, s, rng):
    return {c for c in range(1, n) if rng.random() < s}


def clustered_skips(n, s, k, rng):
    out = set()
    p_start = s / k  # approx same total fraction
    c = 1
    while c < n:
        if rng.random() < p_start:
            out.update(range(c, min(c + k, n)))
            c += k
        else:
            c += 1
    return out


def run(n, s, trials, seed, policies, maker):
    rng = random.Random(seed)
    stats = {p: {"amb": 0, "size": 0, "tests": 0} for p in policies}
    same_sets = 0
    frac = 0.0
    for _ in range(trials):
        skipped = maker(n, s, rng)
        frac += len(skipped) / (n - 1)
        t = rng.randint(1, n)
        sets = []
        for p in policies:
            prng = random.Random(rng.random())
            lo, hi, tests = bisect(n, t, skipped, p, prng)
            assert lo < t <= hi, "true first-bad lost"
            st = stats[p]
            st["amb"] += (hi - lo) > 1
            st["size"] += hi - lo
            st["tests"] += tests
            sets.append((lo, hi))
        same_sets += len(set(sets)) == 1
    res = {p: {k: v / trials for k, v in st.items()} for p, st in stats.items()}
    return res, same_sets / trials, frac / trials


def main():
    ok = True
    pol = ["nearest-mid", "random", "lowest-above-mid"]
    T = 3000

    base, _, _ = run(1000, 0.0, T, 1, ["nearest-mid"], iid_skips)
    base_tests = base["nearest-mid"]["tests"]
    print(f"S0 s=0 n=1000: tests={base_tests:.2f} amb={base['nearest-mid']['amb']:.3f}")
    worst = max(bisect(1000, t, set(), "nearest-mid", None)[2] for t in range(1, 1001))
    print(f"  worst-case tests over every t = {worst} (ceil(log2 1000) = 10)")
    ok &= worst == 10

    print("S1 iid skips, n=1000, three policies")
    for s, seed in ((0.05, 11), (0.10, 12), (0.20, 13)):
        res, same, frac = run(1000, s, T, seed, pol, iid_skips)
        pa, ps = 2 * s - s * s, 1 + 2 * s / (1 - s)
        r = res["nearest-mid"]
        print(f"  s={s:.2f} amb={r['amb']:.4f} (pred {pa:.4f}) size={r['size']:.3f} "
              f"(pred {ps:.3f}) tests={r['tests']:.2f} (+{r['tests']-base_tests:.2f}) "
              f"random-tests={res['random']['tests']:.2f} same-set={same:.4f}")
        ok &= abs(r["amb"] - pa) <= 0.02 and abs(r["size"] - ps) <= 0.05
        ok &= same == 1.0
        if s == 0.10:
            ok &= (r["tests"] - base_tests) < 1.0

    print("S2 iid s=0.10 across n (n-independence)")
    for n, seed in ((64, 21), (5000, 22)):
        res, same, _ = run(n, 0.10, 2000 if n == 5000 else T, seed, ["nearest-mid"], iid_skips)
        r = res["nearest-mid"]
        print(f"  n={n} amb={r['amb']:.4f} size={r['size']:.3f} tests={r['tests']:.2f}")
        ok &= abs(r["amb"] - 0.19) <= 0.025

    print("S3 (scope) clustered skips, runs of 10, s~0.10, n=1000")
    res, same, frac = run(1000, 0.10, T, 31, pol, lambda n, s, r: clustered_skips(n, s, 10, r))
    r = res["nearest-mid"]
    print(f"  skip-frac={frac:.3f} amb={r['amb']:.4f} (iid formula {2*frac-frac*frac:.4f}) "
          f"size={r['size']:.3f} (iid formula {1+2*frac/(1-frac):.3f}) tests={r['tests']:.2f} "
          f"same-set={same:.4f}")
    clustered_differs = r["amb"] < 0.15 and r["size"] > 1.6
    ok &= clustered_differs and same == 1.0

    print("S4 position of t inside 2-commit ranges, iid s=0.20 (skipped cell keeps its prior)")
    rng = random.Random(41)
    pos = [0, 0]
    for _ in range(T):
        sk = iid_skips(1000, 0.20, rng)
        t = rng.randint(2, 999)
        lo, hi, _ = bisect(1000, t, sk, "nearest-mid", None)
        if hi - lo == 2:
            pos[t - lo - 1] += 1
    share = pos[0] / sum(pos)
    print(f"  ranges of size 2: {sum(pos)}, t at first slot {share:.3f} (prior 0.5)")
    ok &= abs(share - 0.5) <= 0.06

    summary = (f"iid skip ambiguity tracks 2s-s^2 and size 1+2s/(1-s) for all 3 policies "
               f"(sets identical); clustered s~0.1 amb={r['amb']:.3f} size={r['size']:.3f}")
    print(("RESULT: PASS " if ok else "RESULT: FAIL ") + summary)


if __name__ == "__main__":
    main()
