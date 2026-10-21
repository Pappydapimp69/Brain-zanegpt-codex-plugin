# Sandbox: curling end scoring. Rule: after 16 stones (8 per team) only the team with the stone closest to the button
# scores, one point per stone nearer than the opponent's nearest. If every distance rank order is equally likely
# (all C(16,8)=12870 assignments of ranks to teams), what does one end look like?
# Prediction (before run): P(team A scores >=1)=1/2 exactly, P(>=2)=7/30 (0.2333), mean points per team 8/9 (0.8889),
# P(blank)=0 because with no ties one team always has the closest stone; max score 8 occurs 1 time in 12870 per team.
from fractions import Fraction
from itertools import combinations
RANKS = range(16)
dist = {}
n = 0
ge = {k: 0 for k in range(1, 9)}
total_pts = 0
for a_ranks in combinations(RANKS, 8):
    s = set(a_ranks); n += 1
    pts = 0
    if 0 in s:
        r = 0
        while r in s: r += 1
        pts = r
    dist[pts] = dist.get(pts, 0) + 1
    total_pts += pts
    for k in range(1, pts + 1): ge[k] += 1
print("assignments:", n)
for k in range(1, 9): print(f"P(A scores >= {k}) = {Fraction(ge[k], n)} = {ge[k]/n:.4f}")
mean = Fraction(total_pts, n)
print("mean points for A per end:", mean, f"= {float(mean):.4f}")
print("A scores 0 (B has the closest stone):", dist[0], "of", n)
ok = n == 12870 and Fraction(ge[1], n) == Fraction(1, 2) and Fraction(ge[2], n) == Fraction(7, 30) and mean == Fraction(8, 9) and ge[8] == 1
print("RESULT:", "PASS" if ok else "FAIL", f"P(>=1)={Fraction(ge[1], n)}, P(>=2)={Fraction(ge[2], n)}, mean {mean}, 8-enders {ge[8]}/{n}, A scores 0 in {dist[0]}/{n}")
