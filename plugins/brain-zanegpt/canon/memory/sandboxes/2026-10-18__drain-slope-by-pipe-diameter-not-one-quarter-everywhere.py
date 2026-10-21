"""Plumbing drain slope (International Plumbing Code 704.1 minimum slope): pipes up to 2.5 in
diameter 1/4 in per ft; 3 to 6 in 1/8 in per ft; 8 in and up 1/16 in per ft.
Question: with a fixed fall budget (height between the fixture outlet and the sewer connection),
does a 'quarter inch per foot everywhere' rule reject runs that the per-diameter code minimum
accepts?  Pure arithmetic, deterministic.  A run is feasible when its minimum fall <= budget."""
def code_slope(d):
    return 0.25 if d <= 2.5 else (0.125 if d <= 6 else 0.0625)
UNIFORM = 0.25
# (name, diameter in, run ft, fall budget in) - budgets are the height available on the job
runs = [
 ("lavatory 1.5in trap arm", 1.5, 5, 2.0),
 ("kitchen 2in branch", 2, 20, 6.0),
 ("bath group 3in branch", 3, 24, 4.0),
 ("3in main slab", 3, 40, 6.0),
 ("4in building drain", 4, 60, 8.0),
 ("6in house sewer", 6, 100, 14.0),
 ("8in sewer", 8, 120, 9.0),
]
bad_uniform = bad_code = 0
for name, d, run, budget in runs:
    need_u, need_c = UNIFORM*run, code_slope(d)*run
    fu, fc = need_u <= budget, need_c <= budget
    bad_uniform += not fu; bad_code += not fc
    print(f"{name:34s} d={d} run={run} budget={budget}: uniform needs {need_u:.2f} ({'ok' if fu else 'FAIL'}), code needs {need_c:.2f} ({'ok' if fc else 'FAIL'})")
# BREAK: for small pipes (<=2.5 in) both rules must agree; any disagreement there would break the claim
small = [r for r in runs if r[1] <= 2.5]
agree_small = all((UNIFORM*r[2] <= r[3]) == (code_slope(r[1])*r[2] <= r[3]) for r in small)
ok = bad_code == 0 and bad_uniform >= 3 and agree_small
print(f"RESULT: {'PASS' if ok else 'FAIL'} uniform quarter-inch rule rejects {bad_uniform} of {len(runs)} runs the per-diameter minimum accepts ({bad_code} rejected); small pipes agree={agree_small}")
