"""Prediction (before run): placing k increases among n stitches (positions 0..n-1) with the midpoint rule
pos_i = floor((2i+1)*n/(2k)) gives segment lengths (edge run, gaps, edge run) whose spread max-min is <=1 for EVERY (n,k) with 1<=k<=n//2, n in 8..60;
the naive rule 'every floor(n/k) stitches, remainder at the end' has spread >=2 in at least 30% of those cases and always puts the whole
remainder in the last run; the midpoint rule is mirror-symmetric (reversed position set equals position set) in all cases where n*? is arranged evenly -
I predict symmetry holds in >=90% of cases but NOT all (built to break: the residue cases where (2i+1)*n/(2k) lands on a half-integer). Also when k>n//2 adjacent increases appear
(gap 0), so the rule must be limited to k<=n/2. Stdlib, deterministic."""
def mid(n, k): return [((2 * i + 1) * n) // (2 * k) for i in range(k)]
def naive(n, k):
    s = n // (k + 1) if False else n // k
    return [min(n - 1, s * (i + 1) - 1) for i in range(k)]
def runs(pos, n):
    # lengths of knit runs between increases: before first, between, after last (counting stitches not including the increase stitch)
    edges = [-1] + list(pos) + [n]
    return [edges[j + 1] - edges[j] - 1 for j in range(len(edges) - 1)]
def spread(pos, n):
    r = runs(pos, n)
    inner = r[1:-1]
    return (max(inner) - min(inner)) if inner else 0, r
def sym(pos, n): return sorted(n - 1 - p for p in pos) == sorted(pos)
cases = [(n, k) for n in range(8, 61) for k in range(1, n // 2 + 1)]
mid_bad = [(n, k) for n, k in cases if spread(mid(n, k), n)[0] > 1 or len(set(mid(n, k))) != k]
nv = [(n, k) for n, k in cases if spread(naive(n, k), n)[0] >= 2]
nv_last = [(n, k) for n, k in cases if k > 1 and runs(naive(n, k), n)[-1] > runs(naive(n, k), n)[1]]
sy = [(n, k) for n, k in cases if not sym(mid(n, k), n)]
# edge balance: first and last run differ at most 1 for midpoint?
edge = [(n, k) for n, k in cases if abs(runs(mid(n, k), n)[0] - runs(mid(n, k), n)[-1]) > 1]
# break: k > n//2
adj = sum(1 for n in range(8, 61) for k in range(n // 2 + 1, n) if min(runs(mid(n, k), n)[1:-1] or [1]) == 0 and True)
tot_over = sum(1 for n in range(8, 61) for k in range(n // 2 + 1, n))
dup = sum(1 for n in range(8, 61) for k in range(n // 2 + 1, n) if len(set(mid(n, k))) != k)
print("cases", len(cases), "mid spread>1 or duplicate:", len(mid_bad), "naive spread>=2:", len(nv), f"({len(nv)/len(cases):.2f})", "naive remainder piles up at end:", len(nv_last))
print("midpoint asymmetric:", len(sy), f"({len(sy)/len(cases):.3f})", "edge runs differ >1:", len(edge))
print("k>n//2 cases:", tot_over, "with adjacent increases (gap 0):", adj, "duplicate positions:", dup)
# ITERATION 2 (added after run 1; P5/P6 written before run 2): run 1 showed P2 failed because inner-gap spread hides the naive rule's flaw (remainder in the last run) and P3 failed (36% of midpoint layouts asymmetric).
# P5: naive layout has total-run spread (edges included) >=2 in >=30% of cases. P6: mirroring the first half of the midpoint positions gives a symmetric layout in 100% of cases with inner spread <=1 in >=95% of them.
def symmid(n, k):
    h = k // 2
    left = mid(n, k)[:h]
    right = [n - 1 - p for p in left][::-1]
    center = [(n - 1) // 2] if k % 2 else []
    return left + center + right
def allspread(pos, n):
    r = runs(pos, n); return max(r) - min(r)
nv_all = [(n, k) for n, k in cases if allspread(naive(n, k), n) >= 2]
sm_sym = [(n, k) for n, k in cases if sym(symmid(n, k), n) and len(set(symmid(n, k))) == k]
sm_ok = [(n, k) for n, k in sm_sym if spread(symmid(n, k), n)[0] <= 1]
print("naive total-run spread>=2:", len(nv_all), f"({len(nv_all)/len(cases):.2f})", "| mirrored midpoint symmetric+distinct:", len(sm_sym), "of", len(cases), "with inner spread<=1:", len(sm_ok))
p5 = len(nv_all) / len(cases) >= .30
p6 = len(sm_sym) == len(cases) and len(sm_ok) / len(cases) >= .95
# ITERATION 3 (P7 written before run 3): the 236 mirrored-layout failures are exactly the parity cases k odd and n even (a lone centre increase has no centre stitch).
fails = {(n, k) for n, k in cases} - set(sm_sym)
par = {(n, k) for n, k in cases if k % 2 == 1 and n % 2 == 0}
print("mirror failures", len(fails), "parity cases (k odd, n even)", len(par), "equal:", fails == par)
p7 = fails == par
p1 = len(mid_bad) == 0
p2 = len(nv) / len(cases) >= .30
p3 = 1 - len(sy) / len(cases) >= .90 and len(sy) > 0
p4 = adj > 0
print("P1", p1, "P2", p2, "P3", p3, "P4", p4, "P5", p5, "P6", p6, "P7", p7)
print("RESULT:", "PASS" if all([p1, p2, p3, p4, p5, p6, p7]) else "FAIL", f"{sum([p1,p2,p3,p4,p5,p6,p7])}/7 predictions held; midpoint spread<=1 in {len(cases)-len(mid_bad)}/{len(cases)}, naive spread>=2 in {len(nv)}, asymmetric midpoint {len(sy)}, edge-run mismatch {len(edge)}, adjacent increases when k>n/2: {adj}/{tot_over}; naive total-run spread>=2 {len(nv_all)}; mirrored symmetric {len(sm_sym)}, inner<=1 {len(sm_ok)}; mirror failures == parity cases {p7} ({len(fails)})")
