"""New-idea loop 4 (DATABASE-DESIGN): when one value dominates a column (95% 'open'), index only the rare values
with a PARTIAL index (WHERE status != hot) and let the hot value use a scan. Composes DATABASE-DESIGN
explain-analyze (estimates vs reality), indexes-tax-every-write, and brain's refreshed-average-stats lesson.
Real SQLite (stdlib sqlite3), file databases in a temp dir, deterministic data; cost = SQLite VM instructions
(progress handler, per 100 ops); size = page_count after VACUUM.
Two databases, 20000 rows, 95% status = -1: FULL index on status vs PARTIAL index WHERE status != -1.
Predictions written before running:
 P1 a rare-key lookup costs within 2x between partial and full index, both under 1/10 of a full scan.
 P2 inserting 5000 more rows (95% hot) costs at least 20% fewer VM ops with the partial index.
 P3 the partial index database is smaller: index pages under 0.2 of the full index's.
 P4 the planner scans for the hot value under the partial index (it cannot use it), and that scan costs no
    more than the full index's index plan did (+10%).
"""
import os, sqlite3, tempfile

def build(kind, d):
    path = os.path.join(d, kind + ".db"); con = sqlite3.connect(path)
    ops = [0]; con.set_progress_handler(lambda: ops.__setitem__(0, ops[0] + 1) or 0, 100)
    con.execute("create table t(id integer primary key, status int, payload text)")
    con.executemany("insert into t values (?,?,?)", [(i, -1 if i % 20 else i % 1000, "x" * 40) for i in range(20000)])
    if kind == "full": con.execute("create index ix on t(status)")
    else: con.execute("create index ix on t(status) where status != -1")
    con.commit(); con.execute("analyze"); con.commit()
    return con, ops, path

def cost(con, ops, sql, args=()):
    ops[0] = 0; con.execute(sql, args).fetchall(); return ops[0]

def plan(con, sql, args=()):
    return " | ".join(r[-1] for r in con.execute("explain query plan " + sql, args))

d = tempfile.mkdtemp(); R = {}
for kind in ("full", "partial"):
    con, ops, path = build(kind, d)
    rare = cost(con, ops, "select payload from t where status = ? and status != -1", (20,))
    hot = cost(con, ops, "select payload from t where status = ?", (-1,))
    hot_plan = plan(con, "select payload from t where status = ?", (-1,))
    rare_plan = plan(con, "select payload from t where status = ? and status != -1", (20,))
    scan = cost(con, ops, "select payload from t not indexed where status = ?", (20,))
    ops[0] = 0
    con.executemany("insert into t(status, payload) values (?,?)", [(-1 if i % 20 else 7, "y" * 40) for i in range(5000)]); con.commit()
    ins = ops[0]
    con.execute("vacuum")
    total = con.execute("pragma page_count").fetchone()[0]
    R[kind] = dict(rare=rare, hot=hot, scan=scan, ins=ins, pages=total, hot_plan=hot_plan, rare_plan=rare_plan)
    con.close()
con = sqlite3.connect(os.path.join(d, "none.db"))
con.execute("create table t(id integer primary key, status int, payload text)")
con.executemany("insert into t values (?,?,?)", [(i, -1 if i % 20 else i % 1000, "x" * 40) for i in range(25000)]); con.commit(); con.execute("vacuum")
base_pages = con.execute("pragma page_count").fetchone()[0]
for k, r in R.items(): print(k, r)
print("no-index pages (same 25000 rows):", base_pages)
ix_full, ix_part = R["full"]["pages"] - base_pages, R["partial"]["pages"] - base_pages
p1 = R["partial"]["rare"] <= 2 * max(1, R["full"]["rare"]) and max(R["full"]["rare"], R["partial"]["rare"]) < R["full"]["scan"] / 10
p2 = R["partial"]["ins"] <= 0.8 * R["full"]["ins"]
p3 = ix_part < 0.2 * ix_full
p4 = "SCAN" in R["partial"]["hot_plan"] and R["partial"]["hot"] <= 1.1 * R["full"]["hot"]
checks = [("P1 rare lookups equally fast", p1), ("P2 inserts >= 20% cheaper", p2), ("P3 partial index < 0.2 the pages", p3), ("P4 hot value scans, no dearer", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; rare full/partial/scan {R['full']['rare']}/{R['partial']['rare']}/{R['full']['scan']}; "
      f"insert ops full/partial {R['full']['ins']}/{R['partial']['ins']}; index pages full/partial {ix_full}/{ix_part}; hot full/partial {R['full']['hot']}/{R['partial']['hot']} ({R['partial']['hot_plan']})")
