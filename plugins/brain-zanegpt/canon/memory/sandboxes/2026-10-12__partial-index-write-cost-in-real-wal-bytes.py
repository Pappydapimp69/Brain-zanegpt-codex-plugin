"""Deeper follow-up to brain's partial-index lesson (its write-cost prediction missed because SQLite VM
instructions do not count B-tree page writes). Real SQLite 3.45 in WAL mode: the bytes appended to the WAL
by an insert batch are the real write cost (page images written). Deterministic data.
Setup: 20000 rows, 95% status = -1, page_size 4096, autocheckpoint off; then insert batches of 5000 rows
(95% hot) in one transaction, and 5000 single-row transactions; measure WAL growth per variant:
  none (no index), full index on status, partial index WHERE status != -1.
Predictions written before running:
 P1 one big transaction: full-index WAL growth exceeds the partial's by >= 25%.
 P2 the partial index's WAL growth is within 15% of no index at all.
 P3 5000 single-row commits: full-index writes >= 1.5x partial (every commit rewrites the index leaf it touches).
"""
import os, sqlite3, tempfile

def setup(kind, d):
    path = os.path.join(d, f"{kind}.db")
    con = sqlite3.connect(path, isolation_level=None)
    con.execute("pragma page_size=4096"); con.execute("pragma journal_mode=wal"); con.execute("pragma wal_autocheckpoint=0")
    con.execute("create table t(id integer primary key, status int, payload text)")
    con.execute("begin")
    con.executemany("insert into t values (?,?,?)", [(i, -1 if i % 20 else i % 1000, "x" * 40) for i in range(20000)])
    if kind == "full": con.execute("create index ix on t(status)")
    if kind == "partial": con.execute("create index ix on t(status) where status != -1")
    con.execute("commit"); con.execute("pragma wal_checkpoint(TRUNCATE)")
    return con, path + "-wal"

def wal(p): return os.path.getsize(p) if os.path.exists(p) else 0

d = tempfile.mkdtemp(); R = {}
for kind in ("none", "full", "partial"):
    con, w = setup(kind, d)
    b0 = wal(w)
    con.execute("begin")
    con.executemany("insert into t(status, payload) values (?,?)", [(-1 if i % 20 else 7 + i % 50, "y" * 40) for i in range(5000)])
    con.execute("commit"); big = wal(w) - b0
    con.execute("pragma wal_checkpoint(TRUNCATE)"); b1 = wal(w)
    for i in range(5000):
        con.execute("insert into t(status, payload) values (?,?)", (-1 if i % 20 else 7 + i % 50, "z" * 40))
    small = wal(w) - b1
    R[kind] = (big, small); con.close()
    print(f"{kind:7s}: WAL bytes one txn {big:>9d}   5000 single commits {small:>10d}")
p1 = R["full"][0] >= 1.25 * R["partial"][0]
p2 = R["partial"][0] <= 1.15 * R["none"][0]
p3 = R["full"][1] >= 1.5 * R["partial"][1]
checks = [("P1 full >= 1.25x partial in one txn", p1), ("P2 partial within 15% of no index", p2), ("P3 single commits full >= 1.5x partial", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; one txn none/full/partial {R['none'][0]}/{R['full'][0]}/{R['partial'][0]}; "
      f"single commits none/full/partial {R['none'][1]}/{R['full'][1]}/{R['partial'][1]}")
