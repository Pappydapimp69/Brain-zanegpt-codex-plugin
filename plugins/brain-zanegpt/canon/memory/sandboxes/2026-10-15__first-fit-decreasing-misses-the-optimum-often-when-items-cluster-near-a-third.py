"""Train kernel (apply): PACKING/bin-packing (first-fit decreasing beats first
fit on average, matched the optimum on 458 of 462 tiny multisets; 'expect it to
match the optimum almost always'). Pushed past the kernel's tiny integer
instances: realistic list sizes, and Johnson's classic adversarial mix.
Deterministic: seeded random.Random lists; exact optimum by a small
branch-and-bound where feasible, else the lower bound ceil(sum/C).
Capacity C = 100.
PREDICTION (written before running): on 2,000 lists of 20 items uniform 1..60,
FFD hits the lower bound (so is optimal) on >= 95%; on items uniform 20..50
(many 'thirds') it hits the lower bound clearly less often (< 80%); the Johnson
mix (6 x 51, 6 x 27, 6 x 26, 12 x 23) packs into 9 bins optimally but FFD uses
11 (ratio 11/9), so 'almost always optimal' depends on the size distribution.
"""
import math, random, sys
print("python", sys.version.split()[0])
C = 100
def ffd(items):
    bins = []
    for x in sorted(items, reverse=True):
        for i, b in enumerate(bins):
            if b + x <= C: bins[i] += x; break
        else: bins.append(x)
    return len(bins)
def opt(items, limit):
    items = sorted(items, reverse=True); best = [limit]
    def go(i, bins):
        if len(bins) >= best[0]: return
        if i == len(items): best[0] = len(bins); return
        seen = set()
        for k in range(len(bins)):
            if bins[k] + items[i] <= C and bins[k] not in seen:
                seen.add(bins[k]); bins[k] += items[i]; go(i + 1, bins); bins[k] -= items[i]
        bins.append(items[i]); go(i + 1, bins); bins.pop()
    go(0, []); return best[0]
J = [51] * 6 + [27] * 6 + [26] * 6 + [23] * 12
fj = ffd(J)
witness = [[51, 26, 23]] * 6 + [[27, 27, 23, 23]] * 3        # a 9-bin packing; 9 = ceil(900/100) so it is optimal
assert sorted(x for b in witness for x in b) == sorted(J) and all(sum(b) <= C for b in witness)
oj = len(witness)
print(f"Johnson mix: FFD {fj} bins, optimum {oj} (lower bound {math.ceil(sum(J)/C)})")
rng = random.Random(42)
def study(lo, hi, n=20, reps=2000):
    at_lb = at_opt = checked = 0
    for _ in range(reps):
        it = [rng.randint(lo, hi) for _ in range(n)]
        f = ffd(it); lb = math.ceil(sum(it) / C)
        at_lb += f == lb
        if f > lb and checked < 40 and n <= 12:
            checked += 1; at_opt += opt(it, f) == f
    return at_lb / reps, checked, at_opt
u = study(1, 60); t = study(20, 50); u12 = study(20, 50, n=12, reps=500)
print(f"uniform 1..60: FFD at lower bound {u[0]:.3f}; ")
print(f"12 items 20..50: FFD at lower bound {u12[0]:.3f}; of {u12[1]} above LB checked by exact search, FFD optimal in {u12[2]}")
print(f"uniform 20..50: FFD at lower bound {t[0]:.3f}; ")
c = [u[0] >= 0.95, t[0] < 0.80, fj == 11 and oj == 9]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/3; Johnson FFD {fj} vs OPT {oj}; uniform 1-60 at LB {u[0]:.3f} ; 20-50 at LB {t[0]:.3f} ; 12 items 20-50 at LB {u12[0]:.3f}, above-LB cases optimal {u12[2]}/{u12[1]}")
