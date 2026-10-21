"""Prediction (before run): model hypertrophy gain per session as a saturating response g(v) = K*(1-exp(-v/k)) of the sets v done
in that session (concave, so splitting weekly volume helps), weekly gain = f * g(V/f). With K=1, k=10 sets:
 A) LINEAR world (k=1e9): volume-equated 2x vs 1x gap = 0.00 exactly (frequency alone does nothing).
 B) SATURATING world, volume equated at V=10: gap(2 vs 1) = 0.787-0.632 = +0.155; gap(3 vs 2) = 0.850-0.787 = +0.063 (smaller, so '3 beats 2' is
    the hard one to detect, matching the kernel's open question).
 C) CONFOUNDED studies: the 2x groups also did 1.5x the volume (V=6 vs V=9 / compare at 10 and 15): the apparent 2x-vs-1x gap is more than
    2x the equated gap (I predict >= 0.35 vs 0.155).
 D) BREAK: a meta-regression that includes volume as a covariate recovers about the equated gap (within 0.03) while the binary-frequency
    regression overstates it. Study grid: V in {6,8,10,12,15}, f in {1,2}, high-frequency groups' volume multiplied by m in {1.0, 1.25, 1.5}.
Deterministic grid, no RNG, stdlib only; K, k are assumed constants (the model is not a fit to the 2016 meta-analysis)."""
import math
def week(f, V, k):
    return f * (1 - math.exp(-(V / f) / k))
def gap(f_hi, f_lo, Vhi, Vlo, k): return week(f_hi, Vhi, k) - week(f_lo, Vlo, k)
a = gap(2, 1, 10, 10, 1e9)
b21, b32 = gap(2, 1, 10, 10, 10), gap(3, 2, 10, 10, 10)
c = gap(2, 1, 15, 10, 10)
print("A linear equated gap %.4f | B saturating equated 2v1 %.3f 3v2 %.3f | C confounded (hi group 1.5x volume) %.3f" % (a, b21, b32, c))
# D: study grid, binary-frequency regression vs regression with log-volume as covariate
studies = []
for V in (6, 8, 10, 12, 15):
    for m in (1.0, 1.25, 1.5):
        lo = (1, V, week(1, V, 10)); hi = (2, V * m, week(2, V * m, 10))
        studies += [lo, hi]
def ols(X, y):
    n = len(X[0]); XtX = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]; Xty = [sum(r[i] * yy for r, yy in zip(X, y)) for i in range(n)]
    A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(A[r][i])); A[i], A[p] = A[p], A[i]
        A[i] = [v / A[i][i] for v in A[i]]
        for r in range(n):
            if r != i: A[r] = [vr - A[r][i] * vi for vr, vi in zip(A[r], A[i])]
    return [A[i][n] for i in range(n)]
y = [s[2] for s in studies]
b_bin = ols([[1, 1 if s[0] == 2 else 0] for s in studies], y)[1]
b_adj = ols([[1, 1 if s[0] == 2 else 0, math.log(s[1])] for s in studies], y)[1]
print("binary-frequency coefficient %.3f | volume-adjusted frequency coefficient %.3f | equated truth at V=10 %.3f" % (b_bin, b_adj, b21))
# equated-only studies (m=1)
eq = [s for s in studies if True]
eq_pairs = [(week(2, V, 10) - week(1, V, 10)) for V in (6, 8, 10, 12, 15)]
mean_eq = sum(eq_pairs) / len(eq_pairs)
print("mean equated gap over the V grid %.3f" % mean_eq)
ok = abs(a) < 1e-6 and abs(b21 - 0.155) < 0.005 and b32 < b21 / 2 and c > 0.35 and c > 2 * b21 and b_bin > 1.5 * mean_eq and abs(b_adj - mean_eq) < abs(b_bin - mean_eq)
print("RESULT: %s linear equated gap %.4f; saturating equated 2v1 %.3f, 3v2 %.3f; confounded %.3f; binary coefficient %.3f vs volume-adjusted %.3f vs equated mean %.3f" %
      ("PASS" if ok else "FAIL", a, b21, b32, c, b_bin, b_adj, mean_eq))
