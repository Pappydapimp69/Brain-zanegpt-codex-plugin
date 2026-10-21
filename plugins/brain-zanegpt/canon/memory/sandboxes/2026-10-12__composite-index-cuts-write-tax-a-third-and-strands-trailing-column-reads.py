"""Sandbox: one composite (a,b) index vs two single-column indexes (a),(b).
Composes ideas:DATABASE-DESIGN/write-cost, sandbox-kernel-database-design/E1
(per-index write tax in SQLite VM ops) and the SYSTEM/database composite-index
kernel (leading column bounds the scan; trailing-only is eligible-not-efficient).
Deterministic: counts SQLite VM instructions and EXPLAIN QUERY PLAN text, no time.

Claim: replacing (a),(b) with (a,b) cuts the per-INSERT index tax (ops above
the no-index baseline) by at least 40%, keeps a=? reads within 2x of the single
index, but turns b=? into a scan costing >=50% of the no-index full scan --
EXCEPT when a has few distinct values and ANALYZE has run, where SQLite's
skip-scan makes b=? cost <10% of a full scan (the scenario built to BREAK it).
"""
import sqlite3

N = 2000

def ops(con, sql, params=()):
    c = [0]
    def h():
        c[0] += 1
        return 0
    con.set_progress_handler(h, 1)
    con.execute(sql, params).fetchall()
    con.set_progress_handler(None, 0)
    return c[0]

def build(indexes, a_card, analyze):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, a INT, b INT, pad TEXT)")
    for ix in indexes:
        con.execute(ix)
    rows = [(i, (i * 7919) % a_card, (i * 104729) % 1000, "x" * 20) for i in range(N)]
    con.executemany("INSERT INTO t VALUES(?,?,?,?)", rows)
    if analyze:
        con.execute("ANALYZE")
    return con

def measure(indexes, a_card, analyze):
    con = build(indexes, a_card, analyze)
    ins = sum(ops(con, "INSERT INTO t VALUES(?,?,?,?)", (N + k, k % a_card, k % 1000, "y"))
              for k in range(100)) / 100
    sa = sum(ops(con, "SELECT id FROM t WHERE a=?", (k % a_card,)) for k in range(20)) / 20
    sb = sum(ops(con, "SELECT id FROM t WHERE b=?", (k * 37 % 1000,)) for k in range(20)) / 20
    plan_b = " | ".join(r[3] for r in con.execute("EXPLAIN QUERY PLAN SELECT id FROM t WHERE b=5"))
    return ins, sa, sb, plan_b

NONE = []
SINGLES = ["CREATE INDEX ia ON t(a)", "CREATE INDEX ib ON t(b)"]
COMPOSITE = ["CREATE INDEX iab ON t(a,b)"]

ok = True
print("sqlite", sqlite3.sqlite_version)
results = {}
for label, a_card, analyze in [("S1 high-card a (1000), no ANALYZE", 1000, False),
                               ("S2 high-card a (1000), ANALYZE", 1000, True),
                               ("S3 BREAKER low-card a (4), ANALYZE", 4, True)]:
    r = {name: measure(ix, a_card, analyze) for name, ix in
         [("none", NONE), ("singles", SINGLES), ("composite", COMPOSITE)]}
    results[label] = r
    print("\n" + label)
    for name, (ins, sa, sb, plan) in r.items():
        print(f"  {name:9s} insert={ins:6.1f} sel_a={sa:8.1f} sel_b={sb:8.1f}  plan_b: {plan}")
    base = r["none"][0]
    tax_s = r["singles"][0] - base
    tax_c = r["composite"][0] - base
    cut = 1 - tax_c / tax_s
    a_ratio = r["composite"][1] / r["singles"][1]
    b_frac = r["composite"][2] / r["none"][2]
    print(f"  index tax singles={tax_s:.1f} composite={tax_c:.1f} cut={cut:.0%}; "
          f"sel_a composite/single={a_ratio:.2f}; sel_b composite/fullscan={b_frac:.1%}")
    results[label] = (cut, a_ratio, b_frac, r["composite"][3])

c1, a1, b1, p1 = results["S1 high-card a (1000), no ANALYZE"]
c2, a2, b2, p2 = results["S2 high-card a (1000), ANALYZE"]
c3, a3, b3, p3 = results["S3 BREAKER low-card a (4), ANALYZE"]
checks = [
    ("S1 tax cut >=40%", c1 >= 0.40),
    ("S1 sel_a within 2x", a1 <= 2.0),
    ("S1 sel_b >=50% of full scan", b1 >= 0.50),
    ("S2 sel_b >=50% of full scan", b2 >= 0.50),
    ("S3 tax cut >=40%", c3 >= 0.40),
    ("S3 skip-scan: sel_b <10% of full scan", b3 < 0.10),
]
print()
for name, passed in checks:
    print(("ok   " if passed else "MISS ") + name)
    ok &= passed
summary = (f"tax cut S1 {c1:.0%} S3 {c3:.0%}; b=? on (a,b) costs {b1:.0%}/{b2:.0%} of full scan "
           f"at 1000 distinct a, {b3:.1%} at 4 distinct a after ANALYZE (skip-scan)")
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + summary)
