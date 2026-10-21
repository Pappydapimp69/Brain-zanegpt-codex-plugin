"""ACTIVITY-SELECTION kernel: to fit the most non-overlapping jobs, sort by earliest finish
(never lost in 401,929 instances). Boundary: real schedules weigh jobs (pay, priority). Does
any greedy order stay optimal when the goal is total WEIGHT? Exhaustive optimum by bitmask
over 6-job instances; instances from a deterministic LCG (start 0-11, length 1-6, weight
1-9); 20,000 instances. Greedies: earliest finish, highest weight, highest weight/length.
Also re-check the unweighted claim on the same instances.
PREDICTION (written before running): unweighted earliest-finish is optimal on 100%;
for total weight, earliest-finish is optimal on under 70% of instances and no greedy order
exceeds 90%; weighted DP (sort by finish, binary search) matches the bitmask optimum 100%."""
import bisect
class LCG:
    def __init__(self, s): self.s = s
    def r(self, m): self.s = (6364136223846793005 * self.s + 1442695040888963407) % 2 ** 64; return (self.s >> 33) % m
def overlap(a, b): return a[0] < b[1] and b[0] < a[1]
def best(jobs, key):
    best_v = 0
    n = len(jobs)
    for mask in range(1 << n):
        sel = [jobs[i] for i in range(n) if mask >> i & 1]
        if any(overlap(sel[i], sel[j]) for i in range(len(sel)) for j in range(i + 1, len(sel))): continue
        best_v = max(best_v, sum(key(j) for j in sel))
    return best_v
def greedy(jobs, order, key):
    chosen = []
    for j in sorted(jobs, key=order):
        if all(not overlap(j, c) for c in chosen): chosen.append(j)
    return sum(key(j) for j in chosen)
def dp(jobs):
    js = sorted(jobs, key=lambda j: j[1]); ends = [j[1] for j in js]; f = [0] * (len(js) + 1)
    for i, j in enumerate(js):
        k = bisect.bisect_right(ends, j[0], 0, i)
        f[i + 1] = max(f[i], f[k] + j[2])
    return f[-1]
g = LCG(11); T = 20000
cnt = {"count EF": 0, "weight EF": 0, "weight heaviest": 0, "weight density": 0, "weight DP": 0}
for _ in range(T):
    jobs = []
    for _ in range(6):
        s = g.r(12); L = 1 + g.r(6); jobs.append((s, s + L, 1 + g.r(9)))
    one = lambda j: 1; w = lambda j: j[2]
    cnt["count EF"] += greedy(jobs, lambda j: j[1], one) == best(jobs, one)
    opt = best(jobs, w)
    cnt["weight EF"] += greedy(jobs, lambda j: j[1], w) == opt
    cnt["weight heaviest"] += greedy(jobs, lambda j: -j[2], w) == opt
    cnt["weight density"] += greedy(jobs, lambda j: -j[2] / (j[1] - j[0]), w) == opt
    cnt["weight DP"] += dp(jobs) == opt
share = {k: v / T for k, v in cnt.items()}
print({k: f"{v:.1%}" for k, v in share.items()})
ok = (share["count EF"] == 1 and share["weight EF"] < 0.7 and max(share["weight heaviest"], share["weight density"], share["weight EF"]) <= 0.9
      and share["weight DP"] == 1)
print(f"RESULT: {'PASS' if ok else 'FAIL'} unweighted earliest-finish optimal {share['count EF']:.1%}; weighted: earliest-finish "
      f"{share['weight EF']:.1%}, heaviest-first {share['weight heaviest']:.1%}, weight/length {share['weight density']:.1%}, DP {share['weight DP']:.1%}")
