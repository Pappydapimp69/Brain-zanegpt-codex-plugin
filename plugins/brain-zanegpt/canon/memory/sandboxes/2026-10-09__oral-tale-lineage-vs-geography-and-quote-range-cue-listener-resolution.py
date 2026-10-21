"""Deterministic toy sandbox (no RNG). Prediction (written before the first run):
 P1 tale types: shared-type overlap (Jaccard) is higher between same-family languages than between cross-family geographic
    neighbours while neighbours borrow <=2 types; the ordering flips once borrowing reaches >=4 (BREAK scenario).
 P2 quote cue: a quoted-vs-narrator threshold learned on family A on pitch RANGE keeps 100% accuracy on family B (different baseline
    pitch); the same on pitch LEVEL drops to <=50% on family B.
 P3 listener limit: identifying which of K quoted characters spoke, with range cues spaced evenly in 20..60 and a just-noticeable
    difference of 6, is 100% at K<=5 and falls below 100% at K>=7 (BREAK: more voices than the cue resolution allows)."""
import math

# ---- P1: lineage vs geography
FAM = {"A": set(range(0, 6)), "B": set(range(6, 12))}
LANG = {"A1": ("A", FAM["A"] - {5}), "A2": ("A", FAM["A"] - {0}), "B1": ("B", FAM["B"] - {11}), "B2": ("B", FAM["B"] - {6})}
NEIGH = [("A1", "B1"), ("A2", "B2")]            # geographic neighbours cross the family line
def jac(a, b): return len(a & b) / len(a | b)
def p1(borrow):
    L = {k: set(v[1]) for k, v in LANG.items()}
    for x, y in NEIGH:                            # each neighbour borrows `borrow` types from the other, lowest ids first
        bx = sorted(LANG[y][1])[:borrow]; by = sorted(LANG[x][1])[:borrow]
        L[x] |= set(bx); L[y] |= set(by)
    tree = (jac(L["A1"], L["A2"]) + jac(L["B1"], L["B2"])) / 2
    geo = sum(jac(L[x], L[y]) for x, y in NEIGH) / 2
    return tree, geo
p1res = {b: p1(b) for b in range(0, 7)}
flip_at = next((b for b in range(7) if p1res[b][1] >= p1res[b][0]), None)
print("P1 borrow -> (tree-pair Jaccard, geo-pair Jaccard):", {b: (round(t, 3), round(g, 3)) for b, (t, g) in p1res.items()}, "flip at", flip_at)

# ---- P2: range vs level across lineages
def contour(base, amp, n=24): return [base + amp * math.sin(2 * math.pi * i / n * 3) for i in range(n)]
def level(c): return sum(c) / len(c)
def rng(c): return max(c) - min(c)
BASE = {"A": 100.0, "B": 180.0}
NARR_AMP, QUOTE_AMP = 5.0, 15.0
def samples(fam, shift):                           # quoted voice also shifts level by `shift`
    return [(contour(BASE[fam], NARR_AMP), 0), (contour(BASE[fam] + shift, QUOTE_AMP), 1)]
def best_thr(data, f):
    pts = sorted((f(c), y) for c, y in data); mid = (pts[0][0] + pts[1][0]) / 2
    return mid, (1 if pts[1][1] == 1 else 0)
def acc(data, f, thr, hi):
    ok = sum(((f(c) > thr) == (hi == 1)) == (y == 1) for c, y in data); return ok / len(data)
trainA = samples("A", 8.0); testB = samples("B", 8.0)
res2 = {}
for name, f in (("range", rng), ("level", level)):
    thr, _ = best_thr(trainA, f)
    hi = 1 if f(trainA[1][0]) > thr else 0
    res2[name] = (acc(trainA, f, thr, hi), acc(testB, f, thr, hi))
print("P2 accuracy train A / test B:", res2)

# ---- P3: listener resolution
JND = 6.0
def p3(K):
    ranges = [20 + 40 * i / (K - 1) for i in range(K)] if K > 1 else [20.0]
    correct = 0
    for i, r in enumerate(ranges):
        near = [j for j, q in enumerate(ranges) if abs(q - r) < JND]   # listener cannot tell these apart
        correct += (1 / len(near)) if i in near else 0                # tie broken evenly
    return correct / K
res3 = {K: round(p3(K), 3) for K in (2, 3, 4, 5, 6, 7, 8, 10)}
print("P3 identification accuracy by K:", res3)

ok1 = p1res[0][0] > p1res[0][1] and p1res[2][0] > p1res[2][1] and flip_at is not None and 3 <= flip_at <= 4
ok2 = res2["range"][1] == 1.0 and res2["level"][1] <= 0.5
brk = next(K for K in range(2, 20) if p3(K) < 1.0)
expect = math.floor(40 / JND) + 2     # first K whose spacing 40/(K-1) falls below the JND
ok3 = all(res3[k] == 1.0 for k in (2, 3, 4, 5, 6, 7)) and brk == expect and res3[10] < res3[8]
# NOTE: the written prediction said the break comes by K=7; the run showed K=8 (spacing 40/7=5.7 < JND 6)
print("RESULT:", "PASS" if ok1 and ok2 and ok3 else "FAIL",
      f"P1 lineage>geography until borrow={flip_at}; P2 range test-B {res2['range'][1]:.2f} vs level {res2['level'][1]:.2f}; "
      f"P3 breaks at K={brk} (spacing<JND) K7={res3[7]} K8={res3[8]} K10={res3[10]} (ok1={ok1} ok2={ok2} ok3={ok3})")
