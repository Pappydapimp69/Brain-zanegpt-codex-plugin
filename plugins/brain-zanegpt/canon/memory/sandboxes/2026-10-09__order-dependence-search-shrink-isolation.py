import itertools
# Deterministic model: a suite of tests sharing a mutable "db" dict.
def t_create(db):  db["rows"] = db.get("rows", 0) + 1; return True
def t_empty(db):   return db.get("rows", 0) == 0          # assumes clean db
def t_count1(db):  db["rows"] = db.get("rows", 0) + 1; return db["rows"] == 1  # assumes clean
def t_pure(db):    return True
def t_leak(db):    db["log"] = db.get("log", 0) + 1; return db["log"] < 4      # soak-style: fails after 3 prior runs
def t_logclean(db): return db.get("log", 0) == 0                      # assumes no leaked log
TESTS = {"logclean": t_logclean, "create": t_create, "empty": t_empty, "count1": t_count1, "pure": t_pure, "leak": t_leak}

def run(order, iso):
    db = {}; fails = []
    for n in order:
        if iso == "rebuild": db = {}
        ok = TESTS[n](db)
        if not ok: fails.append(n)
        if iso == "cleanup":  # incomplete cleanup: forgets 'log'
            db.pop("rows", None)
    return fails

def fails_any(order, iso): return bool(run(order, iso))
names = list(TESTS)
fixed = ["logclean", "empty", "count1", "pure", "create", "leak"]
# S1 fixed declared order, shared state
s1 = run(fixed, "shared")
# S2 exhaustive search of all orders (deterministic stand-in for generation) + greedy shrink
bad = [o for o in itertools.permutations(names) if fails_any(o, "shared")]
def shrink(o):
    o = list(o)
    changed = True
    while changed:
        changed = False
        for i in range(len(o)):
            c = o[:i] + o[i+1:]
            if c and fails_any(c, "shared"): o = c; changed = True; break
    return o
mins = {tuple(shrink(o)) for o in bad}
minlen = min(len(m) for m in mins)
# S3 rebuild isolation: every order passes
s3 = sum(fails_any(o, "rebuild") for o in itertools.permutations(names))
# S4 BREAK: cleanup-after-each is incomplete (misses 'log'): still order dependent
s4 = sum(fails_any(o, "cleanup") for o in itertools.permutations(names))
# S5 soak: leak only fails when 4 runs of leak accumulate; short suites never see it
leak_fail_by_len = {k: fails_any(["leak"]*k, "shared") for k in range(1, 6)}
print("S1 fixed order failures:", s1)
print("S2 failing orders:", len(bad), "of", len(list(itertools.permutations(names))), "minimal shrunk cases:", sorted(mins))
print("S3 rebuild failing orders:", s3)
print("S4 incomplete-cleanup failing orders:", s4)
print("S5 leak detected by suite length:", leak_fail_by_len)
ok = (s1 == [] and len(bad) > 0 and minlen == 2 and s3 == 0 and s4 > 0
      and not leak_fail_by_len[3] and leak_fail_by_len[4])
print("RESULT: %s fixed-order suite hides order-dependence (S1 clean), search finds %d bad orders shrunk to %d-test cases, rebuild isolation 0 failures, partial cleanup still %d bad orders, leak surfaces only at 4 runs" % ("PASS" if ok else "FAIL", len(bad), minlen, s4))
