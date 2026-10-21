"""Sandbox: nominal gear count vs distinct usable ratios for bicycle drivetrains. Deterministic, stdlib only.
Cassettes below are ILLUSTRATIVE tooth counts (not a specific product); ratio = chainring teeth / sprocket teeth.
Cross-chain rule (assumption, parameterised): big ring excludes the CROSS biggest sprockets; small ring excludes the CROSS smallest.
Distinct = greedy merge of sorted ratios whose step from the last kept ratio is below TOL (assumed just-noticeable step)."""
CASS11 = [11, 12, 13, 14, 16, 18, 20, 22, 25, 28, 32]
CASS1X = [10, 12, 14, 16, 18, 21, 24, 28, 33, 39, 45, 52]
def combos(rings, cass, cross):
    out = []
    for ri, r in enumerate(sorted(rings)):
        for ci, c in enumerate(cass):
            if len(rings) > 1 and ri == len(rings) - 1 and ci >= len(cass) - cross: continue
            if len(rings) > 1 and ri == 0 and ci < cross: continue
            out.append(r / c)
    return sorted(out)
def distinct(rs, tol):
    kept = []
    for x in rs:
        if not kept or x / kept[-1] - 1 >= tol: kept.append(x)
    return kept
def report(name, rings, cass, cross, tol):
    nominal = len(rings) * len(cass); usable = combos(rings, cass, cross); d = distinct(usable, tol)
    rng = usable[-1] / usable[0]
    return nominal, len(usable), len(d), rng
for tol in (0.03, 0.05, 0.08):
    print("tol", tol)
    A = report("2x11", (34, 50), CASS11, 3, tol); B = report("1x12", (40,), CASS1X, 0, tol)
    print("  2x11 nominal/usable/distinct/range", A[0], A[1], A[2], round(A[3], 2))
    print("  1x12 nominal/usable/distinct/range", B[0], B[1], B[2], round(B[3], 2))
A = report("2x11", (34, 50), CASS11, 3, 0.05); B = report("1x12", (40,), CASS1X, 0, 0.05)
# break: cross=0 (no exclusion) and tol=0 -> distinct should equal usable only if no ratio collisions
C = report("2x11", (34, 50), CASS11, 0, 0.0)
print("break tol=0 cross=0: nominal/usable/distinct", C[0], C[1], C[2])
ok = A[2] < A[0] and A[1] < A[0] and B[2] <= B[0] and B[3] > A[3] * 0.9 and C[2] <= C[0]
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" 2x11 nominal {A[0]} -> usable {A[1]} -> distinct {A[2]} at 5% (range {A[3]:.2f}x); 1x12 nominal {B[0]} distinct {B[2]} range {B[3]:.2f}x")
