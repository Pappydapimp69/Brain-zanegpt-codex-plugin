"""Seed STRUCTURES: static determinacy of pin-jointed 2D trusses. Maxwell's count m + r = 2j (r=3 reactions).
Check it against the exact rank of the joint-equilibrium matrix (Fractions, no floats). Cases include one that satisfies the count
but is NOT determinate (built to break the count as a test). Directions are integer vectors so everything stays exact."""
from fractions import Fraction as F
def rank_nullity(rows):
    M = [[F(x) for x in r] for r in rows]; rk = 0; ncol = len(M[0]) if M else 0
    for c in range(ncol):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        M[rk] = [x / M[rk][c] for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk, ncol - rk
def analyse(pts, members, supports):
    j, m = len(pts), len(members)
    cols = []
    for a, b in members:
        dx, dy = pts[b][0] - pts[a][0], pts[b][1] - pts[a][1]
        n = F(dx) ** 2 + F(dy) ** 2          # unit vector needs a root; use unnormalised direction (rank unaffected)
        col = [0] * (2 * j); col[2*a] += dx; col[2*a+1] += dy; col[2*b] -= dx; col[2*b+1] -= dy
        cols.append(col)
    for joint, d in supports:                  # reaction directions: 'x' or 'y'
        col = [0] * (2 * j); col[2*joint + (0 if d == 'x' else 1)] = 1; cols.append(col)
    rows = [[cols[c][r] for c in range(len(cols))] for r in range(2 * j)]
    rk, null = rank_nullity(rows)
    unk = m + len(supports)
    return dict(j=j, m=m, count=2*j - (m + len(supports)), rank=rk, nullity=null, unknowns=unk,
                mech=2*j - rk, kind=("determinate" if rk == 2*j and null == 0 else "mechanism" if rk < 2*j else "indeterminate"))
S3 = [(0, 'x'), (0, 'y'), (1, 'y')]
cases = {
 "triangle": ([(0,0),(4,0),(2,3)], [(0,1),(1,2),(0,2)], S3),
 "square no diagonal": ([(0,0),(4,0),(4,4),(0,4)], [(0,1),(1,2),(2,3),(3,0)], S3),
 "square one diagonal": ([(0,0),(4,0),(4,4),(0,4)], [(0,1),(1,2),(2,3),(3,0),(0,2)], S3),
 "square two diagonals": ([(0,0),(4,0),(4,4),(0,4)], [(0,1),(1,2),(2,3),(3,0),(0,2),(1,3)], S3),
 "braced square + dangling joint (count ok)": ([(0,0),(4,0),(4,4),(0,4),(-3,2)], [(0,1),(1,2),(2,3),(3,0),(0,2),(1,3),(0,4)], S3),
}
res = {k: analyse(*v) for k, v in cases.items()}
for k, r in res.items(): print(k, r)
ok = (res["triangle"]["kind"] == "determinate" and res["square no diagonal"]["kind"] == "mechanism"
      and res["square one diagonal"]["kind"] == "determinate" and res["square two diagonals"]["kind"] == "indeterminate"
      and res["braced square + dangling joint (count ok)"]["count"] == 0
      and res["braced square + dangling joint (count ok)"]["kind"] != "determinate")
print("RESULT: %s Maxwell count 0 and exact rank agree for triangle and one-diagonal square, count<0 / >0 match mechanism / indeterminate, but the braced square with a one-bar dangling joint has count %d yet is %s (rank %d of %d)" % (
  "PASS" if ok else "FAIL", res["braced square + dangling joint (count ok)"]["count"], res["braced square + dangling joint (count ok)"]["kind"],
  res["braced square + dangling joint (count ok)"]["rank"], 2*5))
