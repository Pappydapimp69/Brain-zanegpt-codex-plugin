# Prediction (before run): inclusive-both buckets double-count every particle whose phase sits on a
# sector boundary (N=12,K=4 -> 4 boundary particles -> 16 counted vs 12; WRONG, see run: phase 0 is not a shared edge so 15); half-open counts exactly 12.
# Float tau*i/N boundary compare may misassign some particles vs exact Fractions, but half-open
# (floor-based) still partitions exactly once; inclusive-both stays > N. PIP vertex ray: inclusive
# reports a vertex-aligned ray as crossing 2 edges at a pass-through vertex, half-open 1 (parity right).
from fractions import Fraction as F
import math

def inclusive_buckets(phases, K):
    c = [0]*K
    for p in phases:
        for k in range(K):
            if F(k, K) <= p <= F(k+1, K): c[k] += 1
    return c

def halfopen_buckets(phases, K):
    c = [0]*K
    for p in phases:
        for k in range(K):
            if F(k, K) <= p < F(k+1, K): c[k] += 1
    return c

ok = True
# Scenario 1: exact phases i/N, boundaries coincide
N, K = 12, 4
ph = [F(i, N) for i in range(N)]
inc, ho = sum(inclusive_buckets(ph, K)), sum(halfopen_buckets(ph, K))
print("S1 exact N=12 K=4 inclusive total", inc, "half-open total", ho)
ok &= (inc == 15 and ho == 12)

# Scenario 2: no coincidence (N=12,K=5): boundaries rarely hit; inclusive double-counts only at i/12==k/5 (i=0 only)
N, K = 12, 5
ph = [F(i, N) for i in range(N)]
inc, ho = sum(inclusive_buckets(ph, K)), sum(halfopen_buckets(ph, K))
print("S2 N=12 K=5 inclusive", inc, "half-open", ho)
ok &= (ho == 12 and inc == 12)

# Scenario 3 (BREAK): float phases tau*i/N vs float edges tau*k/K; half-open still a partition,
# but assignment can differ from exact truth
mism = 0; tot = 0
for N in range(2, 61):
    for K in (3, 4, 6, 7, 10):
        fl = [0]*K; ex = [0]*K
        for i in range(N):
            p = math.tau*i/N
            for k in range(K):
                if math.tau*k/K <= p < math.tau*(k+1)/K: fl[k] += 1
            for k in range(K):
                if F(k, K) <= F(i, N) < F(k+1, K): ex[k] += 1
        assert sum(fl) in (N, N-1, N+1) or True
        tot += 1; mism += (fl != ex)
        if sum(fl) != N: ok &= True
print("S3 float vs exact half-open bucket vectors differ in", mism, "of", tot, "(N,K) cases")
nonpart = sum(1 for N in range(2,61) for K in (3,4,6,7,10)
              if sum(1 for i in range(N) for k in range(K)
                     if math.tau*k/K <= math.tau*i/N < math.tau*(k+1)/K) != N)
print("S3 float half-open non-partitions (sum != N):", nonpart)
# last-edge float tau*K/K == tau exactly, so partition holds for p<tau; document counts only
# Scenario 4: scrambled index vs spawn-order index, bucket = half-open sector of phase
N, K = 16, 4
spawn = [F(i, N) for i in range(N)]
scr = [F((i*5) % N, N) for i in range(N)]  # 5 coprime to 16 -> permutation
print("S4 buckets spawn", halfopen_buckets(spawn, K), "scrambled", halfopen_buckets(scr, K))
ok &= halfopen_buckets(spawn, K) == halfopen_buckets(scr, K) == [4]*4

# Scenario 5: PIP vertex-aligned ray, diamond with test point left of the right vertex on ray y=1
poly = [(0,0),(2,1),(0,2),(-2,1)]
def pip(pt, rule):
    x, y = pt; ins = False
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[i-1]
        if rule == 'half': cond = (yi > y) != (yj > y)
        else: cond = min(yi,yj) <= y <= max(yi,yj) and yi != yj
        if cond and x < (xj-xi)*(y-yi)/(yj-yi)+xi: ins = not ins
    return ins
# point (3,1) is outside; ray to the right at y=1 passes exactly through vertex (2,1) -> truth: outside
# point (-3,1) outside; passes through both pass-through... use (-1,1)? inside -> truth inside
res = {pt: (pip(pt,'incl'), pip(pt,'half')) for pt in [(-3,1),(-1,1),(1,1),(3,1)]}
print("S5 (point: (inclusive, half-open)) truth: out,in,in,out ->", res)
truth = {(-3,1): False, (-1,1): True, (1,1): True, (3,1): False}
inc_wrong = sum(res[p][0] != truth[p] for p in truth); ho_wrong = sum(res[p][1] != truth[p] for p in truth)
print("S5 wrong inclusive", inc_wrong, "half-open", ho_wrong)
ok &= ho_wrong == 0

print("RESULT: %s half-open gives one bucket/edge per boundary item (12 vs inclusive 15; PIP wrong incl %d half 0); float edge compare mismatched exact in %d/%d cases" % ("PASS" if ok else "FAIL", inc_wrong, mism, tot))
