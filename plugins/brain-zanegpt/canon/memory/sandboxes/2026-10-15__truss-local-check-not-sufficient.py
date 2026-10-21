"""STRUCTURES/trusses kernel: Maxwell's count is necessary, not sufficient; confirm by the
rank of the joint-equilibrium matrix, 'or by checking that every joint is held by at least
two non-parallel members'. Is that local check sufficient? Candidate counterexample: a
doubly braced square (redundant +1) joined to a singly braced square by TWO PARALLEL
horizontal links (a parallelogram: the right square can sway), so totals balance (count 0)
and every joint has >= 2 non-parallel members, yet it should be a mechanism.
Supports: pin at joint 0 (2 reactions), roller (vertical) at joint 1. Exact rank with
Fractions (Gaussian elimination). Controls: the kernel's triangle (determinate), and the
same two squares joined by one horizontal + one diagonal link (count +1? recomputed).
PREDICTION (written before running): the parallel-link truss has Maxwell count 0 and passes
the two-non-parallel-members check at every joint, but its matrix rank is 2j - 1 (one
mechanism mode); replacing one parallel link with a diagonal link makes it rigid. (Iteration 1 refuted that
control: both links met at joint 4, so the right square pivots. Prediction for iteration 2,
written before its run: three non-concurrent links with count 0 are rigid, rank 2j.)"""
from fractions import Fraction as F
def rank(M):
    M = [r[:] for r in M]; rk = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c] / M[rk][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk
def analyse(J, bars, supports):
    n = len(J); rows = 2 * n
    cols = []
    for a, b in bars:
        dx, dy = F(J[b][0] - J[a][0]), F(J[b][1] - J[a][1])
        col = [F(0)] * rows
        col[2 * a], col[2 * a + 1], col[2 * b], col[2 * b + 1] = dx, dy, -dx, -dy   # direction (length scale irrelevant to rank)
        cols.append(col)
    for j, d in supports:
        col = [F(0)] * rows; col[2 * j + d] = F(1); cols.append(col)
    M = [[cols[k][r] for k in range(len(cols))] for r in range(rows)]
    count = len(bars) + len(supports) - 2 * n
    def local_ok(j):
        dirs = [(J[b][0] - J[a][0], J[b][1] - J[a][1]) for a, b in bars if j in (a, b)]
        dirs += [(1, 0) if d == 0 else (0, 1) for jj, d in supports if jj == j]
        return any(u[0] * v[1] - u[1] * v[0] != 0 for i, u in enumerate(dirs) for v in dirs[i + 1:])
    return count, all(local_ok(j) for j in range(n)), rank(M), rows
# joints: left square 0(0,0) 1(1,0) 2(1,1) 3(0,1); right square 4(2,0) 5(3,0) 6(3,1) 7(2,1)
J = [(0, 0), (1, 0), (1, 1), (0, 1), (2, 0), (3, 0), (3, 1), (2, 1)]
left = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)]            # two diagonals
right = [(4, 5), (5, 6), (6, 7), (7, 4), (4, 6)]                    # one diagonal
parallel = left + right + [(1, 4), (2, 7)]                          # two parallel horizontal links
diag = left + right + [(1, 4), (2, 4)]                              # iteration 1 control: also pivots about joint 4
# iteration 2 control: move the redundant bar to a third, non-concurrent link between the bodies
three = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)] + right + [(1, 4), (2, 7), (2, 4)]
sup = [(0, 0), (0, 1), (1, 1)]
tri = analyse([(0, 0), (1, 0), (0, 1)], [(0, 1), (1, 2), (2, 0)], sup)
P = analyse(J, parallel, sup); D = analyse(J, diag, sup); T3 = analyse(J, three, sup)
for name, (c, loc, rk, rows) in (("triangle", tri), ("parallel links", P), ("diagonal link", D), ("three links", T3)):
    print(f"{name:15s} Maxwell count {c:+d}, every joint 2 non-parallel members: {loc}, rank {rk}/{rows} -> "
          f"{'rigid' if rk == rows else 'MECHANISM (' + str(rows - rk) + ' mode)'}")
ok = tri[2] == tri[3] and P[0] == 0 and P[1] and P[2] == P[3] - 1 and T3[0] == 0 and T3[2] == T3[3]
print(f"RESULT: {'PASS' if ok else 'FAIL'} parallel-link truss: count {P[0]:+d}, local check {P[1]}, rank {P[2]}/{P[3]} (mechanism); "
      f"one-joint link (iteration-1 control) also a mechanism, rank {D[2]}/{D[3]}; three non-concurrent links count {T3[0]:+d}, rank {T3[2]}/{T3[3]}")
