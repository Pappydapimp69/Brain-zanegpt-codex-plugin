# Kernel: ideas:EMPATHY/bias/it-is-the-GAP-between-in-group-and-out-group-empathy-that-predicts-harm-not-a-lack-of-empathy
# Prediction (before run): if harm = a*(ingroup - outgroup) with a=0.5, then OLS of harm on [ingroup, outgroup, trait] recovers
# +0.5 and -0.5 (opposite signs, trait ~0); raising ALL empathy by +1 changes mean harm by 0.00; raising only out-group by +1 cuts mean
# harm by 0.50; BREAK: if harm = -0.5*outgroup alone, the general +1 raise cuts harm by 0.50, so "general empathy need not reduce harm" is false there.
import itertools
def ols(X, y):
    n, p = len(X), len(X[0])
    A = [[sum(X[k][i] * X[k][j] for k in range(n)) for j in range(p)] + [sum(X[k][i] * y[k] for k in range(n))] for i in range(p)]
    for i in range(p):
        piv = max(range(i, p), key=lambda r: abs(A[r][i])); A[i], A[piv] = A[piv], A[i]
        for r in range(p):
            if r != i:
                f = A[r][i] / A[i][i]; A[r] = [x - f * z for x, z in zip(A[r], A[i])]
    return [A[i][p] / A[i][i] for i in range(p)]
people = [(t, t + di, t + do) for t, di, do in itertools.product(range(5), (-1, 0, 1, 2), (-2, -1, 0, 1))]  # trait, in, out
def fit(harm):
    X = [[1.0, i, o, t] for t, i, o in people]; y = [harm(t, i, o) for t, i, o in people]
    return [round(b, 3) for b in ols(X, y)]
gap = lambda t, i, o: 0.5 * (i - o)
outonly = lambda t, i, o: -0.5 * o
b1 = fit(gap); b2 = fit(outonly)
def mean(f, dt=0, di=0, do=0): return sum(f(t + dt, i + di, o + do) for t, i, o in people) / len(people)
d_all = round(mean(gap, 1, 1, 1) - mean(gap), 3); d_out = round(mean(gap, 0, 0, 1) - mean(gap), 3)
d_all_b = round(mean(outonly, 1, 1, 1) - mean(outonly), 3)
print("gap model coefficients [const, in, out, trait]", b1, "| out-only model", b2)
print("general +1 raise: gap model", d_all, "out-only model", d_all_b, "| out-group-only +1 raise (gap model)", d_out)
ok = (b1[1] == 0.5 and b1[2] == -0.5 and b1[3] == 0.0 and d_all == 0.0 and d_out == -0.5 and d_all_b == -0.5)
print("RESULT:", "PASS" if ok else "FAIL",
      f"gap model: in {b1[1]:+}, out {b1[2]:+}, trait {b1[3]:+}; general +1 raise changes harm by {d_all}, out-group-only by {d_out}; BREAK out-only model: general raise changes harm by {d_all_b}")
