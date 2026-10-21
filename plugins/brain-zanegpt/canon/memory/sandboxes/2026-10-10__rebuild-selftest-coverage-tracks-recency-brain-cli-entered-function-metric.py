"""Rebuild of: Brain CLI selftest coverage tracks recency (deliberate), not importance (blast radius).
PREDICTION (written before first run): with MY OWN metrics -- coverage = function ENTERED at least once
(sys.setprofile call events, not statement fraction), recency = newest-line blame date per function
(not median), importance = number of cmd_* handlers that transitively reach it via a name-reference graph --
at today's HEAD: Spearman(covered, newness) >= +0.10; |Spearman(covered, reach)| < 0.30; old-and-high-reach
(oldest third AND reach in top third) covered-any <= 30%. Stdlib only, deterministic, no RNG."""
import ast, os, subprocess, sys, importlib.machinery, importlib.util, datetime
ROOT = "/home/user/Brain"
SRC = os.path.join(ROOT, "bin", "brain")
text = open(SRC).read()
tree = ast.parse(text)
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
# blame -> newest line date per function
out = subprocess.run(["git", "-C", ROOT, "blame", "--line-porcelain", "bin/brain"], capture_output=True, text=True).stdout
dates, cur = {}, 0
lineno = 0
for ln in out.splitlines():
    if ln.startswith("author-time "):
        lineno += 1; dates[lineno] = int(ln.split()[1])
newest = {k: max(dates.get(i, 0) for i in range(f.lineno, f.end_lineno + 1)) for k, f in funcs.items()}
# reference graph
refs = {k: {n.id for n in ast.walk(f) if isinstance(n, ast.Name) and n.id in funcs and n.id != k} for k, f in funcs.items()}
cmds = [k for k in funcs if k.startswith("cmd_")]
def reach(start):
    seen, st = set(), [start]
    while st:
        x = st.pop()
        for y in refs[x]:
            if y not in seen: seen.add(y); st.append(y)
    return seen
blast = {k: 0 for k in funcs}
for c in cmds:
    for y in reach(c) | {c}: blast[y] += 1
# coverage: functions entered while the selftest runs
entered = set()
first = {f.lineno: k for k, f in funcs.items()}
def prof(frame, event, arg):
    if event == "call" and os.path.realpath(frame.f_code.co_filename) == SRC:
        n = first.get(frame.f_code.co_firstlineno)
        if n: entered.add(n)
sys.setprofile(prof)
spec = importlib.util.spec_from_file_location("selftest_run", os.path.join(ROOT, "ci", "selftest.py"))
mod = importlib.util.module_from_spec(spec)
import io, contextlib
try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(mod)
except SystemExit:
    pass
finally:
    sys.setprofile(None)
names = sorted(funcs)
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2
        i = j + 1
    return r
def spear(a, b):
    ra, rb = rank(a), rank(b); n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** .5; vb = sum((y - mb) ** 2 for y in rb) ** .5
    return cov / (va * vb) if va and vb else 0.0
cov = [1 if funcs[n].name in entered else 0 for n in names]
new = [newest[n] for n in names]; bl = [blast[n] for n in names]
r_new, r_blast = spear(cov, new), spear(cov, bl)
t1 = sorted(new)[len(new) // 3]; b2 = sorted(bl)[2 * len(bl) // 3]
cell = [i for i, n in enumerate(names) if new[i] <= t1 and bl[i] >= b2]
cell_cov = sum(cov[i] for i in cell) / len(cell) if cell else float("nan")
print(f"functions={len(names)} entered={sum(cov)} cmds={len(cmds)}")
print(f"spearman(cov,newness)={r_new:+.3f} spearman(cov,blast)={r_blast:+.3f} old&important cell n={len(cell)} covered={cell_cov:.2f}")
ok = r_new >= 0.10 and abs(r_blast) < 0.30 and cell and cell_cov <= 0.30
print(f"RESULT: {'PASS' if ok else 'FAIL'} n={len(names)} entered={sum(cov)} r_new={r_new:+.3f} r_blast={r_blast:+.3f} cell_n={len(cell)} cell_cov={cell_cov:.2f}")
