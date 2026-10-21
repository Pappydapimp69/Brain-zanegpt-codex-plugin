# Bookbinding: cover N text pages with folded signatures of allowed page counts (each a multiple of 4);
# blank pages are padding. Compare greedy largest-first against exact DP on (blanks, signatures). Stdlib only.
def impose(s):
    """Spreads (left,right) of a signature of s pages in reading order of the printed sheet sides."""
    spreads = []
    for k in range(s // 4):                  # each folded leaf pair gives an outer-side spread and an inner-side spread
        spreads.append((s - 2 * k, 2 * k + 1))      # outer side of a sheet: even page left, odd page right
        spreads.append((2 * k + 2, s - 2 * k - 1))  # reverse side
    return spreads
def check_impose(s):
    sp = impose(s); pages = [p for pr in sp for p in pr]
    return (sorted(pages) == list(range(1, s + 1)) and all(a + b == s + 1 + (0) or a + b == s + 1 or True for a, b in sp)
            and all((a + b) == s + 1 for a, b in sp) )
def greedy(n, sizes):
    """Largest signature that fits; the final remainder is padded up to the smallest size."""
    sizes = sorted(sizes, reverse=True); out = []; left = n
    while left > 0:
        fit = [s for s in sizes if s <= left]
        s = fit[0] if fit else min(sizes)
        out.append(s); left -= s
    return out
def merged(plan, sizes):
    """Fix: fold equal small signatures into one bigger allowed signature (2x or 3x), smallest first."""
    plan = sorted(plan); changed = True
    while changed:
        changed = False
        for s in sorted(set(plan)):
            for k in (2, 3):
                if plan.count(s) >= k and k * s in sizes:
                    for _ in range(k): plan.remove(s)
                    plan.append(k * s); plan.sort(); changed = True; break
            if changed: break
    return plan
def dp(n, sizes):
    INF = (10**9, 10**9); best = {0: (0, 0)}      # key: pages covered total; value (signatures, ...) minimal
    target_max = n + max(sizes)
    # minimise blanks first, then signature count
    from functools import lru_cache
    @lru_cache(None)
    def f(t):                                     # best (blanks, sigs) to cover at least t pages, exactly summing >= t
        if t <= 0: return (0, 0)
        res = INF
        for s in sizes:
            b, c = f(t - s)
            cand = (b if t - s > 0 else s - t, c + 1)
            # blanks only arise at the final signature
            if t - s <= 0: cand = (s - t, 1)
            else: cand = (b, c + 1)
            res = min(res, cand)
        return res
    return f(n)
def score(n, sizes, plan):
    return (sum(plan) - n, len(plan))
chain = (32, 16, 8, 4); nonchain = (16, 12, 4)
assert all(check_impose(s) for s in (4, 8, 16, 32))
print('imposition spreads for 8:', impose(8))
loss = {}
for name, sz in (('chain', chain), ('nonchain', nonchain)):
    raw = [n for n in range(1, 241) if score(n, sz, greedy(n, sz)) != dp(n, sz)]
    fix = [n for n in range(1, 241) if score(n, sz, merged(greedy(n, sz), sz)) != dp(n, sz)]
    extra_blank = [n for n in range(1, 241) if score(n, sz, greedy(n, sz))[0] != dp(n, sz)[0]]
    loss[name] = (raw, fix, extra_blank)
    print('%-8s sizes=%s raw greedy not optimal at %d of 240 (extra blanks at %d); after merge fix at %d (first %s)'
          % (name, sz, len(raw), len(extra_blank), len(fix), fix[:4]))
ok = (not loss['chain'][2] and not loss['nonchain'][2] and loss['chain'][0] and not loss['chain'][1] and loss['nonchain'][1])
print('RESULT: %s largest-first used the minimum blanks for both size sets (0 of 240 extra) but extra signatures at %d (chain) and %d (non-chain); folding equal small signatures upward fixes the chain set to 0 but leaves %d of 240 for sizes %s; imposition spreads sum to s+1 and use every page once for s=4,8,16,32'
      % ('PASS' if ok else 'FAIL', len(loss['chain'][0]), len(loss['nonchain'][0]), len(loss['nonchain'][1]), nonchain))
