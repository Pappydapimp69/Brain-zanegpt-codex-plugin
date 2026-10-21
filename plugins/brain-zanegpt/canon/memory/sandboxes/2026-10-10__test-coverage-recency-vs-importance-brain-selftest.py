#!/usr/bin/env python3
"""T30 test: does test coverage track RECENCY or IMPORTANCE?  Real data: the
Brain CLI (bin/brain) and its own selftest (ci/selftest.py), pinned to one
commit so the run is reproducible.

MEASURES, fixed before the first run
  unit        every top-level function of bin/brain with >= 1 executable statement
  COVERAGE    primary: fraction of the function's statements executed when
              ci/selftest.py runs in-process under a line tracer.
              secondary: covered-any (at least one body statement ran).
  RECENCY     primary: "newness" = median git-blame commit date over the
              function's lines, in days since the oldest line in the file.
              secondary: newest-line date, oldest-line date.
  IMPORTANCE  primary: BLAST RADIUS = number of CLI commands (COMMANDS table
              entries) whose static reference graph reaches the function.
              secondary: fan-in (distinct other functions naming it);
              HARM = function itself writes/deletes/pushes (the selftest's own
              stated purpose: defects that silently destroy or hide work).
  Nothing in IMPORTANCE reads git history; nothing in RECENCY reads the call graph.

PREDICTION (written before the first run; pole A of T30 says coverage follows
recency):
  P1  Spearman(coverage, newness)      >= +0.20
  P2  |Spearman(coverage, blast radius)| < 0.15
  P3  the OLD x IMPORTANT cell (bottom third newness, top third blast radius)
      has covered-any rate <= 20%
  P4  the NEW third has covered-any rate >= 2x the OLD third
  If any of P1-P4 fails the claim is not supported; RESULT is FAIL.
Scenarios: 1) full population, 2) old x important cell (built to BREAK the claim:
if old-and-important code were covered, P3 fails), 3) permutation null on
newness (fixed seed), 4) planted-truth controls proving the statistic can tell
importance-driven coverage from recency-driven coverage, 5) alternative measures.
"""
import ast, os, random, runpy, subprocess, sys, tarfile, tempfile, io, statistics

REPO = next((c for c in (os.environ.get("BRAIN_REPO"), os.path.expanduser("~/Brain"), "/home/user/Brain")
             if c and os.path.isdir(os.path.join(c, ".git"))), None)
PIN = "9450c1b"          # Brain commit analysed (fixed, so the numbers are stable)

def git(*a, raw=False):
    out = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, check=True).stdout
    return out if raw else out.decode()

# ---------------------------------------------------------------- statistics
def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]: j += 1
        for k in range(i, j + 1): r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r

def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sa = sum((x - ma) ** 2 for x in a) ** .5; sb = sum((y - mb) ** 2 for y in b) ** .5
    return 0.0 if sa == 0 or sb == 0 else sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

def spearman(a, b): return pearson(ranks(a), ranks(b))

def partial(a, b, c):   # Spearman partial corr of a,b controlling c
    rab, rac, rbc = spearman(a, b), spearman(a, c), spearman(b, c)
    d = ((1 - rac ** 2) * (1 - rbc ** 2)) ** .5
    return 0.0 if d == 0 else (rab - rac * rbc) / d

# ---------------------------------------------------------------- load pinned tree
tmp = tempfile.TemporaryDirectory(); root = tmp.name
tarfile.open(fileobj=io.BytesIO(git("archive", PIN, raw=True))).extractall(root, filter="data")
BRAIN = os.path.join(root, "bin", "brain")
src = open(BRAIN, encoding="utf-8").read()
tree = ast.parse(src)

# ---------------------------------------------------------------- coverage by tracing selftest
target = os.path.realpath(BRAIN); executed = set(); cache = {}
def tracer(frame, event, arg):
    fn = frame.f_code.co_filename
    ok = cache.get(fn)
    if ok is None: ok = cache[fn] = (os.path.realpath(fn) == target)
    if not ok: return None
    def local(fr, ev, ar):
        if ev == "line": executed.add(fr.f_lineno)
        return local
    executed.add(frame.f_lineno)
    return local
_o, _e, _argv = sys.stdout, sys.stderr, sys.argv
sys.stdout = sys.stderr = io.StringIO(); sys.settrace(tracer); rc = 0
try:
    runpy.run_path(os.path.join(root, "ci", "selftest.py"), run_name="__main__")
except SystemExit as e:
    rc = e.code or 0
finally:
    sys.settrace(None); sys.stdout, sys.stderr, sys.argv = _o, _e, _argv
print(f"pinned commit {PIN}: selftest exit={rc}, distinct bin/brain lines executed={len(executed)}")

# ---------------------------------------------------------------- units
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
def stmts(fn):
    out = []
    body = fn.body[1:] if (fn.body and isinstance(fn.body[0], ast.Expr)
                           and isinstance(getattr(fn.body[0], "value", None), ast.Constant)
                           and isinstance(fn.body[0].value.value, str)) else fn.body
    for top in body:
        for n in ast.walk(top):
            if isinstance(n, ast.stmt): out.append((n.lineno, n.end_lineno))
    return out

# blame -> per-line commit time
blame = {}; cur = None
for ln in git("blame", "--line-porcelain", "-w", PIN, "--", "bin/brain").splitlines():
    p = ln.split(" ")
    if len(p) >= 3 and len(p[0]) == 40 and p[1].isdigit() and p[2].isdigit(): cur = int(p[2])
    elif ln.startswith("author-time "): blame[cur] = int(p[1])
t0 = min(blame.values()); DAY = 86400

# reference graph over top-level functions + top-level assigned names
glob_refs = {}
for n in tree.body:
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name): glob_refs[t.id] = n
nodes = set(funcs) | set(glob_refs)
def refs(node):
    return {x.id for x in ast.walk(node) if isinstance(x, ast.Name)} & nodes
edges = {k: refs(v) - {k} for k, v in funcs.items()}
for k, v in glob_refs.items():
    if k not in funcs: edges.setdefault(k, set()).update(refs(v) - {k})
cmds = [x for x in tree.body if isinstance(x, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "COMMANDS" for t in x.targets)][0]
entry = [refs(v) for v in cmds.value.values]          # one reference set per command
def reach(start):
    seen = set(start); st = list(start)
    while st:
        for m in edges.get(st.pop(), ()):
            if m not in seen: seen.add(m); st.append(m)
    return seen
reached = [reach(e) for e in entry]
WRITE = {"write_text", "unlink", "rmtree", "remove", "rename", "replace", "move", "copy", "copy2",
         "copytree", "write", "writelines", "symlink", "chmod", "truncate"}
def harmful(fn):
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if nm in WRITE: return 1
            if nm == "open" and len(n.args) > 1 and isinstance(n.args[1], ast.Constant) \
               and any(c in str(n.args[1].value) for c in "wax"): return 1
            if nm in ("run", "check_call", "check_output", "Popen", "call") and n.args \
               and isinstance(n.args[0], (ast.List, ast.Tuple)):
                toks = [c.value for c in n.args[0].elts if isinstance(c, ast.Constant)]
                if any(t in ("push", "commit", "reset", "rm", "merge", "checkout", "clean") for t in toks): return 1
    return 0
callers = {k: 0 for k in funcs}
for k, es in edges.items():
    if k in funcs:
        for m in es:
            if m in callers: callers[m] += 1

U = []
for name, fn in funcs.items():
    st = stmts(fn)
    if not st: continue
    cov = sum(1 for a, b in st if any(l in executed for l in range(a, b + 1)))
    ts = [blame[l] for l in range(fn.lineno, fn.end_lineno + 1) if l in blame]
    U.append(dict(name=name, n=len(st), cov=cov / len(st), any=1 if cov else 0,
                  new=statistics.median(ts) - t0, newest=max(ts) - t0, oldest=min(ts) - t0,
                  B=sum(1 for r in reached if name in r), fanin=callers[name], H=harmful(fn)))
for u in U:
    for k in ("new", "newest", "oldest"): u[k] /= DAY
N = len(U); col = lambda k: [u[k] for u in U]
print(f"units={N} functions; covered-any={sum(col('any'))}; mean line-coverage={statistics.mean(col('cov')):.3f}; "
      f"span={(max(blame.values()) - t0) / DAY:.0f} days; commands={len(entry)}")
print(f"B>=1: {sum(1 for u in U if u['B']>=1)}; B==0 (unreachable from CLI table): {sum(1 for u in U if u['B']==0)}; "
      f"harm functions={sum(col('H'))}")

# ---------------------------------------------------------------- scenario 1
rn = spearman(col("cov"), col("new")); rb = spearman(col("cov"), col("B"))
rb_ctrl = partial(col("cov"), col("B"), col("new")); rn_ctrl = partial(col("cov"), col("new"), col("B"))
rsz = spearman(col("cov"), col("n"))
print(f"S1 full population: rho(cov,newness)={rn:+.3f}  rho(cov,blast)={rb:+.3f}  rho(newness,blast)={spearman(col('new'), col('B')):+.3f}")
print(f"   partial: cov~newness|blast={rn_ctrl:+.3f}  cov~blast|newness={rb_ctrl:+.3f}  (size confound rho(cov,size)={rsz:+.3f})")

# ---------------------------------------------------------------- scenario 2 (breaker)
def tert(key):
    s = sorted(U, key=lambda u: u[key]); k = N // 3
    return s[:k], s[-k:], {id(u) for u in s[:k]}, {id(u) for u in s[-k:]}
old, new, oldids, newids = tert("new")
_, _, _, impids = tert("B")
rate = lambda g: (sum(u["any"] for u in g) / len(g)) if g else float("nan")
mean_c = lambda g: (sum(u["cov"] for u in g) / len(g)) if g else float("nan")
oi = [u for u in U if id(u) in oldids and id(u) in impids]
ni = [u for u in U if id(u) in newids and id(u) in impids]
print(f"S2 thirds by newness: OLD covered-any={rate(old):.2f} (n={len(old)}, mean cov {mean_c(old):.2f})  "
      f"NEW covered-any={rate(new):.2f} (n={len(new)}, mean cov {mean_c(new):.2f})")
print(f"   OLD x IMPORTANT cell n={len(oi)} covered-any={rate(oi):.2f} mean cov={mean_c(oi):.2f}; "
      f"NEW x IMPORTANT cell n={len(ni)} covered-any={rate(ni):.2f} mean cov={mean_c(ni):.2f}")
imp, unimp = tert("B")[1], tert("B")[0]
print(f"   thirds by blast radius: IMPORTANT covered-any={rate(imp):.2f}  UNIMPORTANT covered-any={rate(unimp):.2f}")

# ---------------------------------------------------------------- scenario 3 (permutation null)
rng = random.Random(14); nw = col("new"); cv = col("cov"); ge = 0; null = []
for _ in range(2000):
    s = nw[:]; rng.shuffle(s); r = spearman(cv, s); null.append(r)
    if r >= rn: ge += 1
print(f"S3 permutation null (2000 shuffles, seed 14): null mean={statistics.mean(null):+.3f} sd={statistics.pstdev(null):.3f}; "
      f"p(rho_null >= observed {rn:+.3f})={(ge + 1) / 2001:.4f}")

# ---------------------------------------------------------------- scenario 4 (planted truth)
def plant(kind):
    r = random.Random(7); sc = []
    a, b = ranks(col("new")), ranks(col("B"))
    for i in range(N):
        s = (a[i] if kind == "recency" else b[i]) / N + r.uniform(-.15, .15); sc.append(s)
    cut = sorted(sc)[N // 2]
    return [1.0 if s > cut else 0.0 for s in sc]
for kind in ("recency", "importance"):
    pc = plant(kind)
    print(f"S4 planted {kind}-driven coverage: rho(new)={spearman(pc, col('new')):+.3f} rho(blast)={spearman(pc, col('B')):+.3f} "
          f"partial new|B={partial(pc, col('new'), col('B')):+.3f} partial B|new={partial(pc, col('B'), col('new')):+.3f}")
pr_ok = (partial(plant("recency"), col("new"), col("B")) > partial(plant("recency"), col("B"), col("new")) + .2 and
         partial(plant("importance"), col("B"), col("new")) > partial(plant("importance"), col("new"), col("B")) + .2)
print(f"   statistic separates the two planted worlds: {pr_ok}")

# ---------------------------------------------------------------- scenario 5 (alt measures)
print("S5 alternatives, rho with line-coverage: "
      f"newest-line={spearman(cv, col('newest')):+.3f} oldest-line={spearman(cv, col('oldest')):+.3f} "
      f"fan-in={spearman(cv, col('fanin')):+.3f} harm={spearman(cv, col('H')):+.3f}")
print(f"   covered-any rate: harm functions={rate([u for u in U if u['H']]):.2f} (n={sum(col('H'))}), "
      f"non-harm={rate([u for u in U if not u['H']]):.2f}")
hold = [u for u in U if u["H"] and id(u) in oldids]
print(f"   OLD third AND harm: n={len(hold)} covered-any={rate(hold):.2f}; NEW third AND harm: "
      f"n={len([u for u in U if u['H'] and id(u) in newids])} covered-any="
      f"{rate([u for u in U if u['H'] and id(u) in newids]):.2f}")
by_month = {}
for u in U: by_month.setdefault(int(u["new"] // 30), []).append(u)
print("   by 30-day band of newness (band: n, covered-any, mean cov): " +
      "; ".join(f"{k}: {len(v)}, {rate(v):.2f}, {mean_c(v):.2f}" for k, v in sorted(by_month.items())))


# ---------------------------------------------------------------- scenario 6 (POST-HOC, added after seeing S1-S5; does not affect RESULT)
tsrc = open(os.path.join(root, "ci", "selftest.py"), encoding="utf-8").read()
for u in U: u["direct"] = 1 if ("brain." + u["name"]) in tsrc else 0
inc = [u for u in U if u["any"] and not u["direct"]]
dr = [u for u in U if u["direct"]]
print(f"S6 post-hoc: directly named by selftest={len(dr)}, covered only incidentally (ran, never named)={len(inc)}, uncovered={sum(1 for u in U if not u['any'])}")
print(f"   rho(direct,newness)={spearman(col('direct'), col('new')):+.3f} rho(direct,blast)={spearman(col('direct'), col('B')):+.3f}; "
      f"mean newness direct={statistics.mean([u['new'] for u in dr]):.1f}d vs incidental={statistics.mean([u['new'] for u in inc]):.1f}d; "
      f"mean blast direct={statistics.mean([u['B'] for u in dr]):.1f} vs incidental={statistics.mean([u['B'] for u in inc]):.1f} vs all={statistics.mean(col('B')):.1f}")

ro = rate(old); rnw = rate(new)
p1, p2, p3, p4 = rn >= .20, abs(rb) < .15, (oi and rate(oi) <= .20), (rnw >= 2 * ro if ro > 0 else rnw > 0)
print(f"checks: P1(rho_new>=.20)={p1} P2(|rho_blast|<.15)={p2} P3(old x important <=.20)={bool(p3)} P4(new>=2x old)={p4} planted_ok={pr_ok}")
ok = p1 and p2 and p3 and p4 and pr_ok
print(f"RESULT: {'PASS' if ok else 'FAIL'} rho(cov,newness)={rn:+.3f} rho(cov,blast)={rb:+.3f} old-x-important covered-any="
      f"{rate(oi):.2f} new/old covered-any={rnw:.2f}/{ro:.2f}")
tmp.cleanup()
