"""Gap pass on ideas DATABASE-DESIGN/explain-analyze (a big estimate-vs-actual gap with no LIMIT points at
stale statistics: run ANALYZE). Real SQLite (python stdlib sqlite3), deterministic data, cost measured as
SQLite VM instructions via the progress handler (counted per 100 ops), not wall time.
Table t(id, status, payload) with 20000 rows, index on status.
  phase 1: status = id % 1000 (1000 equal keys)      -> ANALYZE
  phase 2: 95% of rows set to status = -1 ('open')  (stats now stale)
  phase 3: ANALYZE again (stats refreshed)
Estimated rows for status = ? are read from sqlite_stat1 (avg rows per key; plus sqlite_stat4 if this
build has it). Actual rows from count(*). Plan cost: default plan vs NOT INDEXED full scan.
Predictions written before running:
 P1 stale stats misestimate 'open' by more than 50x.
 P2 after re-ANALYZE the average-per-key estimate still misses 'open' by more than 10x (refresh cannot see skew)
    -- unless sqlite_stat4 exists, which I expect it does NOT in this build.
 P3 for 'open' the planner's index plan costs MORE VM ops than the forced full scan, after the refresh too.
 P4 for a rare key the index plan costs under a tenth of the full scan (same estimate, opposite reality).
"""
import sqlite3

N = 20000
con = sqlite3.connect(":memory:")
ops = [0]
con.set_progress_handler(lambda: ops.__setitem__(0, ops[0] + 1) or 0, 100)
con.execute("create table t(id integer primary key, status int, payload text)")
con.executemany("insert into t values (?,?,?)", [(i, i % 1000, "x" * 40) for i in range(N)])
con.execute("create index t_status on t(status)")
con.execute("analyze")

def est(key):
    row = con.execute("select stat from sqlite_stat1 where idx='t_status'").fetchone()
    nrow, per = (int(x) for x in row[0].split()[:2])
    return per

def cost(sql, args):
    ops[0] = 0
    n = con.execute(sql, args).fetchall()
    return ops[0], len(n)

def plan(sql, args):
    return " | ".join(r[-1] for r in con.execute("explain query plan " + sql, args))

has_stat4 = bool(con.execute("select count(*) from sqlite_master where name='sqlite_stat4'").fetchone()[0])
Q = "select payload from t where status = ?"
QF = "select payload from t not indexed where status = ?"
# phase 2: skew
con.execute("update t set status = -1 where id % 20 != 0")
open_actual = con.execute("select count(*) from t where status=-1").fetchone()[0]
e_stale = est(-1)
c_idx_stale, _ = cost(Q, (-1,)); c_full, _ = cost(QF, (-1,)); plan_stale = plan(Q, (-1,))
# phase 3: refresh
con.execute("analyze")
has_stat4 = has_stat4 or bool(con.execute("select count(*) from sqlite_master where name='sqlite_stat4'").fetchone()[0])
e_fresh = est(-1)
c_idx_fresh, _ = cost(Q, (-1,)); plan_fresh = plan(Q, (-1,))
rare_key = 20  # id % 20 == 0 rows kept their status; key 20 survives on ids 20, 1020, ...
rare_actual = con.execute("select count(*) from t where status=?", (rare_key,)).fetchone()[0]
c_rare_idx, _ = cost(Q, (rare_key,)); c_rare_full, _ = cost(QF, (rare_key,))
print(f"sqlite {sqlite3.sqlite_version}; stat4 present: {has_stat4}")
print(f"'open' actual {open_actual}; estimate stale {e_stale} (x{open_actual/e_stale:.0f}), refreshed {e_fresh} (x{open_actual/e_fresh:.0f})")
print(f"plan stale: {plan_stale}\nplan refreshed: {plan_fresh}")
print(f"'open' cost (x100 VM ops): index stale {c_idx_stale}, index refreshed {c_idx_fresh}, full scan {c_full}")
print(f"rare key actual {rare_actual}; cost index {c_rare_idx} vs full {c_rare_full}")
p1 = open_actual / e_stale > 50
p2 = (open_actual / e_fresh > 10) and not has_stat4
p3 = c_idx_stale > c_full and c_idx_fresh > c_full
p4 = c_rare_idx < c_rare_full / 10
checks = [("P1 stale misestimate > 50x", p1), ("P2 refreshed avg still > 10x off, no stat4", p2),
          ("P3 index plan costs more than full scan, before and after refresh", p3), ("P4 rare key index < 1/10 full", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; open actual {open_actual} est stale {e_stale} refreshed {e_fresh}; "
      f"cost idx stale/fresh/full {c_idx_stale}/{c_idx_fresh}/{c_full}; rare idx/full {c_rare_idx}/{c_rare_full}; stat4 {has_stat4}")
